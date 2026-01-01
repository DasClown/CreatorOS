"""
CreatorOS - Settings & Account
Einstellungen und Admin-Bereich
"""

import streamlit as st
import pandas as pd
from utils import check_auth, render_sidebar, init_session_state, init_supabase, logout, ADMIN_EMAIL, PAYMENT_LINK

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Settings - CreatorOS",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# AUTHENTICATION
# =============================================================================
init_session_state()
user = check_auth()

# =============================================================================
# SIDEBAR
# =============================================================================
user_email, is_pro, is_admin = render_sidebar()

# =============================================================================
# SUPABASE CLIENT
# =============================================================================
supabase = init_supabase()

# =============================================================================
# MAIN AREA
# =============================================================================

st.title("⚙️ Einstellungen & Account")
st.write("Verwalte deinen Account und deine Einstellungen")

st.divider()

# =============================================================================
# SEKTION 1: MEIN PROFIL
# =============================================================================

st.subheader("👤 Mein Profil")

col_profile1, col_profile2 = st.columns([2, 1])

with col_profile1:
    st.write("**Email:**")
    st.code(user_email)
    
    st.write("**Status:**")
    if is_pro or is_admin:
        st.success("🟢 PRO Mitglied")
        st.write("Du hast Zugriff auf alle Features:")
        st.write("✅ Unbegrenzte Batch-Verarbeitung")
        st.write("✅ Custom Wasserzeichen-Text")
        st.write("✅ Alle CRM & Finance Features")
        st.write("✅ Unbegrenzte Tasks")
    else:
        st.info("⚪ Free Plan")
        st.write("**Aktuelle Limitierungen:**")
        st.write("❌ Nur 1 Bild pro Batch")
        st.write("❌ Fester Wasserzeichen-Text")
        st.write("✅ CRM & Finance unbegrenzt")
        st.write("✅ Tasks unbegrenzt")

with col_profile2:
    if is_admin:
        st.error("👑 **ADMIN**\n\nDu hast Admin-Rechte")
    elif is_pro:
        st.success("✨ **PRO**\n\nAlle Features freigeschaltet")
    else:
        st.warning("🆓 **FREE**\n\nUpgrade für mehr Features")

st.divider()

# Upgrade für Free User
if not is_pro and not is_admin:
    st.subheader("🚀 Upgrade auf PRO")
    
    col_upgrade1, col_upgrade2 = st.columns([2, 1])
    
    with col_upgrade1:
        st.write("**PRO Vorteile:**")
        st.write("✨ Unbegrenzte Batch-Verarbeitung")
        st.write("✨ Custom Wasserzeichen-Text")
        st.write("✨ Logo-Upload (Coming Soon)")
        st.write("✨ Prioritäts-Support")
        st.write("✨ Keine Limitierungen")
    
    with col_upgrade2:
        st.metric("Preis", "€XX/Monat")
        st.link_button(
            "🚀 Jetzt upgraden",
            PAYMENT_LINK,
            use_container_width=True,
            type="primary"
        )
    
    st.divider()

# Logout
st.subheader("🚪 Abmelden")

if st.button("Ausloggen", type="secondary", use_container_width=False):
    logout()

st.divider()

# =============================================================================
# SEKTION 2: ADMIN BEREICH
# =============================================================================

if user_email == ADMIN_EMAIL:
    st.subheader("👑 Admin Dashboard")
    
    st.info("**Du bist als Admin eingeloggt.** Du kannst alle User verwalten und PRO-Status vergeben.")
    
    with st.expander("🔧 User Management", expanded=True):
        # Lade alle User
        try:
            response = supabase.table("user_settings").select("*").execute()
            
            if response.data:
                df_users = pd.DataFrame(response.data)
                
                # Zeige User-Tabelle
                st.write("**Alle User:**")
                
                # Wähle relevante Spalten
                display_columns = ['email', 'is_pro', 'watermark_text']
                
                # Stelle sicher, dass Spalten existieren
                for col in display_columns:
                    if col not in df_users.columns:
                        if col == 'is_pro':
                            df_users[col] = False
                        else:
                            df_users[col] = ""
                
                df_display = df_users[display_columns].copy()
                
                # Formatiere is_pro als Text
                df_display['is_pro'] = df_display['is_pro'].apply(lambda x: '✅ PRO' if x else '⚪ FREE')
                
                # Rename für bessere Lesbarkeit
                df_display = df_display.rename(columns={
                    'email': 'Email',
                    'is_pro': 'Status',
                    'watermark_text': 'Wasserzeichen'
                })
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                st.divider()
                
                # Stats
                st.write("**Statistiken:**")
                
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                
                total_users = len(df_users)
                pro_users = df_users['is_pro'].sum() if 'is_pro' in df_users.columns else 0
                free_users = total_users - pro_users
                
                with col_stat1:
                    st.metric("Gesamt Users", total_users)
                
                with col_stat2:
                    st.metric("PRO Users", pro_users)
                
                with col_stat3:
                    st.metric("FREE Users", free_users)
                
                st.divider()
                
                # Upgrade Interface
                st.subheader("⚡ User Status ändern")
                
                col_upgrade_input, col_upgrade_actions = st.columns([2, 1])
                
                with col_upgrade_input:
                    target_email = st.text_input(
                        "User Email",
                        placeholder="user@example.com",
                        key="admin_upgrade_email"
                    )
                
                with col_upgrade_actions:
                    st.write("")  # Spacer
                    st.write("")  # Spacer
                    
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("⬆️ PRO", use_container_width=True):
                            if target_email:
                                try:
                                    # Update to PRO
                                    supabase.table("user_settings").update({
                                        "is_pro": True
                                    }).eq("email", target_email).execute()
                                    
                                    st.success(f"✅ {target_email} ist jetzt PRO!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Fehler: {str(e)}")
                            else:
                                st.warning("⚠️ Bitte Email eingeben")
                    
                    with col_btn2:
                        if st.button("⬇️ FREE", use_container_width=True):
                            if target_email:
                                try:
                                    # Downgrade to FREE
                                    supabase.table("user_settings").update({
                                        "is_pro": False
                                    }).eq("email", target_email).execute()
                                    
                                    st.success(f"✅ {target_email} ist jetzt FREE!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Fehler: {str(e)}")
                            else:
                                st.warning("⚠️ Bitte Email eingeben")
            else:
                st.info("Noch keine User in der Datenbank")
        
        except Exception as e:
            st.error(f"Fehler beim Laden der User: {str(e)}")
    
    st.divider()

