"""
CreatorOS - Main Dashboard
Zentrale Übersicht über alle Module
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from utils import check_auth, render_sidebar, init_session_state, init_supabase

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
# SUPABASE CLIENT
# =============================================================================
supabase = init_supabase()
user_id = user.id if hasattr(user, 'id') else user.email

# =============================================================================
# DATA LOADING & AGGREGATION
# =============================================================================

@st.cache_data(ttl=30)
def load_dashboard_data(user_id):
    """Lade alle Daten für das Dashboard"""
    
    # Current Month Dates
    now = datetime.now()
    first_day_month = date(now.year, now.month, 1)
    
    # Last 30 Days
    days_ago_30 = datetime.now() - timedelta(days=30)
    
    data = {
        'revenue_month': 0,
        'profit_month': 0,
        'new_fans_month': 0,
        'open_tasks': 0,
        'revenue_30_days': pd.DataFrame(),
        'total_fans': 0,
        'total_tasks': 0
    }
    
    # =============================================================================
    # FINANCE DATA
    # =============================================================================
    try:
        finance_response = supabase.table("finance_entries").select("*").eq("user_id", user_id).execute()
        
        if finance_response.data:
            df_finance = pd.DataFrame(finance_response.data)
            df_finance['date'] = pd.to_datetime(df_finance['date'])
            
            # This Month
            df_this_month = df_finance[df_finance['date'].dt.date >= first_day_month]
            
            if not df_this_month.empty:
                einnahmen_month = df_this_month[df_this_month['type'] == 'Einnahme']['amount'].sum()
                ausgaben_month = df_this_month[df_this_month['type'] == 'Ausgabe']['amount'].sum()
                
                data['revenue_month'] = einnahmen_month
                data['profit_month'] = einnahmen_month - ausgaben_month
            
            # Last 30 Days (for chart)
            df_30_days = df_finance[df_finance['date'] >= days_ago_30]
            
            if not df_30_days.empty:
                # Daily revenue
                daily_revenue = df_30_days[df_30_days['type'] == 'Einnahme'].groupby(
                    df_30_days['date'].dt.date
                )['amount'].sum().reset_index()
                
                daily_revenue.columns = ['date', 'revenue']
                daily_revenue = daily_revenue.sort_values('date')
                
                data['revenue_30_days'] = daily_revenue
    except Exception as e:
        print(f"Finance load error: {e}")
    
    # =============================================================================
    # FANS DATA
    # =============================================================================
    try:
        fans_response = supabase.table("fans").select("*").eq("user_id", user_id).execute()
        
        if fans_response.data:
            df_fans = pd.DataFrame(fans_response.data)
            data['total_fans'] = len(df_fans)
            
            # Fans created this month
            df_fans['created_at'] = pd.to_datetime(df_fans['created_at'])
            df_new_fans = df_fans[df_fans['created_at'].dt.date >= first_day_month]
            data['new_fans_month'] = len(df_new_fans)
    except Exception as e:
        print(f"Fans load error: {e}")
    
    # =============================================================================
    # TASKS DATA
    # =============================================================================
    try:
        tasks_response = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
        
        if tasks_response.data:
            df_tasks = pd.DataFrame(tasks_response.data)
            data['total_tasks'] = len(df_tasks)
            
            # Open tasks
            df_open = df_tasks[df_tasks['status'] != 'Done']
            data['open_tasks'] = len(df_open)
    except Exception as e:
        print(f"Tasks load error: {e}")
    
    return data

# Load Data
dashboard_data = load_dashboard_data(user_id)

# =============================================================================
# MAIN DASHBOARD
# =============================================================================

st.title("🎯 CreatorDeck Dashboard")
st.write(f"Willkommen zurück, **{user_email}** 👋")

st.divider()

# =============================================================================
# TOP-LEVEL KPIs
# =============================================================================

st.subheader("📊 Übersicht diesen Monat")

col1, col2, col3, col4 = st.columns(4)

with col1:
    revenue = dashboard_data['revenue_month']
    st.metric(
        "💰 Umsatz",
        f"€{revenue:,.2f}",
        delta=None,
        help="Gesamte Einnahmen diesen Monat"
    )

with col2:
    profit = dashboard_data['profit_month']
    delta_color = "normal" if profit >= 0 else "inverse"
    st.metric(
        "📈 Gewinn",
        f"€{profit:,.2f}",
        delta=f"{'🟢' if profit >= 0 else '🔴'}",
        delta_color=delta_color,
        help="Einnahmen - Ausgaben diesen Monat"
    )

with col3:
    new_fans = dashboard_data['new_fans_month']
    st.metric(
        "👥 Neue Fans",
        new_fans,
        delta=None,
        help="Fans, die diesen Monat hinzugefügt wurden"
    )

with col4:
    open_tasks = dashboard_data['open_tasks']
    # Highlight wenn viele offene Tasks
    if open_tasks > 10:
        delta_indicator = "⚠️"
    elif open_tasks > 0:
        delta_indicator = "📋"
    else:
        delta_indicator = "✅"
    
    st.metric(
        "📅 Offene Tasks",
        open_tasks,
        delta=delta_indicator,
        help="Tasks die noch erledigt werden müssen"
    )

st.divider()

# =============================================================================
# SCHNELL-AKTIONEN
# =============================================================================

st.subheader("⚡ Schnell-Aktionen")

col_action1, col_action2, col_action3, col_action4 = st.columns(4)

with col_action1:
    if st.button("📸 Upload starten", use_container_width=True, type="primary"):
        st.switch_page("pages/3_🎨_Content_Factory.py")

with col_action2:
    if st.button("💰 Einnahme buchen", use_container_width=True):
        st.switch_page("pages/2_💸_Finance.py")

with col_action3:
    if st.button("👥 Fan hinzufügen", use_container_width=True):
        st.switch_page("pages/1_💎_CRM.py")

with col_action4:
    if st.button("📅 Task erstellen", use_container_width=True):
        st.switch_page("pages/5_📅_Planner.py")

st.divider()

# =============================================================================
# CHARTS & INSIGHTS
# =============================================================================

col_chart1, col_chart2 = st.columns([2, 1])

with col_chart1:
    st.subheader("📈 Umsatzverlauf (30 Tage)")
    
    df_revenue = dashboard_data['revenue_30_days']
    
    if not df_revenue.empty:
        # Setze date als Index für bessere Chart-Darstellung
        df_revenue_chart = df_revenue.set_index('date')
        
        st.line_chart(df_revenue_chart['revenue'], use_container_width=True)
        
        # Stats
        avg_daily = df_revenue['revenue'].mean()
        max_day = df_revenue.loc[df_revenue['revenue'].idxmax()]
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Ø Tagesumsatz", f"€{avg_daily:.2f}")
        with col_stat2:
            st.metric(
                "Bester Tag", 
                f"€{max_day['revenue']:.2f}",
                delta=max_day['date'].strftime('%d.%m.%Y')
            )
    else:
        st.info("📭 Noch keine Einnahmen in den letzten 30 Tagen. Buche deine erste Einnahme!")

with col_chart2:
    st.subheader("🎯 Quick Stats")
    
    # Progress bars for different metrics
    st.write("**Aktivität:**")
    
    # Fans
    total_fans = dashboard_data['total_fans']
    st.write(f"👥 **{total_fans}** Fans gesamt")
    
    if total_fans > 0:
        fan_growth = (dashboard_data['new_fans_month'] / total_fans * 100) if total_fans > 0 else 0
        st.progress(min(fan_growth / 100, 1.0))
        st.caption(f"{fan_growth:.1f}% Wachstum diesen Monat")
    else:
        st.progress(0.0)
        st.caption("Noch keine Fans")
    
    st.divider()
    
    # Tasks
    total_tasks = dashboard_data['total_tasks']
    st.write(f"📋 **{total_tasks}** Tasks gesamt")
    
    if total_tasks > 0:
        completion_rate = ((total_tasks - open_tasks) / total_tasks * 100) if total_tasks > 0 else 0
        st.progress(completion_rate / 100)
        st.caption(f"{completion_rate:.0f}% abgeschlossen")
    else:
        st.progress(0.0)
        st.caption("Noch keine Tasks")
    
    st.divider()
    
    # Status Badge
    if is_pro or is_admin:
        st.success("✨ **PRO Account**")
    else:
        st.info("🆓 **FREE Account**")
        st.link_button(
            "Upgrade auf PRO",
            "https://buy.stripe.com/28E8wO0W59Y46rM8rG6J200",
            use_container_width=True
        )

st.divider()

# =============================================================================
# MODULE NAVIGATION
# =============================================================================

st.subheader("🗂️ Module")

col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    with st.container():
        st.markdown("### 💎 CRM")
        st.write(f"**{dashboard_data['total_fans']}** Fans")
        st.write(f"**{dashboard_data['new_fans_month']}** neue diesen Monat")
        if st.button("→ Zum CRM", use_container_width=True, key="nav_crm"):
            st.switch_page("pages/1_💎_CRM.py")

with col_nav2:
    with st.container():
        st.markdown("### 💸 Finance")
        st.write(f"**€{dashboard_data['revenue_month']:,.2f}** Umsatz")
        st.write(f"**€{dashboard_data['profit_month']:,.2f}** Gewinn")
        if st.button("→ Zu Finance", use_container_width=True, key="nav_finance"):
            st.switch_page("pages/2_💸_Finance.py")

with col_nav3:
    with st.container():
        st.markdown("### 📅 Planner")
        st.write(f"**{dashboard_data['open_tasks']}** offene Tasks")
        st.write(f"**{dashboard_data['total_tasks']}** gesamt")
        if st.button("→ Zum Planner", use_container_width=True, key="nav_planner"):
            st.switch_page("pages/5_📅_Planner.py")

st.divider()

# =============================================================================
# MOTIVATIONAL MESSAGE
# =============================================================================

st.subheader("💡 Heute")

# Generate motivational message based on data
messages = []

if dashboard_data['open_tasks'] > 0:
    messages.append(f"📋 Du hast **{dashboard_data['open_tasks']}** offene Tasks. Los geht's!")
else:
    messages.append("🎉 Keine offenen Tasks! Zeit für neue Projekte.")

if dashboard_data['profit_month'] > 0:
    messages.append(f"💰 Toller Monat! **€{dashboard_data['profit_month']:,.2f}** Gewinn.")
elif dashboard_data['revenue_month'] > 0:
    messages.append("📊 Einnahmen fließen! Halte die Ausgaben im Griff.")
else:
    messages.append("🚀 Buche deine erste Einnahme und starte durch!")

if dashboard_data['new_fans_month'] > 0:
    messages.append(f"👥 **{dashboard_data['new_fans_month']}** neue Fans diesen Monat!")

# Display messages
for msg in messages:
    st.info(msg)

st.divider()

# =============================================================================
# REFRESH & FOOTER
# =============================================================================

col_refresh, col_spacer = st.columns([1, 3])

with col_refresh:
    if st.button("🔄 Dashboard aktualisieren", use_container_width=True):
        load_dashboard_data.clear()
        st.rerun()

st.divider()

st.caption(f"CreatorOS v10.0 | Zuletzt aktualisiert: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
st.caption("Made with ❤️ for Content Creators")
