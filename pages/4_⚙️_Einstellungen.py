"""
CreatorOS - Einstellungen
Account-Einstellungen und Admin Panel
"""

import streamlit as st
import pandas as pd
from utils import (
    check_auth, 
    render_sidebar, 
    init_session_state, 
    save_user_settings,
    get_all_users,
    upgrade_user_to_pro,
    downgrade_user_from_pro,
    ADMIN_EMAIL,
    PAYMENT_LINK
)

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Einstellungen - CreatorOS",
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
# MAIN AREA
# =============================================================================

st.title("⚙️ Einstellungen")
st.write("Verwalte deinen Account und deine Einstellungen")

st.divider()

# =============================================================================
# ACCOUNT SETTINGS
# =============================================================================

st.subheader("👤 Account")

col1, col2 = st.columns(2)

with col1:
    st.text_input("Email", value=user_email, disabled=True)
    
with col2:
    if is_admin:
        st.success("👑 Admin Account")
    elif is_pro:
        st.success("✨ PRO Account")
    else:
        st.info("🆓 FREE Account")

st.divider()

# =============================================================================
# SUBSCRIPTION
# =============================================================================

st.subheader("💎 Subscription")

if is_pro or is_admin:
    st.success("✅ Du hast Zugriff auf alle PRO Features!")
    
    st.write("**PRO Features:**")
    st.write("✅ Unbegrenzte Batch-Verarbeitung")
    st.write("✅ Custom Wasserzeichen-Text")
    st.write("✅ Logo-Upload (Coming Soon)")
    st.write("✅ Prioritäts-Support")
else:
    st.warning("🔒 Du nutzt aktuell den FREE Plan")
    
    st.write("**FREE Limitierungen:**")
    st.write("❌ Nur 1 Bild pro Batch")
    st.write("❌ Fester Wasserzeichen-Text")
    st.write("❌ Kein Logo-Upload")
    
    st.divider()
    
    st.link_button(
        "🚀 Upgrade auf PRO für €X/Monat",
        PAYMENT_LINK,
        use_container_width=True
    )

st.divider()

# =============================================================================
# WATERMARK SETTINGS (Pro Users)
# =============================================================================

if is_pro or is_admin:
    st.subheader("🎨 Standard-Wasserzeichen")
    
    new_watermark_text = st.text_input(
        "Standard-Text",
        value=st.session_state["watermark_text"]
    )
    
    if st.button("💾 Einstellungen speichern", type="primary"):
        st.session_state["watermark_text"] = new_watermark_text
        if save_user_settings(user_email):
            st.success("✅ Einstellungen gespeichert!")
            st.rerun()
    
    st.divider()

# =============================================================================
# ADMIN PANEL
# =============================================================================

if is_admin:
    st.subheader("👑 Admin Panel")
    
    with st.expander("User Management", expanded=True):
        all_users = get_all_users()
        
        if all_users:
            df = pd.DataFrame(all_users)
            
            # Zeige relevante Spalten
            if "email" in df.columns and "is_pro" in df.columns:
                st.dataframe(
                    df[["email", "is_pro", "watermark_text"]],
                    use_container_width=True
                )
            else:
                st.dataframe(df, use_container_width=True)
            
            st.divider()
            
            st.subheader("User Status ändern")
            
            col_input, col_actions = st.columns([2, 1])
            
            with col_input:
                target_email = st.text_input(
                    "User Email",
                    key="admin_target_email",
                    placeholder="user@example.com"
                )
            
            with col_actions:
                st.write("")  # Spacer
                col_up, col_down = st.columns(2)
                
                with col_up:
                    if st.button("⬆️ PRO", use_container_width=True):
                        if target_email:
                            if upgrade_user_to_pro(target_email):
                                st.success(f"✅ {target_email} → PRO!")
                                st.rerun()
                        else:
                            st.warning("⚠️ Email eingeben")
                
                with col_down:
                    if st.button("⬇️ FREE", use_container_width=True):
                        if target_email:
                            if downgrade_user_from_pro(target_email):
                                st.success(f"✅ {target_email} → FREE!")
                                st.rerun()
                        else:
                            st.warning("⚠️ Email eingeben")
            
            st.divider()
            
            # Stats
            total_users = len(all_users)
            pro_users = sum(1 for u in all_users if u.get("is_pro", False))
            free_users = total_users - pro_users
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.metric("Gesamt Users", total_users)
            
            with col_stat2:
                st.metric("PRO Users", pro_users)
            
            with col_stat3:
                st.metric("FREE Users", free_users)
        else:
            st.info("Keine User in der Datenbank gefunden")
    
    st.divider()

# =============================================================================
# DANGER ZONE
# =============================================================================

st.subheader("⚠️ Danger Zone")

with st.expander("Account löschen", expanded=False):
    st.error("**Achtung:** Diese Aktion kann nicht rückgängig gemacht werden!")
    st.write("Account-Löschung ist aktuell noch nicht verfügbar. Kontaktiere den Support.")

st.divider()
st.caption("CreatorOS v10.0 Multi-Page | Made with ❤️ for Creators")

