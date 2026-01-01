"""
Shared Utilities für CreatorOS
Enthält: Supabase Client, Auth-Funktionen, DB-Operations, Custom CSS
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
# CUSTOM CSS
# =============================================================================

def inject_custom_css():
    """Injiziert Custom CSS für ein modernes, poliertes Design"""
    st.markdown("""
    <style>
    /* ===== Google Font Import ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* ===== Global Font ===== */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* ===== Layout Optimierung ===== */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px;
    }
    
    /* ===== Buttons mit Gradient ===== */
    .stButton > button {
        background: linear-gradient(135deg, #7C3AED 0%, #A78BFA 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 20px rgba(124, 58, 237, 0.4);
        background: linear-gradient(135deg, #6D28D9 0%, #8B5CF6 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0px) scale(0.98);
    }
    
    /* Primary Button spezielle Styles */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7C3AED 0%, #A78BFA 100%);
        font-weight: 700;
    }
    
    /* Secondary Button */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
        box-shadow: 0 4px 12px rgba(30, 41, 59, 0.25);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #334155 0%, #475569 100%);
    }
    
    /* ===== Metriken als Cards ===== */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1E293B 0%, #1a2332 100%);
        padding: 1.5rem 1.25rem;
        border-radius: 16px;
        border: 1px solid rgba(124, 58, 237, 0.1);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        border-color: rgba(124, 58, 237, 0.3);
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.2);
    }
    
    [data-testid="stMetric"] label {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #94A3B8 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    
    /* ===== DataFrames & Tables ===== */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(124, 58, 237, 0.15);
    }
    
    /* DataFrame Header */
    [data-testid="stDataFrame"] thead tr th {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%) !important;
        color: #F8FAFC !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        font-size: 0.8rem !important;
        letter-spacing: 0.5px;
        padding: 1rem !important;
        border-bottom: 2px solid #7C3AED !important;
    }
    
    /* DataFrame Rows */
    [data-testid="stDataFrame"] tbody tr {
        transition: background-color 0.2s ease;
    }
    
    [data-testid="stDataFrame"] tbody tr:hover {
        background-color: rgba(124, 58, 237, 0.08) !important;
    }
    
    /* DataFrame Cells */
    [data-testid="stDataFrame"] td {
        padding: 0.75rem 1rem !important;
        border-bottom: 1px solid rgba(148, 163, 184, 0.1) !important;
    }
    
    /* ===== Sidebar Styling ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
        border-right: 1px solid rgba(124, 58, 237, 0.2);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: #F8FAFC !important;
        font-weight: 700 !important;
    }
    
    /* ===== Input Fields ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea textarea,
    .stDateInput > div > div > input {
        background-color: #1E293B !important;
        border: 1px solid rgba(124, 58, 237, 0.2) !important;
        border-radius: 8px !important;
        color: #F8FAFC !important;
        padding: 0.75rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea textarea:focus,
    .stDateInput > div > div > input:focus {
        border-color: #7C3AED !important;
        box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2) !important;
    }
    
    /* ===== Select Boxes ===== */
    .stSelectbox > div > div {
        background-color: #1E293B !important;
        border: 1px solid rgba(124, 58, 237, 0.2) !important;
        border-radius: 8px !important;
    }
    
    /* ===== Sliders ===== */
    .stSlider > div > div > div > div {
        background-color: #7C3AED !important;
    }
    
    .stSlider > div > div > div > div > div {
        background-color: #A78BFA !important;
    }
    
    /* ===== Tabs ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: #94A3B8;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(124, 58, 237, 0.1);
        color: #A78BFA;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7C3AED 0%, #A78BFA 100%);
        color: white !important;
    }
    
    /* ===== Expander ===== */
    .streamlit-expanderHeader {
        background-color: #1E293B !important;
        border-radius: 8px !important;
        border: 1px solid rgba(124, 58, 237, 0.2) !important;
        padding: 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #7C3AED !important;
        background-color: rgba(124, 58, 237, 0.05) !important;
    }
    
    /* ===== Info/Success/Warning/Error Boxes ===== */
    .stAlert {
        border-radius: 12px !important;
        border-left-width: 4px !important;
        padding: 1rem 1.25rem !important;
        backdrop-filter: blur(10px);
    }
    
    /* ===== Progress Bar ===== */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #7C3AED 0%, #A78BFA 100%);
        border-radius: 10px;
    }
    
    /* ===== Charts ===== */
    .js-plotly-plot .plotly .modebar {
        background-color: #1E293B !important;
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    /* ===== Divider ===== */
    hr {
        border-color: rgba(124, 58, 237, 0.2) !important;
        margin: 2rem 0 !important;
    }
    
    /* ===== File Uploader ===== */
    [data-testid="stFileUploader"] {
        background-color: #1E293B;
        border: 2px dashed rgba(124, 58, 237, 0.4);
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #7C3AED;
        background-color: rgba(124, 58, 237, 0.05);
    }
    
    /* ===== Download Button ===== */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10B981 0%, #34D399 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4);
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
    }
    
    /* ===== Link Button ===== */
    .stLinkButton > a {
        background: linear-gradient(135deg, #7C3AED 0%, #A78BFA 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        text-decoration: none !important;
        display: inline-block !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25) !important;
    }
    
    .stLinkButton > a:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(124, 58, 237, 0.4) !important;
    }
    
    /* ===== Code Blocks ===== */
    code {
        background-color: #1E293B !important;
        color: #A78BFA !important;
        padding: 0.25rem 0.5rem !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
    }
    
    /* ===== Scrollbar ===== */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0F172A;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #7C3AED 0%, #A78BFA 100%);
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #6D28D9 0%, #8B5CF6 100%);
    }
    
    /* ===== Animation ===== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .main .block-container > div {
        animation: fadeIn 0.5s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)

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
    # Inject CSS first
    inject_custom_css()
    
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
    
    # Inject CSS für alle Pages
    inject_custom_css()
    
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
