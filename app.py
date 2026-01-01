import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import zipfile
from supabase import create_client, Client
import pandas as pd

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="CreatorOS",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CONSTANTS
# =============================================================================
ADMIN_EMAIL = "janick@icanhasbucket.de"
PAYMENT_LINK = "https://buy.stripe.com/your-payment-link"  # Hier deinen Stripe-Link einfügen
IMPRESSUM_LINK = "https://creatordeckapp.com/impressum"
DATENSCHUTZ_LINK = "https://creatordeckapp.com/datenschutz"

# =============================================================================
# SUPABASE SETUP
# =============================================================================

@st.cache_resource
def init_supabase():
    """Initialisiere Supabase Client"""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase: Client = init_supabase()

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

if "user" not in st.session_state:
    st.session_state["user"] = None

if "is_pro" not in st.session_state:
    st.session_state["is_pro"] = False

if "watermark_text" not in st.session_state:
    st.session_state["watermark_text"] = "© CreatorOS"

if "opacity" not in st.session_state:
    st.session_state["opacity"] = 180

if "padding" not in st.session_state:
    st.session_state["padding"] = 50

if "output_format" not in st.session_state:
    st.session_state["output_format"] = "PNG"

if "jpeg_quality" not in st.session_state:
    st.session_state["jpeg_quality"] = 85

# =============================================================================
# AUTH FUNCTIONS
# =============================================================================

def login_screen():
    """Login/Signup Screen"""
    st.title("🔒 CreatorOS")
    st.write("Privacy & Watermark Bot für Content-Creator")
    
    st.divider()
    
    tab1, tab2 = st.tabs(["Login", "Registrieren"])
    
    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Passwort", type="password", key="login_password")
        
        if st.button("🔓 Einloggen", type="primary", use_container_width=True):
            if email and password:
                try:
                    response = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    
                    if response.user:
                        st.session_state["user"] = response.user
                        load_user_settings(email)
                        st.success("✅ Erfolgreich eingeloggt!")
                        st.rerun()
                    else:
                        st.error("❌ Login fehlgeschlagen")
                except Exception as e:
                    st.error(f"❌ Fehler: {str(e)}")
            else:
                st.warning("⚠️ Bitte Email und Passwort eingeben")
    
    with tab2:
        st.subheader("Registrieren")
        email_signup = st.text_input("Email", key="signup_email")
        password_signup = st.text_input("Passwort", type="password", key="signup_password")
        password_confirm = st.text_input("Passwort bestätigen", type="password", key="signup_password_confirm")
        
        if st.button("📝 Registrieren", type="primary", use_container_width=True):
            if email_signup and password_signup and password_confirm:
                if password_signup != password_confirm:
                    st.error("❌ Passwörter stimmen nicht überein")
                elif len(password_signup) < 6:
                    st.error("❌ Passwort muss mindestens 6 Zeichen lang sein")
                else:
                    try:
                        response = supabase.auth.sign_up({
                            "email": email_signup,
                            "password": password_signup
                        })
                        
                        if response.user:
                            st.success("✅ Registrierung erfolgreich! Bitte logge dich ein.")
                            # Initialisiere User-Settings in DB
                            init_user_settings(email_signup)
                        else:
                            st.error("❌ Registrierung fehlgeschlagen")
                    except Exception as e:
                        st.error(f"❌ Fehler: {str(e)}")
            else:
                st.warning("⚠️ Bitte alle Felder ausfüllen")
    
    # Footer auf Login-Seite
    st.divider()
    st.markdown(f"[Impressum]({IMPRESSUM_LINK}) • [Datenschutz]({DATENSCHUTZ_LINK})")
    st.caption("© 2025 CreatorDeck")

def logout():
    """Logout User"""
    try:
        supabase.auth.sign_out()
    except:
        pass
    st.session_state["user"] = None
    st.session_state["is_pro"] = False
    st.rerun()

# =============================================================================
# DATABASE FUNCTIONS
# =============================================================================

def init_user_settings(email):
    """Initialisiere User-Settings in der Datenbank"""
    try:
        supabase.table("user_settings").insert({
            "user_id": email,
            "email": email,
            "is_pro": False,
            "watermark_text": "© CreatorOS",
            "opacity": 180,
            "padding": 50,
            "output_format": "PNG",
            "jpeg_quality": 85
        }).execute()
    except Exception as e:
        print(f"Error initializing settings: {e}")

