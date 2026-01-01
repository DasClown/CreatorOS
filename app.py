import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import zipfile

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
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

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
    
    Args:
        image: PIL Image Objekt
        watermark_type: "text" oder "logo"
        position: "tiled", "center", "bottom_right"
        text: Wasserzeichen-Text (nur bei watermark_type="text")
        logo_image: PIL Image Objekt des Logos (nur bei watermark_type="logo")
        opacity: Transparenz (0-255, höher = deckender)
        padding: Abstand (bei tiled zwischen Wasserzeichen, bei bottom_right vom Rand)
        size_factor: Größenfaktor (für Text: Multiplier, für Logo: % der Bildbreite)
    """
    # Konvertiere zu RGBA
    base_image = image.convert("RGBA")
    
    # Erstelle transparentes Overlay
    overlay = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    if watermark_type == "text":
        # TEXT-WASSERZEICHEN
        # Berechne dynamische Schriftgröße
        font_size = int(image.height * 0.05 * size_factor)
        
        # Versuche TrueType Font zu laden
        font = None
        font_paths = [
            "arial.ttf",  # Windows
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux Alternative
        ]
        
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except:
                continue
        
        # Fallback auf Default Font
        if font is None:
            font = ImageFont.load_default()
        
        # Definiere Textfarbe mit konfigurierbarer Transparenz
        text_color = (150, 150, 150, opacity)
        
        # Ermittle Textgröße
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Positionierung
        if position == "tiled":
            # Gekachelt über das gesamte Bild
            y_step = text_height + padding
            x_step = text_width + padding
            
            for y in range(0, base_image.height + y_step, y_step):
                for x in range(0, base_image.width + x_step, x_step):
                    draw.text((x, y), text, fill=text_color, font=font)
        
        elif position == "center":
            # Zentriert
            x = (base_image.width - text_width) // 2
            y = (base_image.height - text_height) // 2
            draw.text((x, y), text, fill=text_color, font=font)
        
        elif position == "bottom_right":
            # Unten rechts mit Abstand (padding)
            x = base_image.width - text_width - padding
            y = base_image.height - text_height - padding
            draw.text((x, y), text, fill=text_color, font=font)
    
    else:
        # LOGO-WASSERZEICHEN
        if logo_image is None:
            return image  # Kein Logo verfügbar
        
        # Bereite Logo vor
        logo = logo_image.convert("RGBA")
        
        # Skaliere Logo basierend auf size_factor (% der Bildbreite)
        target_width = int(base_image.width * size_factor)
        aspect_ratio = logo.height / logo.width
        target_height = int(target_width * aspect_ratio)
        logo = logo.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Wende Transparenz auf Logo an
        logo_with_opacity = logo.copy()
        if logo_with_opacity.mode == 'RGBA':
            # Extrahiere den Alpha-Kanal und skaliere ihn
            alpha = logo_with_opacity.split()[3]
            alpha = alpha.point(lambda p: int(p * (opacity / 255)))
            logo_with_opacity.putalpha(alpha)
        else:
            # Wenn kein Alpha-Kanal, erstelle einen
            alpha = Image.new('L', logo.size, opacity)
            logo_with_opacity.putalpha(alpha)
        
        logo_width = logo_with_opacity.width
        logo_height = logo_with_opacity.height
        
        # Positionierung
        if position == "tiled":
            # Gekachelt über das gesamte Bild
            y_step = logo_height + padding
            x_step = logo_width + padding
            
            for y in range(0, base_image.height, y_step):
                for x in range(0, base_image.width, x_step):
                    overlay.paste(logo_with_opacity, (x, y), logo_with_opacity)
        
        elif position == "center":
            # Zentriert
            x = (base_image.width - logo_width) // 2
            y = (base_image.height - logo_height) // 2
            overlay.paste(logo_with_opacity, (x, y), logo_with_opacity)
        
        elif position == "bottom_right":
            # Unten rechts mit Abstand (padding)
            x = base_image.width - logo_width - padding
            y = base_image.height - logo_height - padding
            overlay.paste(logo_with_opacity, (x, y), logo_with_opacity)
    
    # Kombiniere Basisbild und Overlay
    final_image = Image.alpha_composite(base_image, overlay)
    
    # Konvertiere zurück zu RGB
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
# SIDEBAR - Einstellungen
# =============================================================================

st.sidebar.title("⚙️ Einstellungen")

# Wasserzeichen-Typ Auswahl
watermark_type = st.sidebar.radio(
    "Wasserzeichen-Typ",
    ["Text", "Bild/Logo"],
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
        value="© CreatorOS",
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
        value=1.0,
        step=0.1,
        help="Multiplier für die Textgröße"
    )
else:
    size_factor = st.sidebar.slider(
        "Logo-Größe",
        min_value=0.05,
        max_value=0.50,
        value=0.15,
        step=0.05,
        help="Logo-Breite als % der Bildbreite"
    )

# Transparenz-Slider
opacity = st.sidebar.slider(
    "Deckkraft",
    min_value=0,
    max_value=255,
    value=180,
    help="0 = komplett transparent, 255 = komplett deckend"
)

# Padding-Slider (mit kontextabhängiger Beschreibung)
if position == "tiled":
    padding_help = "Abstand in Pixeln zwischen den Wasserzeichen"
    padding_label = "Abstand zwischen Wasserzeichen"
elif position == "bottom_right":
    padding_help = "Abstand vom Rand in Pixeln"
    padding_label = "Rand-Abstand"
else:  # center
    padding_help = "Hat keine Auswirkung bei zentrierter Positionierung"
    padding_label = "Abstand (nicht relevant)"

padding = st.sidebar.slider(
    padding_label,
    min_value=10,
    max_value=200,
    value=50,
    help=padding_help,
    disabled=(position == "center")  # Deaktivieren bei zentriert
)

st.sidebar.divider()

# Export-Einstellungen
with st.sidebar.expander("📤 Export-Einstellungen", expanded=False):
    filename_prefix = st.text_input(
        "Dateiname-Präfix",
        value="",
        help="Optional: Präfix für alle Dateien (z.B. 'MyBrand_'). Leer lassen für Originalnamen."
    )
    
    output_format = st.selectbox(
        "Ausgabe-Format",
        ["PNG", "JPEG"],
        help="PNG = verlustfrei, größere Dateien. JPEG = komprimiert, kleinere Dateien."
    )
    
    jpeg_quality = 85
    if output_format == "JPEG":
        jpeg_quality = st.slider(
            "JPEG-Qualität",
            min_value=1,
            max_value=100,
            value=85,
            help="Höhere Qualität = bessere Bildqualität, größere Dateien"
        )

st.sidebar.divider()

# Info-Box
st.sidebar.info("💡 **Hinweis:** Einstellungen gelten für alle Bilder im aktuellen Batch.")

# Zusätzliche Infos
with st.sidebar.expander("ℹ️ Über CreatorOS"):
    st.write("""
    **CreatorOS v5.0 Final**
    
    Features:
    - ✅ EXIF-Metadaten-Entfernung
    - ✅ Auto-Rotation Korrektur
    - ✅ Text-Wasserzeichen
    - ✅ Logo-Wasserzeichen
    - ✅ Flexible Positionierung
    - ✅ Export-Einstellungen
    - ✅ Live-Vorschau
    - ✅ Batch-Verarbeitung
    - ✅ ZIP-Download
    
    Perfekt für Content-Creator!
    """)

# =============================================================================
# MAIN AREA - Header
# =============================================================================

st.title("🔒 CreatorOS - Privacy & Watermark Bot")
st.write("Schütze deine Bilder mit Metadaten-Entfernung und professionellen Wasserzeichen.")
st.divider()

# =============================================================================
# LAYOUT - Zwei Spalten für bessere UX
# =============================================================================

col_left, col_right = st.columns([1, 1])

# =============================================================================
# LINKE SPALTE - Upload & Vorschau
# =============================================================================

with col_left:
    st.subheader("📤 Upload")
    
    # File Uploader mit Multiple Files
    uploaded_files = st.file_uploader(
        "Lade ein oder mehrere Bilder hoch",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help="Unterstützte Formate: JPG, JPEG, PNG"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} Bild(er) hochgeladen")
        
        # Prüfe, ob Wasserzeichen-Einstellungen komplett sind
        can_preview = False
        if watermark_type == "Text" and watermark_text:
            can_preview = True
        elif watermark_type == "Bild/Logo" and logo_image:
            can_preview = True
        
        if can_preview:
            st.divider()
            st.subheader("👁️ Live-Vorschau")
            
            # Lade das erste Bild
            first_file = uploaded_files[0]
            preview_image = Image.open(first_file)
            first_file.seek(0)  # Reset file pointer
            
            # Verarbeite das Bild
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
            
            # Zeige Tabs für Vorher/Nachher
            tab1, tab2 = st.tabs(["Original", "Mit Wasserzeichen"])
            
            with tab1:
                st.image(preview_image, caption=first_file.name, use_container_width=True)
            
            with tab2:
                st.image(watermarked_preview, caption="Vorschau", use_container_width=True)
                
                # Berechne und zeige Dateigröße
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
        
        # Quick Tips
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
        # Prüfe, ob Verarbeitung möglich ist
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
            
            # Button zum Verarbeiten
            if st.button("🚀 Alle Bilder verarbeiten", type="primary", use_container_width=True):
                # Progress Bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Liste für verarbeitete Bilder
                processed_images = []
                
                # Verarbeite jedes Bild
                for idx, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"⏳ Verarbeite {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                    
                    # Bild laden
                    image = Image.open(uploaded_file)
                    
                    # Metadaten entfernen (inkl. Auto-Rotation)
                    cleaned_image = remove_metadata(image)
                    
                    # Wasserzeichen hinzufügen
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
                    
                    # Speichere das verarbeitete Bild
                    processed_images.append({
                        'image': final_image,
                        'original_filename': uploaded_file.name
                    })
                    
                    # Update Progress Bar
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                    
                    # Reset file pointer
                    uploaded_file.seek(0)
                
                status_text.empty()
                progress_bar.empty()
                
                st.success(f"🎉 {len(processed_images)} Bild(er) erfolgreich verarbeitet!")
                
                # Erstelle ZIP-Datei
                zip_buffer = io.BytesIO()
                
                # Bestimme Datei-Endung
                file_extension = "png" if output_format == "PNG" else "jpg"
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for idx, item in enumerate(processed_images):
                        # Konvertiere Bild zu Bytes
                        img_buffer = io.BytesIO()
                        
                        if output_format == "PNG":
                            item['image'].save(img_buffer, format="PNG")
                        else:
                            item['image'].save(img_buffer, format="JPEG", quality=jpeg_quality, optimize=True)
                        
                        img_bytes = img_buffer.getvalue()
                        
                        # Generiere Dateinamen
                        if filename_prefix:
                            new_filename = f"{filename_prefix}{idx+1:03d}.{file_extension}"
                        else:
                            original_name_without_ext = item['original_filename'].rsplit('.', 1)[0]
                            new_filename = f"{original_name_without_ext}.{file_extension}"
                        
                        zip_file.writestr(new_filename, img_bytes)
                
                # Setze Buffer-Position zurück
                zip_buffer.seek(0)
                
                # Zeige ZIP-Info
                zip_size = len(zip_buffer.getvalue())
                st.info(f"📦 ZIP-Archiv: {format_bytes(zip_size)}")
                
                # Download-Button
                st.download_button(
                    label="⬇️ ZIP herunterladen",
                    data=zip_buffer,
                    file_name="creatorOS_processed.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                
                st.divider()
                
                # Galerie-Vorschau (max 6 Bilder in kompakter Ansicht)
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
        
        # Features
        with st.expander("✨ Features"):
            st.markdown("""
            **Privacy:**
            - EXIF-Metadaten entfernen
            - GPS-Daten löschen
            - Auto-Rotation Korrektur
            
            **Wasserzeichen:**
            - Text & Logo Support
            - 3 Positionierungs-Modi
            - Anpassbare Transparenz
            
            **Export:**
            - PNG/JPEG Format
            - Qualitäts-Kontrolle
            - Batch-Verarbeitung
            """)

st.divider()

# Footer
st.caption("CreatorOS v5.0 Final | Made for Content Creators 🎨")
