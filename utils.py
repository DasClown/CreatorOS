"""
Shared Utilities für CreatorOS
Enthält: Supabase Client, Auth-Funktionen, DB-Operations
"""

import streamlit as st
from supabase import create_client, Client

# =============================================================================
# CONSTANTS
# =============================================================================
ADMIN_EMAIL = "janick@icanhasbucket.de"
PAYMENT_LINK = "https://buy.stripe.com/28E8wO0W59Y46rM8rG6J200"

IMPRESSUM_TEXT = """
**Angaben gemäß § 5 TMG:**

CreatorDeck / Janick Thum
[Deine Adresse hier]

**Kontakt:**  
E-Mail: janick@icanhasbucket.de

**Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV:**  
Janick Thum  
[Adresse]
"""

DATENSCHUTZ_TEXT = """
**Datenschutzerklärung für CreatorDeck**

**1. Datenerhebung**  
Wir erheben nur die für die Nutzung der App notwendigen Daten (E-Mail, Passwort verschlüsselt).

**2. Nutzung**  
Ihre hochgeladenen Bilder werden nicht gespeichert und verbleiben nur temporär im RAM während der Verarbeitung.

**3. Supabase**  
Wir nutzen Supabase für Authentifizierung und Einstellungen. Details: https://supabase.com/privacy

**4. Ihre Rechte**  
Sie haben jederzeit das Recht auf Auskunft, Löschung und Berichtigung Ihrer Daten.

**Kontakt:**  
janick@icanhasbucket.de
"""

# =============================================================================
# SUPABASE SETUP
# =============================================================================

@st.cache_resource
def init_supabase():
    """Initialisiere Supabase Client"""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def init_session_state():
    """Initialisiere alle Session State Variablen"""
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

def logout():
    """Logout User"""
    supabase = init_supabase()
    try:
        supabase.auth.sign_out()
    except:
        pass
    st.session_state["user"] = None
    st.session_state["is_pro"] = False
    st.rerun()

def login_screen():
    """Login/Signup Screen"""
    supabase = init_supabase()
    
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
                            init_user_settings(email_signup)
                        else:
                            st.error("❌ Registrierung fehlgeschlagen")
                    except Exception as e:
                        st.error(f"❌ Fehler: {str(e)}")
            else:
                st.warning("⚠️ Bitte alle Felder ausfüllen")
    
    # Footer
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Impressum", use_container_width=True):
            show_impressum()
    with col2:
        if st.button("🔒 Datenschutz", use_container_width=True):
            show_datenschutz()
    
    st.caption("© 2025 CreatorDeck")

# =============================================================================
# DIALOG FUNCTIONS
# =============================================================================

@st.dialog("📄 Impressum")
def show_impressum():
    """Zeige Impressum im Dialog"""
    st.markdown(IMPRESSUM_TEXT)
    if st.button("Schließen", use_container_width=True):
        st.rerun()

@st.dialog("🔒 Datenschutz")
def show_datenschutz():
    """Zeige Datenschutzerklärung im Dialog"""
    st.markdown(DATENSCHUTZ_TEXT)
    if st.button("Schließen", use_container_width=True):
        st.rerun()

# =============================================================================
# DATABASE FUNCTIONS
# =============================================================================

def init_user_settings(email):
    """Initialisiere User-Settings in der Datenbank"""
    supabase = init_supabase()
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
    supabase = init_supabase()
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
            init_user_settings(email)
    except Exception as e:
        st.error(f"Fehler beim Laden: {str(e)}")

def save_user_settings(email):
    """Speichere User-Settings in der Datenbank"""
    supabase = init_supabase()
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
    supabase = init_supabase()
    try:
        response = supabase.table("user_settings").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Fehler: {str(e)}")
        return []

def upgrade_user_to_pro(email):
    """Admin: Upgrade User zu PRO"""
    supabase = init_supabase()
    try:
        supabase.table("user_settings").update({"is_pro": True}).eq("email", email).execute()
        return True
    except Exception as e:
        st.error(f"Fehler: {str(e)}")
        return False

def downgrade_user_from_pro(email):
    """Admin: Downgrade User von PRO"""
    supabase = init_supabase()
    try:
        supabase.table("user_settings").update({"is_pro": False}).eq("email", email).execute()
        return True
    except Exception as e:
        st.error(f"Fehler: {str(e)}")
        return False

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def check_auth():
    """Prüft ob User eingeloggt ist, sonst zeige Login Screen"""
    init_session_state()
    
    if st.session_state["user"] is None:
        login_screen()
        st.stop()
    
    return st.session_state["user"]

def render_sidebar():
    """Rendert Standard-Sidebar mit User-Info"""
    user = st.session_state["user"]
    user_email = user.email
    is_pro = st.session_state["is_pro"]
    is_admin = (user_email == ADMIN_EMAIL)
    
    st.sidebar.title("🎯 CreatorOS")
    
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
    
    # Upgrade-Bereich für Free-User
    if not is_pro and not is_admin:
        st.sidebar.info("🔒 **Free Plan**\n\nUpgrade für alle Features!")
        st.sidebar.link_button(
            "🚀 Upgrade auf PRO",
            PAYMENT_LINK,
            use_container_width=True
        )
        st.sidebar.divider()
    
    # Footer
    st.sidebar.divider()
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("📄 Impressum", use_container_width=True, key=f"impressum_sidebar_{id(user)}"):
            show_impressum()
    with col2:
        if st.button("🔒 Datenschutz", use_container_width=True, key=f"datenschutz_sidebar_{id(user)}"):
            show_datenschutz()
    
    st.sidebar.caption("© 2025 CreatorDeck")
    
    return user_email, is_pro, is_admin

