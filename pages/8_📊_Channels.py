"""
CreatorOS - Social Media Channels
Übersicht über alle Social Media Kanäle mit Reichweite & Performance
"""

import streamlit as st
from utils import (
    inject_custom_css,
    init_supabase,
    render_card,
    get_channels,
    format_big_number,
    check_auth,
    render_sidebar,
    init_session_state,
    fetch_youtube_stats,
    sync_youtube_channel,
    YOUTUBE_API_AVAILABLE
)

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Channels - CreatorOS",
    page_icon="📊",
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
st.markdown("## Social Media Channels")
st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# Lade Channels aus der Datenbank
channels = get_channels()

# Berechnungen
total_reach = sum(ch.get('value_main', 0) for ch in channels) if channels else 0
avg_engagement = sum(ch.get('engagement_rate', 0) for ch in channels) / len(channels) if channels else 0

# Top Stats
col1, col2 = st.columns(2, gap="small")
with col1:
    render_card(
        "Gesamt-Reichweite",
        format_big_number(total_reach),
        subtext="über alle Plattformen",
        icon="🌐"
    )
with col2:
    render_card(
        "Ø Engagement",
        f"{avg_engagement:.1f}%",
        subtext=f"{len(channels)} Kanäle aktiv",
        icon="❤️"
    )

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# Channel Liste
st.markdown("### Deine Plattformen")
st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

if not channels:
    st.markdown("""
        <div class="st-card" style="text-align: center; padding: 32px 20px;">
            <div style="font-size: 48px; margin-bottom: 16px;">📊</div>
            <h3 style="font-size: 18px; font-weight: 600; margin: 0 0 8px 0; color: #111827;">Noch keine Kanäle</h3>
            <p style="font-size: 14px; color: #6B7280; margin: 0;">Füge deine ersten Social Media Accounts hinzu</p>
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
           - `value_main`: Follower-Zahl (z.B. 125500)
           - `value_label`: "Follower" oder "Subscribers"
           - `engagement_rate`: z.B. 3.8
           - `growth_30d`: z.B. 12.4 (für +12.4%)
           - `platform_icon`: Emoji (z.B. "📸")
        
        **Via SQL (Schneller):**
        ```sql
        -- Ersetze mit deiner Email
        INSERT INTO public.channels 
        (user_id, platform, handle, value_main, value_label, engagement_rate, growth_30d, platform_icon, is_primary)
        VALUES 
        ('deine-email@example.com', 'Instagram', '@username', 125500, 'Follower', 3.8, 12.4, '📸', true),
        ('deine-email@example.com', 'TikTok', '@username', 89200, 'Follower', 5.2, 22.3, '🎵', false);
        ```
        """)
else:
    for channel in channels:
        platform = channel.get('platform', 'Unknown')
        handle = channel.get('handle', '')
        value_main = channel.get('value_main', 0)
        value_label = channel.get('value_label', 'Follower')
        engagement = channel.get('engagement_rate', 0)
        growth = channel.get('growth_30d', 0)
        icon = channel.get('platform_icon', '📱')
        is_primary = channel.get('is_primary', False)
        
        # Primary Badge
        primary_badge = '<span style="background: #7C3AED; color: white; font-size: 11px; font-weight: 600; padding: 2px 6px; border-radius: 4px; margin-left: 8px;">PRIMARY</span>' if is_primary else ""
        
        # Growth Badge
        growth_color = "#10B981" if growth > 0 else "#EF4444" if growth < 0 else "#9CA3AF"
        growth_arrow = "▲" if growth > 0 else "▼" if growth < 0 else "•"
        
        st.markdown(f"""
            <div class="st-card" style="padding: 18px;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; margin-bottom: 4px;">
                            <span style="font-size: 24px; margin-right: 8px;">{icon}</span>
                            <div>
                                <div style="font-weight: 700; font-size: 16px; color: #111827;">
                                    {platform} {primary_badge}
                                </div>
                                <div style="font-size: 13px; color: #9CA3AF;">{handle}</div>
                            </div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 20px; font-weight: 700; color: #111827;">
                            {format_big_number(value_main)}
                        </div>
                        <div style="font-size: 12px; color: #6B7280;">{value_label}</div>
                    </div>
                </div>
                
                <div style="display: flex; gap: 12px; padding-top: 12px; border-top: 1px solid #F3F4F6;">
                    <div style="flex: 1;">
                        <div style="font-size: 11px; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">Engagement</div>
                        <div style="font-size: 15px; font-weight: 600; color: #111827;">{engagement}%</div>
                    </div>
                    <div style="flex: 1; text-align: right;">
                        <div style="font-size: 11px; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">30d Growth</div>
                        <div style="font-size: 15px; font-weight: 600; color: {growth_color};">
                            {growth_arrow} {abs(growth):.1f}%
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-top: 32px; margin-bottom: 16px; border-top: 1px solid #F3F4F6;'></div>", unsafe_allow_html=True)

# Insights & Tipps
st.markdown("""
<div style='background: #F9FAFB; border-radius: 12px; padding: 16px; border: 1px solid #F3F4F6;'>
    <div style='font-size: 13px; color: #6B7280; line-height: 1.6;'>
        💡 <strong>Tipp:</strong> Verknüpfe deine Kanäle mit APIs für automatische Updates:<br>
        • <strong>Instagram:</strong> Instagram Graph API<br>
        • <strong>YouTube:</strong> YouTube Data API v3<br>
        • <strong>TikTok:</strong> TikTok For Developers<br>
        📊 Channel-Daten werden aus der Supabase <code>channels</code> Tabelle geladen.
    </div>
</div>
""", unsafe_allow_html=True)

# API-Sync Sektion
if channels and YOUTUBE_API_AVAILABLE:
    st.markdown("<div style='margin-top: 32px; margin-bottom: 16px; border-top: 1px solid #F3F4F6;'></div>", unsafe_allow_html=True)
    
    st.markdown("### 🔄 API-Sync")
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    
    with st.expander("YouTube-Statistiken aktualisieren", expanded=False):
        st.markdown("""
        **YouTube Data API v3**
        
        Synchronisiere automatisch deine Subscriber-Zahlen und Stats.
        """)
        
        youtube_channels = [c for c in channels if c.get('platform') == 'YouTube']
        
        if not youtube_channels:
            st.info("Keine YouTube-Kanäle gefunden")
        else:
            for yt_channel in youtube_channels:
                handle = yt_channel.get('handle', '')
                current_subs = yt_channel.get('value_main', 0)
                
                st.markdown(f"**{handle}**")
                st.caption(f"Aktuell: {format_big_number(current_subs)} Subscribers")
                
                col_input, col_sync = st.columns([3, 1])
                with col_input:
                    channel_id = st.text_input(
                        "YouTube Channel ID",
                        key=f"yt_id_{handle}",
                        placeholder="UCxxxxxxxxxxxxxxxxxxxxxx",
                        label_visibility="collapsed"
                    )
                with col_sync:
                    if st.button("🔄 Sync", key=f"sync_{handle}", use_container_width=True):
                        if channel_id:
                            with st.spinner("Syncing..."):
                                stats = sync_youtube_channel(channel_id, handle)
                                if stats:
                                    st.rerun()
                        else:
                            st.error("❌ Channel ID eingeben")
                
                st.divider()

# Sidebar Actions
with st.sidebar:
    st.divider()
    st.markdown("#### 🔄 Daten")
    if st.button("🔄 Neu laden", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