def load_user_settings(email):
    """Lade User-Settings aus der Datenbank"""
    try:
        response = supabase.table("user_settings").select("*").eq("user_id", email).execute()
        
        if response.data and len(response.data) > 0:
            settings = response.data[0]
            st.session_state["is_pro"] = settings.get("is_pro", False)
            st.session_state["watermark_text"] = settings.get("watermark_text", "© CreatorOS")
            st.session_state["opacity"] = settings.get("opacity", 180)
            st.session_state["padding"] = settings.get("padding", 50)
            st.session_state["output_format"] = settings.get("output_format", "PNG")
            st.session_state["jpeg_quality"] = settings.get("jpeg_quality", 85)
        else:
            # Settings existieren nicht, erstelle sie
            init_user_settings(email)
    except Exception as e:
        st.error(f"Fehler beim Laden: {str(e)}")

def save_user_settings(email):
    """Speichere User-Settings in der Datenbank"""
    try:
        supabase.table("user_settings").upsert({
            "user_id": email,
            "email": email,
            "is_pro": st.session_state["is_pro"],
            "watermark_text": st.session_state["watermark_text"],
            "opacity": st.session_state["opacity"],
            "padding": st.session_state["padding"],
            "output_format": st.session_state["output_format"],
            "jpeg_quality": st.session_state["jpeg_quality"]
        }).execute()
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern: {str(e)}")
        return False

def get_all_users():
    """Admin: Lade alle User"""
    try:
        response = supabase.table("user_settings").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Fehler: {str(e)}")
        return []

def upgrade_user_to_pro(email):
    """Admin: Upgrade User zu PRO"""
    try:
        supabase.table("user_settings").update({"is_pro": True}).eq("email", email).execute()
        return True
    except Exception as e:
        st.error(f"Fehler: {str(e)}")
        return False

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
# MAIN APP
# =============================================================================

# Wenn nicht eingeloggt, zeige Login-Screen
if st.session_state["user"] is None:
    login_screen()
else:
    user = st.session_state["user"]
    user_email = user.email
    is_pro = st.session_state["is_pro"]
    is_admin = (user_email == ADMIN_EMAIL)
    
    # =============================================================================
    # SIDEBAR
    # =============================================================================
    
    st.sidebar.title("⚙️ CreatorOS")
    
    # User Info
    st.sidebar.subheader("👤 User")
    st.sidebar.text(user_email)
    
    if is_admin:
        st.sidebar.error("👑 ADMIN")
    elif is_pro:
        st.sidebar.success("✨ PRO")
    else:
        st.sidebar.info("🆓 FREE")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
    
    st.sidebar.divider()
    
    # Admin Panel
    if is_admin:
        with st.sidebar.expander("👑 Admin Dashboard", expanded=False):
            st.subheader("User Management")
            
            all_users = get_all_users()
            
            if all_users:
                df = pd.DataFrame(all_users)
                st.dataframe(df[["email", "is_pro"]], use_container_width=True)
                
                st.divider()
                
                upgrade_email = st.text_input("User Email für Upgrade")
                
                if st.button("⬆️ Zum PRO machen"):
                    if upgrade_email:
                        if upgrade_user_to_pro(upgrade_email):
                            st.success(f"✅ {upgrade_email} ist jetzt PRO!")
                            st.rerun()
                    else:
                        st.warning("⚠️ Email eingeben")
            else:
                st.info("Keine User gefunden")
        
        st.sidebar.divider()
    
    # Einstellungen
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
    
    # Einstellungen speichern
    if st.sidebar.button("💾 Einstellungen speichern", use_container_width=True):
        if save_user_settings(user_email):
            st.sidebar.success("✅ Gespeichert!")
    
    st.sidebar.divider()
    
    # Upgrade-Bereich für Free-User
    if not is_pro and not is_admin:
        st.sidebar.info("🔒 **Free Plan**\n\nLimitiert auf 1 Bild pro Batch")
        st.sidebar.link_button(
            "🚀 Upgrade auf PRO",
            PAYMENT_LINK,
            use_container_width=True
        )
        st.sidebar.divider()
    
    # Footer
    st.sidebar.divider()
    st.sidebar.markdown(
        f"[Impressum]({IMPRESSUM_LINK}) • [Datenschutz]({DATENSCHUTZ_LINK})",
        unsafe_allow_html=True
    )
    st.sidebar.caption("© 2025 CreatorDeck")
    
    # =============================================================================
    # MAIN AREA
    # =============================================================================
    
    st.title("🔒 CreatorOS - Privacy & Watermark Bot")
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
    st.caption("CreatorOS v10.0 | Made with ❤️ for Creators")
