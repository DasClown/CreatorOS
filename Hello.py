import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
from supabase import create_client, Client

# --- KONFIGURATION ---
st.set_page_config(page_title="CreatorDeck", page_icon="🚀", layout="wide")

# --- SUPABASE CLIENT ---
@st.cache_resource
def init_supabase() -> Client:
    """Initialisiert den Supabase Client."""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Supabase Verbindungsfehler: {e}")
        return None

supabase = init_supabase()

# --- HILFSFUNKTIONEN ---
def get_instagram_followers():
    """Ruft die Follower-Zahl von der Instagram Graph API ab."""
    try:
        if "INSTAGRAM_ACCESS_TOKEN" in st.secrets and "INSTAGRAM_ACCOUNT_ID" in st.secrets:
            token = st.secrets["INSTAGRAM_ACCESS_TOKEN"]
            id = st.secrets["INSTAGRAM_ACCOUNT_ID"]
            url = f"https://graph.facebook.com/v18.0/{id}?fields=followers_count&access_token={token}"
            response = requests.get(url).json()
            if 'error' in response:
                st.error(f"API Fehler: {response['error']['message']}")
                return 0
            return response.get('followers_count', 0)
        else:
            return 0
    except Exception as e:
        st.error(f"Verbindungsfehler: {e}")
        return 0

def get_recent_media():
    """Ruft die letzten 3 Instagram-Posts von der Graph API ab."""
    try:
        if "INSTAGRAM_ACCESS_TOKEN" in st.secrets and "INSTAGRAM_ACCOUNT_ID" in st.secrets:
            token = st.secrets["INSTAGRAM_ACCESS_TOKEN"]
            account_id = st.secrets["INSTAGRAM_ACCOUNT_ID"]
            url = f"https://graph.facebook.com/v18.0/{account_id}/media"
            params = {
                "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,like_count,comments_count,timestamp",
                "limit": 3,
                "access_token": token
            }
            response = requests.get(url, params=params).json()
            
            if 'error' in response:
                st.error(f"API Fehler: {response['error']['message']}")
                return []
            
            return response.get('data', [])
        else:
            return []
    except Exception as e:
        st.error(f"Verbindungsfehler: {e}")
        return []

def load_content_from_supabase() -> pd.DataFrame:
    """Lädt Content-Daten aus Supabase."""
    if not supabase:
        return pd.DataFrame()
    
    try:
        response = supabase.table('content_plan').select("*").order('datum', desc=True).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            # Konvertiere Datum-Strings zu date-Objekten
            if 'datum' in df.columns:
                df['datum'] = pd.to_datetime(df['datum']).dt.date
            # Rename columns to match UI (capitalize)
            df = df.rename(columns={
                'id': 'ID',
                'datum': 'Datum',
                'titel': 'Titel',
                'format': 'Format',
                'status': 'Status',
                'notizen': 'Notizen'
            })
            return df
        else:
            return pd.DataFrame(columns=['ID', 'Datum', 'Titel', 'Format', 'Status', 'Notizen'])
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        return pd.DataFrame(columns=['ID', 'Datum', 'Titel', 'Format', 'Status', 'Notizen'])

def init_session_state():
    """Initialisiert die Datenbank im Session State - lädt aus Supabase."""
    if 'content_df' not in st.session_state:
        st.session_state['content_df'] = load_content_from_supabase()

def check_password():
    """Prüft das Passwort und gibt nur bei korrekter Eingabe Zugriff."""
    # Prüfe, ob bereits verifiziert
    if st.session_state.get('password_correct', False):
        return True
    
    # Zeige Login-Screen
    st.title("🔒 CreatorDeck Login")
    st.markdown("Bitte gib den Zugangscode ein, um fortzufahren.")
    
    password = st.text_input("Zugangscode", type="password", key="password_input")
    
    if st.button("Anmelden", type="primary"):
        # Prüfe Passwort
        if "APP_PASSWORD" in st.secrets and password == st.secrets["APP_PASSWORD"]:
            st.session_state['password_correct'] = True
            st.success("✅ Zugriff gewährt!")
            st.rerun()
        else:
            st.error("❌ Zugriff verweigert - Falscher Zugangscode")
            st.stop()
    else:
        st.stop()
    
    return False