# =============================================================================
# SEKTION 3: RECHTLICHES
# =============================================================================

st.subheader("📄 Rechtliches")

with st.expander("📜 Impressum"):
    st.markdown("""
    **Angaben gemäß § 5 TMG:**

    CreatorDeck / Janick Thum  
    [Deine Adresse hier]  
    [PLZ Stadt]  
    [Land]

    **Kontakt:**  
    E-Mail: janick@icanhasbucket.de  
    Telefon: [Deine Telefonnummer]

    **Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV:**  
    Janick Thum  
    [Adresse]

    **Haftung für Inhalte:**  
    Die Inhalte unserer Seiten wurden mit größter Sorgfalt erstellt. Für die Richtigkeit, Vollständigkeit und Aktualität der Inhalte können wir jedoch keine Gewähr übernehmen.

    **Haftung für Links:**  
    Unser Angebot enthält Links zu externen Webseiten Dritter, auf deren Inhalte wir keinen Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen.

    **Urheberrecht:**  
    Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht.
    """)

with st.expander("🔒 Datenschutzerklärung"):
    st.markdown("""
    **Datenschutzerklärung für CreatorDeck**

    **1. Datenerhebung und -verarbeitung**

    Wir erheben nur die für die Nutzung der App notwendigen Daten:
    - E-Mail-Adresse (für Authentifizierung)
    - Passwort (verschlüsselt gespeichert)
    - Von Ihnen eingegebene Daten (Fans, Finanzen, Tasks)

    **2. Verwendungszweck**

    Ihre Daten werden ausschließlich für folgende Zwecke verwendet:
    - Bereitstellung der App-Funktionalität
    - Speicherung Ihrer persönlichen Einstellungen
    - Verwaltung Ihres Accounts

    **3. Datenspeicherung**

    Ihre Daten werden auf Servern von Supabase (USA/EU) gespeichert.  
    Weitere Informationen: https://supabase.com/privacy

    **4. Bildverarbeitung**

    Hochgeladene Bilder werden:
    - Nur temporär im RAM verarbeitet
    - Niemals dauerhaft gespeichert
    - Niemals an Dritte weitergegeben
    - Sofort nach der Verarbeitung gelöscht

    **5. Cookies und Tracking**

    Wir verwenden:
    - Session-Cookies für die Authentifizierung
    - Keine Tracking-Cookies
    - Keine Analyse-Tools (außer Supabase-eigene Logs)

    **6. Ihre Rechte**

    Sie haben jederzeit das Recht auf:
    - Auskunft über Ihre gespeicherten Daten
    - Berichtigung unrichtiger Daten
    - Löschung Ihrer Daten
    - Einschränkung der Verarbeitung
    - Datenübertragbarkeit

    **7. Datenweitergabe**

    Wir geben Ihre Daten nicht an Dritte weiter, außer:
    - Es besteht eine gesetzliche Verpflichtung
    - Sie haben ausdrücklich zugestimmt

    **8. Datensicherheit**

    Wir verwenden moderne Sicherheitsmaßnahmen:
    - SSL/TLS-Verschlüsselung
    - Passwort-Hashing (bcrypt)
    - Row Level Security (RLS) in der Datenbank
    - Regelmäßige Sicherheits-Updates

    **9. Änderungen der Datenschutzerklärung**

    Wir behalten uns vor, diese Datenschutzerklärung anzupassen, um sie an geänderte Rechtslage oder bei Änderungen der App anzupassen.

    **10. Kontakt**

    Bei Fragen zum Datenschutz:  
    E-Mail: janick@icanhasbucket.de

    **Stand:** Januar 2025
    """)

st.divider()

# =============================================================================
# DANGER ZONE (Optional)
# =============================================================================

st.subheader("⚠️ Danger Zone")

with st.expander("🗑️ Account löschen", expanded=False):
    st.error("**Achtung:** Diese Aktion kann nicht rückgängig gemacht werden!")
    st.write("Wenn du deinen Account löschst, werden alle deine Daten unwiderruflich gelöscht:")
    st.write("- Alle Fans aus dem CRM")
    st.write("- Alle Finanz-Einträge")
    st.write("- Alle Tasks")
    st.write("- Alle Einstellungen")
    
    st.divider()
    
    st.write("**Account-Löschung ist aktuell noch nicht verfügbar.**")
    st.write("Bitte kontaktiere den Support: janick@icanhasbucket.de")
    
    # Future Implementation:
    # confirm_email = st.text_input("Bestätige deine Email", placeholder=user_email)
    # if st.button("🗑️ Account unwiderruflich löschen", type="secondary"):
    #     if confirm_email == user_email:
    #         # Delete all user data
    #         # Delete from fans, finance_entries, tasks, user_settings
    #         # Sign out
    #         pass

st.divider()
st.caption("CreatorOS v10.0 Multi-Page | Made with ❤️ for Creators")

