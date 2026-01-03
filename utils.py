"""
Shared Utilities für CreatorOS
Enthält: Supabase Client, Auth-Funktionen, DB-Operations, Custom CSS
"""

import streamlit as st
from supabase import create_client, Client

try:
    from googleapiclient.discovery import build
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

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
    """Injiziert minimalistisches CSS im Trade Republic / Banking App Style mit Mobile-First Design"""
    st.markdown("""
    <style>
    /* ===== Inter Font ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #0E1117;
    }

    /* ===== Layout: Schlank & Mittig (Mobile App Feel) ===== */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 480px !important; /* Erzwingt schmale Breite */
        margin: 0 auto !important;   /* Zentriert */
    }

    /* ===== Card Styling (Moderner, runder) ===== */
    .st-card {
        background-color: white;
        border-radius: 16px; /* Runder, moderner */
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); /* Weicherer Schatten */
        margin-bottom: 16px;
        border: 1px solid #F3F4F6;
        transition: transform 0.1s, border-color 0.2s;
    }
    .st-card:hover {
        border-color: #E5E7EB;
        transform: translateY(-1px);
    }

    /* ===== Metriken ===== */
    div[data-testid="stMetricValue"] {
        font-size: 26px;
        font-weight: 700;
        color: #111827;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 13px;
        font-weight: 600;
        color: #6B7280;
    }

    /* ===== Buttons (Schwarz/Flach/Abgerundet) ===== */
    .stButton > button {
        background-color: #000000;
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: 600;
        font-size: 14px;
        width: 100%;
        height: 48px;
        margin-top: 8px;
    }
    .stButton > button:hover {
        background-color: #222222;
        color: white;
        border: none;
    }
    
    /* ===== Input Fields ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: #F9FAFB;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        color: #111827;
    }
    
    /* ===== DataFrames ===== */
    [data-testid="stDataFrame"] {
        border: 1px solid #E5E7EB !important;
        border-radius: 12px;
    }
    
    /* ===== Toast Styling ===== */
    div[data-testid="stToast"] {
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

def render_card(title, value, subtext=None, trend=None, icon=None):
    """
    Rendert eine minimalistische HTML Card im Trade Republic Style.
    
    Args:
        title: Titel der Karte (z.B. "Gesamtwert", "Instagram")
        value: Hauptwert (z.B. "12.450 €", "125.5k")
        subtext: Optional - Zusätzlicher Text unter dem Wert (ersetzt description)
        trend: Optional - Trend in Prozent (z.B. 2.4 für +2.4% oder -1.2 für -1.2%)
        icon: Optional - Emoji/Icon für die Karte (z.B. "📸", "💰")
    """
    # Trend Color & Arrow mit Badge-Style
    trend_color = "#10B981" if trend and trend > 0 else "#EF4444" if trend and trend < 0 else "#9CA3AF"
    trend_arrow = "▲" if trend and trend > 0 else "▼" if trend and trend < 0 else "•"
    trend_html = f'<span style="color: {trend_color}; font-size: 13px; font-weight: 600; background: {trend_color}15; padding: 2px 6px; border-radius: 4px;">{trend_arrow} {abs(trend):.1f}%</span>' if trend is not None else ""
    
    # Icon Logik (optional)
    icon_html = f'<span style="font-size: 20px; margin-right: 8px;">{icon}</span>' if icon else ""
    
    # Subtext unter dem Wert
    subtext_html = f'<div style="color: #9CA3AF; font-size: 13px; margin-top: 4px;">{subtext}</div>' if subtext else ""
    
    st.markdown(f"""
        <div class="st-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <h3 style="margin: 0 0 6px 0; font-size: 12px; color: #6B7280; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">{title}</h3>
                    <div style="font-size: 26px; font-weight: 750; color: #111827; display: flex; align-items: center;">
                        {icon_html}{value}
                    </div>
                </div>
                <div style="text-align: right;">
                    {trend_html}
                </div>
            </div>
            {subtext_html}
        </div>
    """, unsafe_allow_html=True)

# =============================================================================
# SUPABASE SETUP
# =============================================================================

@st.cache_resource
def init_supabase():
    """Initialisiere Supabase Client mit Error Handling"""
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"⚠️ Supabase Verbindungsfehler: {e}")
        st.stop()
        return None

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

def format_currency(value):
    """
    Formatiert Zahlen ins deutsche Währungsformat (1.000,00 €).
    
    Args:
        value: Numerischer Wert (int oder float)
    
    Returns:
        Formatierter String (z.B. "1.234,56 €")
    """
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

def format_big_number(num):
    """
    Formatiert große Zahlen kompakt (12.5k, 1.2M).
    
    Args:
        num: Numerischer Wert (int oder float)
    
    Returns:
        Formatierter String (z.B. "12.5k", "1.2M")
    """
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    if num >= 1_000:
        return f"{num/1_000:.1f}k"
    return str(int(num))

def get_deal_status_display(status_db):
    """
    Mappt DB-Status zu deutschem Anzeige-Status für Deals.
    
    Args:
        status_db: Status aus Datenbank (z.B. "In Progress", "Completed")
    
    Returns:
        Deutscher Anzeige-Status (z.B. "In Arbeit", "Bezahlt")
    """
    status_map = {
        'Negotiation': 'Verhandlung',
        'Confirmed': 'Bestätigt',
        'In Progress': 'In Arbeit',
        'Completed': 'Bezahlt',
        'Cancelled': 'Abgesagt'
    }
    return status_map.get(status_db, status_db)

def get_deal_status_color(status_display):
    """
    Gibt Farbe für Deal-Status zurück.
    
    Args:
        status_display: Anzeige-Status (deutsch oder englisch)
    
    Returns:
        Hex-Farbcode (z.B. "#10B981")
    """
    color_map = {
        'Bezahlt': '#10B981',
        'Completed': '#10B981',
        'Bestätigt': '#3B82F6',
        'Confirmed': '#3B82F6',
        'In Arbeit': '#F59E0B',
        'In Progress': '#F59E0B',
        'Verhandlung': '#6B7280',
        'Negotiation': '#6B7280',
        'Abgesagt': '#EF4444',
        'Cancelled': '#EF4444'
    }
    return color_map.get(status_display, '#6B7280')

# =============================================================================
# API INTEGRATION FUNCTIONS
# =============================================================================

def fetch_youtube_stats(channel_id):
    """
    Holt YouTube-Statistiken via YouTube Data API v3.
    
    Args:
        channel_id: YouTube Channel ID (z.B. "UCxxxxxxxxxxxxxxxxxxxxxx")
    
    Returns:
        Dict mit subscribers, view_count, video_count oder None bei Fehler
    """
    if not YOUTUBE_API_AVAILABLE:
        st.error("❌ YouTube API nicht verfügbar. Installiere: pip install google-api-python-client")
        return None
    
    try:
        api_key = st.secrets.get("YOUTUBE_API_KEY")
        if not api_key:
            st.error("❌ YOUTUBE_API_KEY nicht in secrets.toml gefunden")
            return None
        
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        request = youtube.channels().list(
            part='statistics,snippet',
            id=channel_id
        )
        response = request.execute()
        
        if response.get('items'):
            stats = response['items'][0]['statistics']
            snippet = response['items'][0]['snippet']
            
            return {
                "subscribers": int(stats.get('subscriberCount', 0)),
                "view_count": int(stats.get('viewCount', 0)),
                "video_count": int(stats.get('videoCount', 0)),
                "channel_title": snippet.get('title', 'Unknown')
            }
        else:
            st.error(f"❌ Keine Daten für Channel ID: {channel_id}")
            return None
            
    except Exception as e:
        st.error(f"❌ YouTube API Fehler: {e}")
        return None

def update_channel_in_db(platform, handle, value_main, user_id=None):
    """
    Aktualisiert Channel-Werte in der Supabase Datenbank.
    
    Args:
        platform: Plattform-Name (z.B. "YouTube")
        handle: Handle/Username
        value_main: Neuer Wert für value_main
        user_id: Optional - User Email (falls nicht aus session_state)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    supabase = init_supabase()
    if not supabase:
        return False
    
    # Hole User Email
    if user_id is None:
        if "user" not in st.session_state or st.session_state["user"] is None:
            st.error("❌ Nicht eingeloggt")
            return False
        user_id = st.session_state["user"].email
    
    try:
        # Update metric_main auch (formatierte Anzeige)
        metric_main = f"{format_big_number(value_main)} Subscribers" if platform == "YouTube" else f"{format_big_number(value_main)} Follower"
        
        response = supabase.table("channels").update({
            "value_main": value_main,
            "metric_main": metric_main
        }).eq("platform", platform).eq("handle", handle).eq("user_id", user_id).execute()
        
        return True
    except Exception as e:
        st.error(f"❌ Datenbank-Update fehlgeschlagen: {e}")
        return False

def sync_youtube_channel(channel_id, handle):
    """
    Synchronisiert YouTube-Statistiken und aktualisiert die Datenbank.
    
    Args:
        channel_id: YouTube Channel ID
        handle: Handle in der Datenbank
    
    Returns:
        Dict mit Stats oder None bei Fehler
    """
    stats = fetch_youtube_stats(channel_id)
    
    if stats:
        success = update_channel_in_db("YouTube", handle, stats["subscribers"])
        
        if success:
            st.success(f"✅ YouTube-Stats aktualisiert: {format_big_number(stats['subscribers'])} Subscribers")
            return stats
        else:
            st.error("❌ Datenbank-Update fehlgeschlagen")
            return None
    
    return None

def get_assets():
    """
    Holt alle Assets des aktuell eingeloggten Users aus der Datenbank,
    sortiert nach höchstem Wert.
    
    Returns:
        Liste von Asset-Dicts
    """
    supabase = init_supabase()
    if not supabase:
        return []
    
    # Hole User aus Session State
    if "user" not in st.session_state or st.session_state["user"] is None:
        return []
    
    user_id = st.session_state["user"].email
    
    try:
        response = supabase.table("assets") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("current_value", desc=True) \
            .execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Fehler beim Laden der Assets: {e}")
        return []

def get_channels():
    """
    Holt alle Social Media Channels des aktuell eingeloggten Users aus der Datenbank,
    sortiert nach wichtigstem Kanal (höchste Reichweite).
    
    Returns:
        Liste von Channel-Dicts
    """
    supabase = init_supabase()
    if not supabase:
        return []
    
    # Hole User aus Session State
    if "user" not in st.session_state or st.session_state["user"] is None:
        return []
    
    user_id = st.session_state["user"].email
    
    try:
        response = supabase.table("channels") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("value_main", desc=True) \
            .execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Fehler beim Laden der Channels: {e}")
        return []

def get_deals():
    """
    Holt alle Deals/Kooperationen des aktuell eingeloggten Users aus der Datenbank,
    sortiert nach Fälligkeitsdatum (nächste zuerst).
    
    Returns:
        Liste von Deal-Dicts
    """
    supabase = init_supabase()
    if not supabase:
        return []
    
    # Hole User aus Session State
    if "user" not in st.session_state or st.session_state["user"] is None:
        return []
    
    user_id = st.session_state["user"].email
    
    try:
        response = supabase.table("deals") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("due_date", desc=False) \
            .execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Fehler beim Laden der Deals: {e}")
        return []

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
