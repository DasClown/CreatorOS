"""
CreatorOS - Main Entry Point
Landing Page & Dashboard
"""

import streamlit as st
from utils import check_auth, render_sidebar, init_session_state

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="CreatorOS - Dashboard",
    page_icon="🎯",
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
# MAIN DASHBOARD
# =============================================================================

st.title("🎯 CreatorOS Dashboard")
st.write(f"Willkommen zurück, **{user_email}**!")

st.divider()

# High-Level KPIs
st.subheader("📊 Übersicht")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="👥 Fans",
        value="0",
        delta="Coming Soon"
    )

with col2:
    st.metric(
        label="💰 Revenue",
        value="€0",
        delta="Coming Soon"
    )

with col3:
    st.metric(
        label="🎨 Content",
        value="0",
        delta="Coming Soon"
    )

with col4:
    st.metric(
        label="📈 Engagement",
        value="0%",
        delta="Coming Soon"
    )

st.divider()

# Navigation Hints
st.subheader("🚀 Quick Actions")

col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    st.info("**💎 CRM**\n\nVerwalte deine Fans und Kunden")
    if st.button("Zum CRM →", use_container_width=True):
        st.switch_page("pages/1_💎_CRM.py")

with col_nav2:
    st.info("**🎨 Content Factory**\n\nBilder verarbeiten & Wasserzeichen")
    if st.button("Zur Content Factory →", use_container_width=True):
        st.switch_page("pages/3_🎨_Content_Factory.py")

with col_nav3:
    st.info("**⚙️ Einstellungen**\n\nAccount & Admin Panel")
    if st.button("Zu Einstellungen →", use_container_width=True):
        st.switch_page("pages/4_⚙️_Einstellungen.py")

st.divider()

# Recent Activity
st.subheader("📝 Letzte Aktivitäten")
st.info("🔜 Hier werden bald deine letzten Aktionen angezeigt")

st.divider()

# Status & Help
st.subheader("💡 Status")

if is_pro or is_admin:
    st.success("✨ **PRO Account** - Du hast Zugriff auf alle Features!")
else:
    st.warning("🔒 **FREE Account** - Upgrade für unbegrenzte Nutzung!")

st.divider()
st.caption("CreatorOS v10.0 Multi-Page | Made with ❤️ for Creators")

