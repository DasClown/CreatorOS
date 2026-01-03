"""
CreatorOS - Deals & Collaborations
Management von Brand Deals, Sponsorings und Kooperationen
"""

import streamlit as st
from utils import (
    inject_custom_css,
    init_supabase,
    render_card,
    get_deals,
    format_currency,
    get_deal_status_display,
    get_deal_status_color,
    check_auth,
    render_sidebar,
    init_session_state
)
from datetime import datetime, date

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Deals - CreatorOS",
    page_icon="🤝",
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
st.markdown("## Deals & Collaborations")
st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# Lade Deals aus der Datenbank
deals = get_deals()

# Berechnungen
if deals:
    total_value = sum(d.get('amount', 0) for d in deals if d.get('amount'))
    confirmed_deals = [d for d in deals if d.get('status') in ['Confirmed', 'In Progress']]
    completed_deals = [d for d in deals if d.get('status') == 'Completed']
    completed_revenue = sum(d.get('amount', 0) for d in completed_deals if d.get('amount'))
else:
    total_value = 0
    confirmed_deals = []
    completed_deals = []
    completed_revenue = 0

# Top Stats
col1, col2 = st.columns(2, gap="small")
with col1:
    render_card(
        "Pipeline Value",
        format_currency(total_value),
        subtext=f"{len(deals)} Deals gesamt",
        icon="💼"
    )
with col2:
    render_card(
        "Completed Revenue",
        format_currency(completed_revenue),
        subtext=f"{len(completed_deals)} abgeschlossen",
        icon="✅"
    )

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# Filter & Actions
col_filter, col_action = st.columns([2, 1], gap="small")
with col_filter:
    filter_status = st.selectbox(
        "Filter",
        ["Alle", "Negotiation", "Confirmed", "In Progress", "Completed", "Cancelled"],
        label_visibility="collapsed"
    )
with col_action:
    if st.button("➕ Neuer Deal", use_container_width=True):
        st.session_state["show_add_form"] = True

st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

# Add Deal Form (wenn aktiviert)
if st.session_state.get("show_add_form", False):
    with st.expander("➕ Neuen Deal hinzufügen", expanded=True):
        with st.form("add_deal_form"):
            col_brand, col_type = st.columns(2)
            with col_brand:
                brand_name = st.text_input("Brand/Unternehmen", placeholder="z.B. Nike")
            with col_type:
                deal_type = st.selectbox(
                    "Deal-Typ",
                    ["Sponsored Post", "Sponsored Video", "Brand Ambassador", "Affiliate Deal", "Product Review", "Event Appearance", "Content Series", "Giveaway"]
                )
            
            col_platform, col_amount = st.columns(2)
            with col_platform:
                platform = st.selectbox("Plattform", ["Instagram", "YouTube", "TikTok", "Multi-Channel", "Sonstige"])
            with col_amount:
                amount = st.number_input("Betrag (€)", min_value=0.0, step=100.0, value=1000.0)
            
            col_status, col_due = st.columns(2)
            with col_status:
                status = st.selectbox("Status", ["Negotiation", "Confirmed", "In Progress", "Completed", "Cancelled"])
            with col_due:
                due_date = st.date_input("Fälligkeitsdatum", value=date.today())
            
            deliverables = st.text_area("Deliverables", placeholder="z.B. 3 Instagram Posts, 2 Stories")
            
            col_contact, col_email = st.columns(2)
            with col_contact:
                contact_person = st.text_input("Ansprechpartner", placeholder="z.B. Sarah Marketing")
            with col_email:
                contact_email = st.text_input("Email", placeholder="sarah@brand.com")
            
            notes = st.text_area("Notizen", placeholder="Zusätzliche Informationen...")
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submitted = st.form_submit_button("💾 Speichern", use_container_width=True)
            with col_cancel:
                cancelled = st.form_submit_button("❌ Abbrechen", use_container_width=True)
            
            if submitted and brand_name:
                supabase = init_supabase()
                try:
                    supabase.table("deals").insert({
                        "user_id": user.email,
                        "brand_name": brand_name,
                        "deal_type": deal_type,
                        "platform": platform,
                        "status": status,
                        "amount": amount,
                        "due_date": str(due_date),
                        "deliverables": deliverables,
                        "contact_person": contact_person,
                        "contact_email": contact_email,
                        "notes": notes
                    }).execute()
                    st.success("✅ Deal hinzugefügt!")
                    st.session_state["show_add_form"] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Fehler: {e}")
            
            if cancelled:
                st.session_state["show_add_form"] = False
                st.rerun()

# Deal Liste
st.markdown("### Pipeline")
st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

