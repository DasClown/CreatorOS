"""
CreatorOS - Content Factory
Bilder-Upload, Wasserzeichen, ZIP-Download
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import zipfile
from utils import check_auth, render_sidebar, init_session_state, inject_custom_css

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Content Factory - CreatorOS",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS
inject_custom_css()

# =============================================================================
# AUTHENTICATION
# =============================================================================
init_session_state()
user = check_auth()

# =============================================================================
# IMAGE PROCESSING FUNCTIONS
# =============================================================================

def remove_metadata(image):
    """Entfernt EXIF-Metadaten und korrigiert Rotation"""
    image = ImageOps.exif_transpose(image)
    data = list(image.getdata())
    new_image = Image.new(image.mode, image.size)
    new_image.putdata(data)
    return new_image

def add_watermark(image, text, opacity, padding, is_pro):
    """Fügt Wasserzeichen hinzu"""
    # Free-User: Erzwinge CreatorOS Branding
    if not is_pro:
        text = "Created with CreatorOS"
    
    base_image = image.convert("RGBA")
    overlay = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Font laden
    font_size = int(image.height * 0.05)
    font = None
    font_paths = [
        "arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except:
            continue
    
    if font is None:
        font = ImageFont.load_default()
    
    text_color = (150, 150, 150, opacity)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Gekachelt (Tiled)
    y_step = text_height + padding
    x_step = text_width + padding
    
    for y in range(0, base_image.height + y_step, y_step):
        for x in range(0, base_image.width + x_step, x_step):
            draw.text((x, y), text, fill=text_color, font=font)
    
    final_image = Image.alpha_composite(base_image, overlay)
    return final_image.convert("RGB")

def format_bytes(size):
    """Formatiert Bytes in lesbare Größe"""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.2f} MB"

# =============================================================================
# SIDEBAR WITH SETTINGS
# =============================================================================

user_email, is_pro, is_admin = render_sidebar()

st.sidebar.divider()
st.sidebar.subheader("🎨 Wasserzeichen")

# Free-User: Deaktivierte Inputs
if not is_pro and not is_admin:
    st.sidebar.text_input(
        "Text",
        value="Created with CreatorOS",
        disabled=True,
        help="🔒 PRO Feature"
    )
    st.sidebar.warning("🔒 Custom Text nur im PRO Plan")
else:
    watermark_text = st.sidebar.text_input(
        "Text",
        value=st.session_state["watermark_text"],
        key="watermark_text"
    )

opacity = st.sidebar.slider(
    "Deckkraft",
    0, 255,
    st.session_state["opacity"],
    key="opacity"
)

padding = st.sidebar.slider(
    "Abstand",
    10, 200,
    st.session_state["padding"],
    key="padding"
)

st.sidebar.divider()

# Export
st.sidebar.subheader("📤 Export")

output_format = st.sidebar.selectbox(
    "Format",
    ["PNG", "JPEG"],
    index=0 if st.session_state["output_format"] == "PNG" else 1,
    key="output_format"
)

if output_format == "JPEG":
    jpeg_quality = st.sidebar.slider(
        "JPEG Qualität",
        1, 100,
        st.session_state["jpeg_quality"],
        key="jpeg_quality"
    )
else:
    jpeg_quality = 85

# =============================================================================
# MAIN AREA
# =============================================================================

st.title("🎨 Content Factory")
st.write("Schütze deine Bilder mit Metadaten-Entfernung und Wasserzeichen.")

# Free-User Warnung
if not is_pro and not is_admin:
    st.warning("🔒 **FREE Plan:** Nur 1 Bild pro Batch | Fester Wasserzeichen-Text | Upgrade für mehr Features!")

st.divider()

# Layout
col_left, col_right = st.columns([1, 1])

# =============================================================================
# LINKE SPALTE - Upload & Preview
# =============================================================================

with col_left:
    st.subheader("📤 Upload")
    
    uploaded_files = st.file_uploader(
        "Bilder hochladen",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        # Free-User: Nur 1 Bild
        if not is_pro and not is_admin and len(uploaded_files) > 1:
            st.info(f"📋 {len(uploaded_files)} hochgeladen, aber nur 1 wird verarbeitet (FREE)")
            files_to_process = uploaded_files[:1]
        else:
            files_to_process = uploaded_files
        
        st.success(f"✅ {len(files_to_process)} Bild(er)")
        
        # Live-Vorschau
        st.divider()
        st.subheader("👁️ Vorschau")
        
        first_file = files_to_process[0]
        preview_img = Image.open(first_file)
        first_file.seek(0)
        
        cleaned = remove_metadata(preview_img)
        watermarked = add_watermark(
            cleaned,
            st.session_state["watermark_text"] if (is_pro or is_admin) else "Created with CreatorOS",
            st.session_state["opacity"],
            st.session_state["padding"],
            is_pro or is_admin
        )
        
        tab1, tab2 = st.tabs(["Original", "Wasserzeichen"])
        
        with tab1:
            st.image(preview_img, use_container_width=True)
        
        with tab2:
            st.image(watermarked, use_container_width=True)
            
            # Dateigröße
            buf = io.BytesIO()
            if output_format == "PNG":
                watermarked.save(buf, format="PNG")
            else:
                watermarked.save(buf, format="JPEG", quality=jpeg_quality, optimize=True)
            
            st.caption(f"📊 Größe: {format_bytes(len(buf.getvalue()))}")
    else:
        st.info("👆 Bilder hochladen")

# =============================================================================
# RECHTE SPALTE - Processing
# =============================================================================

with col_right:
    st.subheader("🚀 Verarbeitung")
    
    if uploaded_files:
        # Free-User: Nur 1 Bild
        if not is_pro and not is_admin and len(uploaded_files) > 1:
            files_to_process = uploaded_files[:1]
        else:
            files_to_process = uploaded_files
        
        if len(files_to_process) > 1:
            st.info(f"📋 {len(files_to_process)} Bilder bereit")
        
        if st.button("🚀 Verarbeiten & ZIP Download", type="primary", use_container_width=True):
            progress = st.progress(0)
            status = st.empty()
            
            processed = []
            
            for idx, file in enumerate(files_to_process):
                status.text(f"⏳ {idx+1}/{len(files_to_process)}: {file.name}")
                
                img = Image.open(file)
                cleaned = remove_metadata(img)
                final = add_watermark(
                    cleaned,
                    st.session_state["watermark_text"] if (is_pro or is_admin) else "Created with CreatorOS",
                    st.session_state["opacity"],
                    st.session_state["padding"],
                    is_pro or is_admin
                )
                
                processed.append({
                    'image': final,
                    'filename': file.name
                })
                
                progress.progress((idx + 1) / len(files_to_process))
                file.seek(0)
            
            status.empty()
            progress.empty()
            
            st.success(f"🎉 {len(processed)} Bild(er) verarbeitet!")
            
            # ZIP erstellen
            zip_buf = io.BytesIO()
            ext = "png" if output_format == "PNG" else "jpg"
            
            with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                for idx, item in enumerate(processed):
                    img_buf = io.BytesIO()
                    
                    if output_format == "PNG":
                        item['image'].save(img_buf, format="PNG")
                    else:
                        item['image'].save(img_buf, format="JPEG", quality=jpeg_quality, optimize=True)
                    
                    name = item['filename'].rsplit('.', 1)[0]
                    zf.writestr(f"{name}.{ext}", img_buf.getvalue())
            
            zip_buf.seek(0)
            
            st.info(f"📦 ZIP: {format_bytes(len(zip_buf.getvalue()))}")
            
            st.download_button(
                "⬇️ ZIP herunterladen",
                zip_buf,
                "creatorOS_processed.zip",
                "application/zip",
                use_container_width=True
            )
            
            # Vorschau
            st.divider()
            st.subheader("🖼️ Galerie")
            
            for i in range(0, min(len(processed), 4), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(processed):
                        with cols[j]:
                            st.image(
                                processed[i + j]['image'],
                                caption=processed[i + j]['filename'],
                                use_container_width=True
                            )
    else:
        st.info("Warte auf Upload...")

st.divider()
st.caption("CreatorOS v10.0 Multi-Page | Made with ❤️ for Creators")

