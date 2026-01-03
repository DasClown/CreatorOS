"""
CreatorOS - Dashboard
Überblick über alle wichtigen KPIs und Channels
"""

import streamlit as st
from utils import (
    inject_custom_css,
    get_channels,
    get_deals,
    render_card,
    format_big_number,
    format_currency,
    get_deal_status_display,
    get_deal_status_color,
    check_auth,
    render_sidebar,
    init_session_state,
    fetch_youtube_stats,
    update_channel_in_db,
    YOUTUBE_API_AVAILABLE
)

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Dashboard - CreatorOS",
    page_icon="🏠",
    layout="centered"
)

# Inject Custom CSS
inject_custom_css()

# =============================================================================
# AUTHENTICATION
# =============================================================================
init_session_state()
user = check_auth()
render_sidebar()

# =============================================================================
# MAIN CONTENT
# =============================================================================

# Header
st.markdown("## Dashboard")
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# Lade Channels aus der Datenbank
channels = get_channels()

# Aggregierte Metriken berechnen
if channels:
    total_audience = sum(c.get('value_main', 0) for c in channels)
    total_revenue = sum(c.get('revenue_mtd', 0) for c in channels)
    avg_growth = sum(c.get('change_24h', 0) for c in channels) / len(channels)
else:
    total_audience = 0
    total_revenue = 0
    avg_growth = 0

# Top KPIs (Audience & Revenue)
col1, col2 = st.columns(2, gap="small")
with col1:
    render_card(
        "Audience",
        format_big_number(total_audience),
        subtext="Gesamtreichweite",
        trend=avg_growth if avg_growth != 0 else None
    )
with col2:
    render_card(
        "Revenue (MTD)",
        format_currency(total_revenue),
        subtext="Brutto Einnahmen"
    )

st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

# Quick Actions
st.markdown("### Quick Actions")
st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

col_a, col_b = st.columns(2, gap="small")
with col_a:
    if st.button("📝 Neuer Post", use_container_width=True):
        st.toast("📝 Post-Planer geöffnet")
with col_b:
    if st.button("💰 Einnahme +", use_container_width=True):
        st.toast("💰 Buchung hinzugefügt")

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# Kanal-Übersicht
st.markdown("### Channels")
st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# Icon Mapping für verschiedene Plattformen
icon_map = {
    "YouTube": "🟥",
    "Instagram": "📸",
    "TikTok": "🎵",
    "LinkedIn": "💼",
    "Newsletter": "📩",
    "OnlyFans": "🔥",
    "Twitter": "🐦",
    "X": "🐦",
    "Facebook": "📘",
    "Snapchat": "👻",
    "Twitch": "🎮"
}

