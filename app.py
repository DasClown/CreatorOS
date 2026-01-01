import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import zipfile
from supabase import create_client, Client

# =============================================================================
# PAGE CONFIG - Muss als ERSTES kommen
# =============================================================================
st.set_page_config(
    page_title="CreatorOS",
    page_icon="🔒",
    layout="wide"
)

# =============================================================================
# CUSTOM CSS - UI Cleanup
# =============================================================================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SUPABASE SETUP
# =============================================================================

@st.cache_resource
def init_supabase():
    """Initialisiere Supabase Client (mit Caching)"""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase: Client = init_supabase()

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def init_session_state():
    """Initialisiere Session State mit Default-Werten"""
    defaults = {
        "profile_name": "demo",
        "watermark_type": "Text",
        "position": "Gekachelt (Tiled)",
        "watermark_text": "© CreatorOS",
        "size_factor_text": 1.0,
        "size_factor_logo": 0.15,
        "opacity": 180,
        "padding": 50,
        "filename_prefix": "",
        "output_format": "PNG",
        "jpeg_quality": 85
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# =============================================================================
# DATABASE FUNCTIONS
# =============================================================================

def load_settings(profile_name):
    """Lade Einstellungen aus Supabase"""
    try:
        response = supabase.table("user_settings").select("*").eq("user_id", profile_name).execute()
        
        if response.data and len(response.data) > 0:
            settings = response.data[0]
            
            # Update Session State mit geladenen Werten
            st.session_state["watermark_type"] = settings.get("watermark_type", "Text")
            st.session_state["position"] = settings.get("position", "Gekachelt (Tiled)")
            st.session_state["watermark_text"] = settings.get("watermark_text", "© CreatorOS")
            st.session_state["size_factor_text"] = settings.get("size_factor_text", 1.0)
            st.session_state["size_factor_logo"] = settings.get("size_factor_logo", 0.15)
            st.session_state["opacity"] = settings.get("opacity", 180)
            st.session_state["padding"] = settings.get("padding", 50)
            st.session_state["filename_prefix"] = settings.get("filename_prefix", "")
            st.session_state["output_format"] = settings.get("output_format", "PNG")
            st.session_state["jpeg_quality"] = settings.get("jpeg_quality", 85)
            
            return True
        return False
    except Exception as e:
        st.error(f"Fehler beim Laden: {str(e)}")
        return False

def save_settings(profile_name):
    """Speichere Einstellungen in Supabase"""
    try:
        settings_data = {
            "user_id": profile_name,
            "watermark_type": st.session_state["watermark_type"],
            "position": st.session_state["position"],
            "watermark_text": st.session_state["watermark_text"],
            "size_factor_text": st.session_state["size_factor_text"],
            "size_factor_logo": st.session_state["size_factor_logo"],
            "opacity": st.session_state["opacity"],
            "padding": st.session_state["padding"],
            "filename_prefix": st.session_state["filename_prefix"],
            "output_format": st.session_state["output_format"],
            "jpeg_quality": st.session_state["jpeg_quality"]
        }
        
        supabase.table("user_settings").upsert(settings_data).execute()
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern: {str(e)}")
        return False

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def remove_metadata(image):
    """
    Entfernt alle Metadaten (EXIF, etc.) aus einem Bild.
    Korrigiert zuerst die Rotation basierend auf EXIF-Daten.
    """
    # Auto-Rotation basierend auf EXIF-Daten (BEVOR wir sie löschen)
    image = ImageOps.exif_transpose(image)
    
    # Entferne Metadaten durch Neuerstellen des Bildes
    data = list(image.getdata())
    new_image = Image.new(image.mode, image.size)
    new_image.putdata(data)
    return new_image

def add_watermark(image, watermark_type, position="tiled", text=None, logo_image=None, opacity=180, padding=50, size_factor=0.15):
    """
    Fügt ein Wasserzeichen über das Bild hinzu.
    """
    # Konvertiere zu RGBA
    base_image = image.convert("RGBA")
    
    # Erstelle transparentes Overlay
    overlay = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    if watermark_type == "text":
        # TEXT-WASSERZEICHEN
        font_size = int(image.height * 0.05 * size_factor)
        
        # Versuche TrueType Font zu laden
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
        
        # Positionierung
        if position == "tiled":
            y_step = text_height + padding
            x_step = text_width + padding
            
            for y in range(0, base_image.height + y_step, y_step):
                for x in range(0, base_image.width + x_step, x_step):
                    draw.text((x, y), text, fill=text_color, font=font)
        
        elif position == "center":
            x = (base_image.width - text_width) // 2
            y = (base_image.height - text_height) // 2
            draw.text((x, y), text, fill=text_color, font=font)
        
        elif position == "bottom_right":
            x = base_image.width - text_width - padding
            y = base_image.height - text_height - padding
            draw.text((x, y), text, fill=text_color, font=font)
    
    else:
        # LOGO-WASSERZEICHEN
        if logo_image is None:
            return image
        
        logo = logo_image.convert("RGBA")
        target_width = int(base_image.width * size_factor)
        aspect_ratio = logo.height / logo.width
        target_height = int(target_width * aspect_ratio)
        logo = logo.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        logo_with_opacity = logo.copy()
        if logo_with_opacity.mode == 'RGBA':
            alpha = logo_with_opacity.split()[3]
            alpha = alpha.point(lambda p: int(p * (opacity / 255)))
            logo_with_opacity.putalpha(alpha)
        else:
            alpha = Image.new('L', logo.size, opacity)
            logo_with_opacity.putalpha(alpha)
        
        logo_width = logo_with_opacity.width
        logo_height = logo_with_opacity.height
        
        # Positionierung
        if position == "tiled":
            y_step = logo_height + padding
            x_step = logo_width + padding
            
            for y in range(0, base_image.height, y_step):
                for x in range(0, base_image.width, x_step):
                    overlay.paste(logo_with_opacity, (x, y), logo_with_opacity)
        
        elif position == "center":
            x = (base_image.width - logo_width) // 2
            y = (base_image.height - logo_height) // 2
            overlay.paste(logo_with_opacity, (x, y), logo_with_opacity)
        
        elif position == "bottom_right":
            x = base_image.width - logo_width - padding
            y = base_image.height - logo_height - padding
            overlay.paste(logo_with_opacity, (x, y), logo_with_opacity)
    
    final_image = Image.alpha_composite(base_image, overlay)
    return final_image.convert("RGB")

def format_bytes(bytes_size):
    """Formatiert Bytes in lesbare Größe"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.2f} MB"

# =============================================================================
# SIDEBAR - Profil & Einstellungen
# =============================================================================

st.sidebar.title("👤 Profil")

# Profil-Name Input
profile_name = st.sidebar.text_input(
    "Profil-Name",
    value=st.session_state["profile_name"],
    key="profile_name",
    help="Dein Profil-Name zum Laden/Speichern der Einstellungen"
)

# Load/Save Buttons
col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("📥 Laden", use_container_width=True):
        if load_settings(st.session_state["profile_name"]):
            st.success("✅ Geladen!")
            st.rerun()
        else:
            st.info("Keine gespeicherten Einstellungen gefunden.")

with col2:
    if st.button("💾 Speichern", use_container_width=True):
        if save_settings(st.session_state["profile_name"]):
            st.success("✅ Gespeichert!")

st.sidebar.divider()
st.sidebar.title("⚙️ Einstellungen")

# Wasserzeichen-Typ Auswahl
watermark_type = st.sidebar.radio(
    "Wasserzeichen-Typ",
    ["Text", "Bild/Logo"],
    key="watermark_type",
    help="Wähle zwischen Text oder deinem eigenen Logo"
)

# Positionierung Auswahl
position_labels = {
    "Gekachelt (Tiled)": "tiled",
    "Zentriert": "center",
    "Unten Rechts": "bottom_right"
}

position_label = st.sidebar.selectbox(
    "Positionierung",
    list(position_labels.keys()),
    key="position",
    help="Wähle, wie das Wasserzeichen platziert werden soll"
)
position = position_labels[position_label]

st.sidebar.divider()

# Text-Input oder Logo-Upload basierend auf Typ
watermark_text = None
logo_file = None
logo_image = None

if watermark_type == "Text":
    watermark_text = st.sidebar.text_input(
        "Wasserzeichen-Text",
        value=st.session_state["watermark_text"],
        key="watermark_text",
        help="Der Text, der als Wasserzeichen verwendet wird"
    )
else:
    logo_file = st.sidebar.file_uploader(
        "Logo hochladen",
        type=["png", "jpg", "jpeg"],
        help="Lade dein Logo als PNG oder JPG hoch"
    )
    if logo_file:
        logo_image = Image.open(logo_file)
        st.sidebar.image(logo_image, caption="Dein Logo", width=150)

st.sidebar.divider()

# Größen-Slider
if watermark_type == "Text":
    size_factor = st.sidebar.slider(
        "Text-Größe",
        min_value=0.5,
        max_value=3.0,
        value=st.session_state["size_factor_text"],
        step=0.1,
        key="size_factor_text",
        help="Multiplier für die Textgröße"
    )
else:
    size_factor = st.sidebar.slider(
        "Logo-Größe",
        min_value=0.05,
        max_value=0.50,
        value=st.session_state["size_factor_logo"],
        step=0.05,
        key="size_factor_logo",
        help="Logo-Breite als % der Bildbreite"
    )

# Transparenz-Slider
opacity = st.sidebar.slider(
    "Deckkraft",
    min_value=0,
    max_value=255,
    value=st.session_state["opacity"],
    key="opacity",
    help="0 = komplett transparent, 255 = komplett deckend"
)

# Padding-Slider
if position == "tiled":
    padding_help = "Abstand in Pixeln zwischen den Wasserzeichen"
    padding_label = "Abstand zwischen Wasserzeichen"
elif position == "bottom_right":
    padding_help = "Abstand vom Rand in Pixeln"
    padding_label = "Rand-Abstand"
else:
    padding_help = "Hat keine Auswirkung bei zentrierter Positionierung"
    padding_label = "Abstand (nicht relevant)"

padding = st.sidebar.slider(
    padding_label,
    min_value=10,
    max_value=200,
    value=st.session_state["padding"],
    key="padding",
    help=padding_help,
    disabled=(position == "center")
)

st.sidebar.divider()

# Export-Einstellungen
with st.sidebar.expander("📤 Export-Einstellungen", expanded=False):
    filename_prefix = st.text_input(
        "Dateiname-Präfix",
        value=st.session_state["filename_prefix"],
        key="filename_prefix",
        help="Optional: Präfix für alle Dateien. Leer lassen für Originalnamen."
    )
    
    output_format = st.selectbox(
        "Ausgabe-Format",
        ["PNG", "JPEG"],
        index=0 if st.session_state["output_format"] == "PNG" else 1,
        key="output_format",
        help="PNG = verlustfrei, größere Dateien. JPEG = komprimiert, kleinere Dateien."
    )
    
    jpeg_quality = st.session_state["jpeg_quality"]
    if output_format == "JPEG":
        jpeg_quality = st.slider(
            "JPEG-Qualität",
            min_value=1,
            max_value=100,
            value=st.session_state["jpeg_quality"],
            key="jpeg_quality",
            help="Höhere Qualität = bessere Bildqualität, größere Dateien"
        )

st.sidebar.divider()

# Info-Box
st.sidebar.info("💡 **Tipp:** Lade dein Profil, um deine gespeicherten Einstellungen zu verwenden.")

# Zusätzliche Infos
with st.sidebar.expander("ℹ️ Über CreatorOS"):
    st.write("""
    **CreatorOS v6.0**
    
    Features:
    - ✅ Profil-System (Cloud-Speicherung)
    - ✅ EXIF-Metadaten-Entfernung
    - ✅ Auto-Rotation Korrektur
    - ✅ Text & Logo-Wasserzeichen
    - ✅ Flexible Positionierung
    - ✅ Export-Einstellungen
    - ✅ Live-Vorschau
    - ✅ Batch-Verarbeitung
    
    Powered by Supabase 🚀
    """)

# =============================================================================
# MAIN AREA - Header
# =============================================================================

st.title("🔒 CreatorOS - Privacy & Watermark Bot")
st.write("Schütze deine Bilder mit Metadaten-Entfernung und professionellen Wasserzeichen.")
st.divider()

# =============================================================================
# LAYOUT - Zwei Spalten
# =============================================================================

col_left, col_right = st.columns([1, 1])

# =============================================================================
# LINKE SPALTE - Upload & Vorschau
# =============================================================================

with col_left:
    st.subheader("📤 Upload")
    
    uploaded_files = st.file_uploader(
        "Lade ein oder mehrere Bilder hoch",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help="Unterstützte Formate: JPG, JPEG, PNG"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} Bild(er) hochgeladen")
        
        can_preview = False
        if watermark_type == "Text" and watermark_text:
            can_preview = True
        elif watermark_type == "Bild/Logo" and logo_image:
            can_preview = True
        
        if can_preview:
            st.divider()
            st.subheader("👁️ Live-Vorschau")
            
            first_file = uploaded_files[0]
            preview_image = Image.open(first_file)
            first_file.seek(0)
            
            cleaned_preview = remove_metadata(preview_image)
            watermarked_preview = add_watermark(
                cleaned_preview,
                watermark_type.lower().replace("/", "_"),
                position=position,
                text=watermark_text,
                logo_image=logo_image,
                opacity=opacity,
                padding=padding,
                size_factor=size_factor
            )
            
            tab1, tab2 = st.tabs(["Original", "Mit Wasserzeichen"])
            
            with tab1:
                st.image(preview_image, caption=first_file.name, use_container_width=True)
            
            with tab2:
                st.image(watermarked_preview, caption="Vorschau", use_container_width=True)
                
                preview_buffer = io.BytesIO()
                if output_format == "PNG":
                    watermarked_preview.save(preview_buffer, format="PNG")
                else:
                    watermarked_preview.save(preview_buffer, format="JPEG", quality=jpeg_quality, optimize=True)
                
                file_size = len(preview_buffer.getvalue())
                st.caption(f"📊 Geschätzte Dateigröße: {format_bytes(file_size)}")
        
        else:
            if watermark_type == "Bild/Logo" and not logo_image:
                st.warning("⚠️ Bitte lade ein Logo in der Sidebar hoch.")
    
    else:
        st.info("👆 Bitte lade ein oder mehrere Bilder hoch, um zu beginnen.")
        
        with st.expander("💡 Schnellstart"):
            st.markdown("""
            **In 3 Schritten:**
            1. Wasserzeichen konfigurieren (Sidebar)
            2. Bilder hochladen
            3. Verarbeiten & Download
            """)

# =============================================================================
# RECHTE SPALTE - Verarbeitung & Download
# =============================================================================

with col_right:
    st.subheader("🚀 Verarbeitung")
    
    if uploaded_files:
        can_process = False
        if watermark_type == "Text" and watermark_text:
            can_process = True
        elif watermark_type == "Bild/Logo" and logo_image:
            can_process = True
        
        if not can_process:
            st.warning("⚠️ Bitte konfiguriere das Wasserzeichen in der Sidebar.")
        else:
            if len(uploaded_files) > 1:
                st.info(f"📋 {len(uploaded_files)} Bilder bereit zur Verarbeitung")
            
            if st.button("🚀 Alle Bilder verarbeiten", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                processed_images = []
                
                for idx, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"⏳ Verarbeite {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                    
                    image = Image.open(uploaded_file)
                    cleaned_image = remove_metadata(image)
                    
                    final_image = add_watermark(
                        cleaned_image,
                        watermark_type.lower().replace("/", "_"),
                        position=position,
                        text=watermark_text,
                        logo_image=logo_image,
                        opacity=opacity,
                        padding=padding,
                        size_factor=size_factor
                    )
                    
                    processed_images.append({
                        'image': final_image,
                        'original_filename': uploaded_file.name
                    })
                    
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                    uploaded_file.seek(0)
                
                status_text.empty()
                progress_bar.empty()
                
                st.success(f"🎉 {len(processed_images)} Bild(er) erfolgreich verarbeitet!")
                
                zip_buffer = io.BytesIO()
                file_extension = "png" if output_format == "PNG" else "jpg"
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for idx, item in enumerate(processed_images):
                        img_buffer = io.BytesIO()
                        
                        if output_format == "PNG":
                            item['image'].save(img_buffer, format="PNG")
                        else:
                            item['image'].save(img_buffer, format="JPEG", quality=jpeg_quality, optimize=True)
                        
                        img_bytes = img_buffer.getvalue()
                        
                        if filename_prefix:
                            new_filename = f"{filename_prefix}{idx+1:03d}.{file_extension}"
                        else:
                            original_name_without_ext = item['original_filename'].rsplit('.', 1)[0]
                            new_filename = f"{original_name_without_ext}.{file_extension}"
                        
                        zip_file.writestr(new_filename, img_bytes)
                
                zip_buffer.seek(0)
                
                zip_size = len(zip_buffer.getvalue())
                st.info(f"📦 ZIP-Archiv: {format_bytes(zip_size)}")
                
                st.download_button(
                    label="⬇️ ZIP herunterladen",
                    data=zip_buffer,
                    file_name="creatorOS_processed.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                
                st.divider()
                
                st.subheader("🖼️ Vorschau")
                preview_count = min(len(processed_images), 6)
                
                if len(processed_images) > 6:
                    st.caption(f"Zeige {preview_count} von {len(processed_images)} Bildern")
                
                for i in range(0, preview_count, 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < preview_count:
                            with cols[j]:
                                st.image(
                                    processed_images[i + j]['image'],
                                    caption=processed_images[i + j]['original_filename'],
                                    use_container_width=True
                                )
    else:
        st.info("Warte auf Bilder-Upload...")
        
        with st.expander("✨ Features"):
            st.markdown("""
            **Privacy:**
            - EXIF-Metadaten entfernen
            - GPS-Daten löschen
            - Auto-Rotation Korrektur
            
            **Wasserzeichen:**
            - Text & Logo Support
            - 3 Positionierungs-Modi
            - Cloud-Speicherung
            
            **Export:**
            - PNG/JPEG Format
            - Batch-Verarbeitung
            """)

st.divider()
st.caption("CreatorOS v6.0 | Cloud-Powered 🚀")