if not deals:
    st.markdown("""
        <div class="st-card" style="text-align: center; padding: 32px 20px;">
            <div style="font-size: 48px; margin-bottom: 16px;">🤝</div>
            <h3 style="font-size: 18px; font-weight: 600; margin: 0 0 8px 0; color: #111827;">Noch keine Deals</h3>
            <p style="font-size: 14px; color: #6B7280; margin: 0;">Füge deine ersten Kooperationen hinzu</p>
        </div>
    """, unsafe_allow_html=True)
else:
    # Filtere Deals basierend auf Auswahl
    filtered_deals = deals if filter_status == "Alle" else [d for d in deals if d.get('status') == filter_status]
    
    if not filtered_deals:
        st.info(f"📭 Keine Deals mit Status '{filter_status}'")
    else:
        for deal in filtered_deals:
            brand = deal.get('brand_name', 'Unknown')
            deal_type = deal.get('deal_type', 'N/A')
            platform = deal.get('platform', 'N/A')
            status = deal.get('status', 'Unknown')
            amount = deal.get('amount', 0)
            due_date_str = deal.get('due_date', '')
            deliverables = deal.get('deliverables', '')
            
            # Nutze Utility-Funktionen für Status
            status_display = get_deal_status_display(status)
            status_color = get_deal_status_color(status)
            
            # Datum-Parsing & Overdue-Check
            try:
                due_date_obj = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                days_until = (due_date_obj - date.today()).days
                
                if days_until < 0 and status not in ['Completed', 'Cancelled']:
                    date_display = f'<span style="color: #EF4444; font-weight: 600;">⚠️ {abs(days_until)}d überfällig</span>'
                elif days_until == 0:
                    date_display = '<span style="color: #F59E0B; font-weight: 600;">📅 Heute fällig</span>'
                elif days_until <= 7:
                    date_display = f'<span style="color: #F59E0B;">📅 in {days_until}d</span>'
                else:
                    date_display = f'<span style="color: #6B7280;">📅 {due_date_str}</span>'
            except:
                date_display = f'<span style="color: #6B7280;">📅 {due_date_str}</span>'
            
            # Platform Icon
            platform_icons = {
                'Instagram': '📸',
                'YouTube': '📺',
                'TikTok': '🎵',
                'Multi-Channel': '🌐',
                'LinkedIn': '💼'
            }
            platform_icon = platform_icons.get(platform, '📱')
            
            st.markdown(f"""
                <div class="st-card" style="padding: 18px;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                        <div style="flex: 1;">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                                <span style="font-size: 20px;">{platform_icon}</span>
                                <div style="font-weight: 700; font-size: 16px; color: #111827;">{brand}</div>
                                <span style="background: {status_color}; color: white; font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 4px; text-transform: uppercase;">{status_display}</span>
                            </div>
                            <div style="font-size: 13px; color: #6B7280;">{deal_type} • {platform}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 700; font-size: 18px; color: #111827;">
                                {format_currency(amount)}
                            </div>
                        </div>
                    </div>
                    
                    <div style="padding-top: 12px; border-top: 1px solid #F3F4F6;">
                        <div style="font-size: 12px; color: #6B7280; margin-bottom: 4px;">
                            {date_display}
                        </div>
                        <div style="font-size: 12px; color: #6B7280;">
                            📋 {deliverables if deliverables else 'Keine Deliverables angegeben'}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.markdown("<div style='margin-top: 32px; margin-bottom: 16px; border-top: 1px solid #F3F4F6;'></div>", unsafe_allow_html=True)

# Performance Summary
if deals and len(confirmed_deals) > 0:
    pending_value = sum(d.get('amount', 0) for d in confirmed_deals if d.get('amount'))
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #3B82F615 0%, #10B98115 100%); border-radius: 12px; padding: 16px; border: 1px solid #3B82F630;'>
        <div style='font-size: 13px; color: #111827; line-height: 1.6;'>
            <strong>💼 {len(confirmed_deals)} aktive Deals</strong><br>
            Pending Revenue: <strong>{format_currency(pending_value)}</strong><br>
            <span style="font-size: 12px; color: #6B7280;">Completed: {format_currency(completed_revenue)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style='background: #F9FAFB; border-radius: 12px; padding: 16px; border: 1px solid #F3F4F6;'>
        <div style='font-size: 13px; color: #6B7280; line-height: 1.6;'>
            💡 <strong>Tipp:</strong> Tracke deine Brand Deals und Kooperationen zentral.<br>
            📊 Übersicht über Pipeline Value, Deadlines und Status.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar Actions
with st.sidebar:
    st.divider()
    st.markdown("#### 🔄 Daten")
    if st.button("🔄 Neu laden", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