if not channels:
    st.markdown("""
        <div class="st-card" style="text-align: center; padding: 32px 20px;">
            <div style="font-size: 48px; margin-bottom: 16px;">📊</div>
            <h3 style="font-size: 18px; font-weight: 600; margin: 0 0 8px 0; color: #111827;">Noch keine Kanäle</h3>
            <p style="font-size: 14px; color: #6B7280; margin: 0;">Verbinde deine Social Media Accounts</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📝 Anleitung: Kanäle hinzufügen", expanded=True):
        st.markdown("""
        **Via Supabase Dashboard:**
        
        1. Öffne [Supabase Dashboard](https://supabase.com/dashboard)
        2. **Table Editor** → `channels` → **Insert Row**
        3. Fülle die Felder aus:
           - `user_id`: Deine Email
           - `platform`: z.B. "Instagram"
           - `handle`: z.B. "@username"
           - `metric_main`: z.B. "125.5k Follower"
           - `value_main`: 125500
           - `change_24h`: z.B. 2.4 (für +2.4%)
           - `revenue_mtd`: z.B. 1250.50
        
        **Via SQL (Schneller):**
        ```sql
        -- Ersetze mit deiner Email
        INSERT INTO public.channels 
        (user_id, platform, handle, metric_main, value_main, value_label, change_24h, revenue_mtd, platform_icon)
        VALUES 
        ('deine-email@example.com', 'Instagram', '@username', '125.5k Follower', 125500, 'Follower', 2.4, 1250.50, '📸'),
        ('deine-email@example.com', 'YouTube', 'Channel Name', '34.8k Subscribers', 34800, 'Subscribers', 1.8, 2340.00, '📺');
        ```
        """)
else:
    for c in channels:
        platform = c.get('platform', 'Unknown')
        metric_main = c.get('metric_main', f"{c.get('value_main', 0)} {c.get('value_label', '')}")
        value_main = c.get('value_main', 0)
        change_24h = c.get('change_24h', 0)
        revenue = c.get('revenue_mtd', 0)
        
        # Passendes Icon wählen (aus icon_map oder platform_icon aus DB)
        icon = c.get('platform_icon') or icon_map.get(platform, "📱")
        
        # Prozent-Logik für Trend
        trend_color = "#10B981" if change_24h > 0 else "#EF4444" if change_24h < 0 else "#6B7280"
        trend_sign = "+" if change_24h > 0 else ""
        
        # Revenue Badge (optional)
        revenue_badge = f'<span style="background: #10B98115; color: #10B981; font-size: 11px; font-weight: 600; padding: 2px 6px; border-radius: 4px; margin-left: 6px;">{format_currency(revenue)}</span>' if revenue > 0 else ""
        
        # HTML Render für Listen-Element
        st.markdown(f"""
            <div class="st-card" style="display: flex; justify-content: space-between; align-items: center; padding: 16px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="font-size: 24px;">{icon}</div>
                    <div>
                        <div style="font-weight: 600; font-size: 15px; color: #111827;">
                            {platform} {revenue_badge}
                        </div>
                        <div style="color: #9CA3AF; font-size: 12px;">{metric_main}</div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-weight: 700; font-size: 16px; color: #111827;">
                        {format_big_number(value_main)}
                    </div>
                    <div style="font-size: 12px; font-weight: 600; color: {trend_color};">
                        {trend_sign}{change_24h:.1f}%
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-top: 32px; margin-bottom: 16px; border-top: 1px solid #F3F4F6;'></div>", unsafe_allow_html=True)

# Brand Deals Sektion
st.markdown("### Brand Deals")
st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

deals = get_deals()

if not deals:
    st.markdown("""
        <div class="st-card" style="text-align: center; padding: 24px 20px;">
            <div style="font-size: 32px; margin-bottom: 8px;">🤝</div>
            <p style="font-size: 13px; color: #6B7280; margin: 0;">Keine aktiven Deals</p>
        </div>
    """, unsafe_allow_html=True)
else:
    # Zeige nur die nächsten 5 Deals (sortiert nach due_date)
    upcoming_deals = [d for d in deals if d.get('status') not in ['Completed', 'Cancelled']][:5]
    
    if not upcoming_deals:
        st.info("📋 Keine anstehenden Deals")
    else:
        for d in upcoming_deals:
            brand_name = d.get('brand_name', 'Unknown')
            platform = d.get('platform', 'N/A')
            due_date = d.get('due_date', 'N/A')
            amount = d.get('amount', 0)
            status_db = d.get('status', 'Unknown')
            
            # Nutze Utility-Funktionen für Status-Mapping
            status_display = get_deal_status_display(status_db)
            s_color = get_deal_status_color(status_display)
            
            st.markdown(f"""
                <div class="st-card" style="display: flex; justify-content: space-between; align-items: center; padding: 16px; border-left: 4px solid {s_color};">
                    <div>
                        <div style="font-weight: 600; font-size: 15px; color: #111827;">{brand_name}</div>
                        <div style="color: #9CA3AF; font-size: 12px;">{platform} • {due_date}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: 700; font-size: 16px; color: #111827;">{format_currency(amount)}</div>
                        <div style="font-size: 11px; font-weight: 600; color: {s_color}; text-transform: uppercase;">{status_display}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Link zur vollen Deals-Page
        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
        if st.button("📋 Alle Deals anzeigen", use_container_width=True):
            st.switch_page("pages/9_🤝_Deals.py")

st.markdown("<div style='margin-top: 32px; margin-bottom: 16px; border-top: 1px solid #F3F4F6;'></div>", unsafe_allow_html=True)

# Performance Summary
if channels and total_revenue > 0:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #10B98115 0%, #7C3AED15 100%); border-radius: 12px; padding: 16px; border: 1px solid #10B98130;'>
        <div style='font-size: 13px; color: #111827; line-height: 1.6;'>
            <strong>💰 Revenue-Tracking aktiv</strong><br>
            Deine Kanäle generieren <strong>""" + format_currency(total_revenue) + """</strong> MTD.<br>
            <span style="font-size: 12px; color: #6B7280;">Durchschnittliches Wachstum: """ + f"{avg_growth:.1f}%" + """</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style='background: #F9FAFB; border-radius: 12px; padding: 16px; border: 1px solid #F3F4F6;'>
        <div style='font-size: 13px; color: #6B7280; line-height: 1.6;'>
            💡 <strong>Tipp:</strong> Füge das <code>revenue_mtd</code> Feld zu deinen Channels hinzu, um Einnahmen zu tracken.<br>
            📊 Dashboard-Daten werden aus der Supabase <code>channels</code> Tabelle geladen.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar Actions
with st.sidebar:
    st.divider()
    st.markdown("#### 🔄 Daten")
    
    # Social Stats Sync (YouTube API)
    if YOUTUBE_API_AVAILABLE and st.secrets.get("YOUTUBE_API_KEY"):
        if st.button("🔄 Social Stats Sync", use_container_width=True):
            with st.spinner("🔄 Synchronisiere Live-Daten..."):
                # Lade YouTube-Channels
                youtube_channels = [c for c in channels if c.get('platform') == 'YouTube']
                
                if not youtube_channels:
                    st.warning("⚠️ Keine YouTube-Kanäle gefunden")
                else:
                    success_count = 0
                    
                    # Prüfe ob Channel-IDs in notes gespeichert sind
                    for yt_channel in youtube_channels:
                        handle = yt_channel.get('handle', '')
                        notes = yt_channel.get('notes', '')
                        
                        # Suche Channel ID in notes (Format: "channel_id:UCxxxxxx" oder einfach "UCxxxxxx")
                        channel_id = None
                        if notes and 'UC' in notes:
                            # Extrahiere Channel ID aus notes
                            parts = notes.split()
                            for part in parts:
                                if part.startswith('UC') and len(part) == 24:
                                    channel_id = part
                                    break
                                elif 'channel_id:' in part.lower():
                                    channel_id = part.split(':')[-1]
                                    break
                        
                        if channel_id:
                            # Synchronisiere
                            yt_data = fetch_youtube_stats(channel_id)
                            if yt_data:
                                success = update_channel_in_db("YouTube", handle, yt_data['subscribers'])
                                if success:
                                    success_count += 1
                        else:
                            st.info(f"ℹ️ {handle}: Füge Channel ID zu Notizen hinzu")
                    
                    if success_count > 0:
                        st.success(f"✅ {success_count} YouTube-Kanal(e) synchronisiert!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Keine YouTube-Kanäle mit Channel ID gefunden")
    
    # Standard Reload
    if st.button("🔄 Seite neu laden", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()
    
    # YouTube Channel ID Setup (Hilfe)
    if YOUTUBE_API_AVAILABLE and st.secrets.get("YOUTUBE_API_KEY"):
        with st.expander("ℹ️ YouTube-Sync einrichten"):
            st.markdown("""
            **So richtest du den Sync ein:**
            
            1. Finde deine YouTube Channel ID:
               - Gehe zu `youtube.com/@yourhandle`
               - Klicke auf den Kanal
               - URL wird zu `youtube.com/channel/UCxxxxxx`
            
            2. Füge die Channel ID hinzu:
               - Gehe zu **📊 Channels**
               - Suche deinen YouTube-Kanal
               - Füge die Channel ID zu den **Notizen** hinzu
               - Format: `UCxxxxxxxxxxxxxxxxxxxxxx`
            
            3. Klicke dann hier auf **🔄 Social Stats Sync**
            
            **Oder nutze die manuelle Sync-Funktion:**
            - Gehe zu **📊 Channels**
            - Scrolle zu **🔄 API-Sync**
            """)
    elif not st.secrets.get("YOUTUBE_API_KEY"):
        with st.expander("ℹ️ YouTube API einrichten"):
            st.markdown("""
            **Aktiviere automatischen Sync:**
            
            1. Erstelle einen YouTube API-Key:
               - [Google Cloud Console](https://console.cloud.google.com/)
               - YouTube Data API v3 aktivieren
               - API-Key erstellen
            
            2. Füge den Key zu `secrets.toml` hinzu:
               ```toml
               YOUTUBE_API_KEY = "dein-key-hier"
               ```
            
            3. Lies die vollständige Anleitung:
               - Siehe `API_INTEGRATION.md`
            """)