# --- HAUPTPROGRAMM ---
def main():
    # Passwort-Schutz als erstes prüfen
    check_password()
    
    st.title("🚀 CreatorDeck")
    
    init_session_state()
    
    # 1. TABS ERSTELLEN
    tab_cockpit, tab_planner, tab_settings = st.tabs(["📊 Cockpit", "🗓️ Content Planer", "⚙️ Einstellungen"])

    # --- TAB 1: COCKPIT ---
    with tab_cockpit:
        st.header("Performance Übersicht")
        
        col1, col2, col3 = st.columns(3)
        
        # Instagram Stats (Live Data)
        followers = get_instagram_followers()
        
        with col1:
            st.metric(label="Instagram Follower", value=f"{followers:,}")
        
        with col2:
            # Beispiel für statische/berechnete Metrik aus dem Planer
            df = st.session_state['content_df']
            planned_count = len(df[df['Status'] == 'Ready']) if not df.empty else 0
            st.metric(label="Beiträge Ready", value=planned_count)
        
        with col3:
            # Gesamt Content-Ideen
            total_ideas = len(st.session_state['content_df'])
            st.metric(label="Content-Ideen", value=total_ideas)
        
        st.divider()
        
        # Visual Analytics
        st.subheader("📊 Content Pipeline Analytics")
        
        df = st.session_state['content_df']
        
        if not df.empty:
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown("**Status-Verteilung**")
                # Gruppiere nach Status und zähle
                status_counts = df['Status'].value_counts()
                st.bar_chart(status_counts)
            
            with c2:
                st.markdown("**Format-Verteilung**")
                # Gruppiere nach Format und zähle
                format_counts = df['Format'].value_counts()
                st.bar_chart(format_counts)
        else:
            st.info("📭 Noch keine Daten für Grafiken vorhanden.")
        
        st.divider()
        
        # Live Media Feed
        st.subheader("📸 Neueste Posts")
        
        recent_posts = get_recent_media()
        
        if recent_posts and len(recent_posts) > 0:
            cols = st.columns(3)
            
            for idx, post in enumerate(recent_posts):
                with cols[idx]:
                    # Bestimme die richtige Bild-URL
                    if post.get('media_type') == 'VIDEO':
                        image_url = post.get('thumbnail_url', '')
                    else:
                        image_url = post.get('media_url', '')
                    
                    # Zeige das Bild
                    if image_url:
                        st.image(image_url, use_container_width=True)
                    
                    # Metriken
                    likes = post.get('like_count', 0)
                    comments = post.get('comments_count', 0)
                    st.markdown(f"❤️ **{likes:,}** | 💬 **{comments:,}**")
                    
                    # Caption (gekürzt)
                    caption = post.get('caption', 'Kein Text')
                    if len(caption) > 50:
                        caption = caption[:50] + '...'
                    st.caption(caption)
                    
                    # Link zum Post
                    permalink = post.get('permalink', '')
                    if permalink:
                        st.link_button("Auf Insta ansehen", permalink, use_container_width=True)
        else:
            st.info("📭 Keine Posts gefunden oder API-Limit erreicht.")

    # --- TAB 2: CONTENT PLANER ---
    with tab_planner:
        st.header("Content Planung")
        
        # UI Komponente C: Quick Stats
        df = st.session_state['content_df']
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Offene Ideen", len(df[df['Status'] == 'Idee']) if not df.empty else 0)
        m_col2.metric("In Arbeit (Drafts)", len(df[df['Status'] == 'Draft']) if not df.empty else 0)
        m_col3.metric("Gesamt", len(df))
        
        st.divider()

        # UI Komponente A: Eingabe (Neue Idee)
        with st.expander("➕ Neue Idee erfassen", expanded=False):
            with st.form("new_post_form"):
                c1, c2 = st.columns(2)
                with c1:
                    new_title = st.text_input("Titel / Thema")
                    new_date = st.date_input("Geplantes Datum", date.today())
                with c2:
                    new_format = st.selectbox("Format", ["Reel", "Post", "Carousel", "Story"])
                    new_status = st.selectbox("Status", ["Idee", "Draft", "Ready", "Published"])
                
                new_notes = st.text_area("Notizen / Skript")
                
                submitted = st.form_submit_button("Speichern")
                
                if submitted and supabase:
                    if not new_title:
                        st.error("⚠️ Bitte gib einen Titel ein!")
                    else:
                        # Erstelle neuen Eintrag für Supabase
                        new_data = {
                            'datum': new_date.isoformat(),
                            'titel': new_title,
                            'format': new_format,
                            'status': new_status,
                            'notizen': new_notes
                        }
                        
                        try:
                            # Insert in Supabase
                            response = supabase.table('content_plan').insert(new_data).execute()
                            st.success(f"✅ Idee '{new_title}' wurde gespeichert!")
                            # Reload data
                            st.session_state['content_df'] = load_content_from_supabase()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Fehler beim Speichern: {e}")

        # UI Komponente B: Übersicht (Data Editor)
        st.subheader("Aktuelle Planung")
        
        if not df.empty:
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "ID": st.column_config.NumberColumn(
                        "ID",
                        disabled=True,
                        width="small"
                    ),
                    "Format": st.column_config.SelectboxColumn(
                        "Format",
                        help="Das Format des Beitrags",
                        width="medium",
                        options=["Reel", "Post", "Carousel", "Story"],
                        required=True,
                    ),
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        width="medium",
                        options=["Idee", "Draft", "Ready", "Published"],
                        required=True,
                    ),
                    "Datum": st.column_config.DateColumn(
                        "Datum",
                        format="DD.MM.YYYY",
                    ),
                },
                hide_index=True,
                key="content_editor"
            )
            
            # Sync Button
            if st.button("💾 Änderungen synchronisieren", type="primary", use_container_width=True):
                if supabase:
                    try:
                        # Iteriere durch edited_df und update in Supabase
                        for _, row in edited_df.iterrows():
                            update_data = {
                                'datum': row['Datum'].isoformat() if isinstance(row['Datum'], date) else row['Datum'],
                                'titel': row['Titel'],
                                'format': row['Format'],
                                'status': row['Status'],
                                'notizen': row['Notizen']
                            }
                            
                            # Upsert basierend auf ID
                            supabase.table('content_plan').update(update_data).eq('id', row['ID']).execute()
                        
                        st.success("✅ Alle Änderungen wurden synchronisiert!")
                        st.session_state['content_df'] = load_content_from_supabase()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Fehler beim Synchronisieren: {e}")
        else:
            st.info("📭 Noch keine Content-Ideen vorhanden. Erstelle deine erste Idee oben!")

    # --- TAB 3: EINSTELLUNGEN ---
    with tab_settings:
        st.header("Einstellungen")
        st.info("🚧 Dieser Bereich ist in Entwicklung.")
        
        with st.expander("API Konfiguration"):
            st.markdown("""
            **Instagram Graph API**
            
            Füge deine Credentials in `.streamlit/secrets.toml` hinzu:
            ```toml
            INSTAGRAM_ACCESS_TOKEN = "dein_token"
            INSTAGRAM_ACCOUNT_ID = "deine_id"
            ```
            
            **Supabase Database**
            
            ```toml
            [supabase]
            url = "https://dein-projekt.supabase.co"
            key = "dein_anon_key"
            ```
            """)
        
        with st.expander("🔄 Daten neu laden"):
            if st.button("Daten aus Supabase neu laden"):
                st.session_state['content_df'] = load_content_from_supabase()
                st.success("✅ Daten wurden neu geladen!")
                st.rerun()

if __name__ == "__main__":
    main()
