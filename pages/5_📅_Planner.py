"""
CreatorOS - Planner & Task Management
Aufgaben-Verwaltung für Content Creator
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import time
from utils import check_auth, render_sidebar, init_session_state, init_supabase

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Planner - CreatorOS",
    page_icon="📅",
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
# DATA LOADING
# =============================================================================

@st.cache_data(ttl=10)
def load_tasks(user_id):
    """Lade alle Tasks des aktuellen Users"""
    try:
        response = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            # Konvertiere due_date string zu datetime
            if 'due_date' in df.columns:
                df['due_date'] = pd.to_datetime(df['due_date'])
            return df
        else:
            return pd.DataFrame(columns=["id", "user_id", "title", "due_date", "category", "priority", "status", "created_at"])
    except Exception as e:
        st.error(f"Fehler beim Laden: {str(e)}")
        return pd.DataFrame(columns=["id", "user_id", "title", "due_date", "category", "priority", "status", "created_at"])

# Get User ID
user_id = user.id if hasattr(user, 'id') else user.email

# Load Tasks
df_tasks = load_tasks(user_id)

# =============================================================================
# KATEGORIEN & OPTIONEN
# =============================================================================

CATEGORIES = ["Shooting", "Editing", "Posting", "Admin", "Marketing", "Sonstiges"]
PRIORITIES = ["High", "Medium", "Low"]
STATUSES = ["Open", "In Progress", "Done"]

# =============================================================================
# MAIN AREA
# =============================================================================

st.title("📅 Task Planner")
st.write("Organisiere deine Content-Produktion")

st.divider()

# =============================================================================
# TOP METRIKEN
# =============================================================================

if not df_tasks.empty:
    total_tasks = len(df_tasks)
    open_tasks = len(df_tasks[df_tasks['status'] != 'Done'])
    high_prio_tasks = len(df_tasks[(df_tasks['priority'] == 'High') & (df_tasks['status'] != 'Done')])
    done_today = len(df_tasks[(df_tasks['status'] == 'Done') & 
                               (pd.to_datetime(df_tasks['created_at']).dt.date == date.today())])
else:
    total_tasks = 0
    open_tasks = 0
    high_prio_tasks = 0
    done_today = 0

col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)

with col_metric1:
    st.metric("📋 Gesamt", total_tasks)

with col_metric2:
    st.metric("⏳ Offen", open_tasks)

with col_metric3:
    # Highlight High-Prio Tasks
    if high_prio_tasks > 0:
        st.metric("🔴 High Priority", high_prio_tasks, delta="Dringend!")
    else:
        st.metric("✅ High Priority", high_prio_tasks)

with col_metric4:
    st.metric("🎯 Heute erledigt", done_today)

st.divider()

# =============================================================================
# LAYOUT: NEUE AUFGABE + TASK LISTE
# =============================================================================

col_left, col_right = st.columns([1, 2])

# =============================================================================
# LINKE SPALTE - NEUE AUFGABE
# =============================================================================

with col_left:
    st.subheader("➕ Neue Aufgabe")
    
    with st.form("add_task_form", clear_on_submit=True):
        task_title = st.text_input(
            "Titel",
            placeholder="z.B. Shooting für Instagram Post"
        )
        
        task_due_date = st.date_input(
            "Fälligkeitsdatum",
            value=date.today()
        )
        
        task_category = st.selectbox(
            "Kategorie",
            CATEGORIES
        )
        
        task_priority = st.selectbox(
            "Priorität",
            PRIORITIES,
            index=1  # Default: Medium
        )
        
        submitted = st.form_submit_button(
            "✅ Add Task",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if task_title:
                try:
                    # Insert in DB
                    supabase.table("tasks").insert({
                        "user_id": user_id,
                        "title": task_title,
                        "due_date": task_due_date.isoformat(),
                        "category": task_category,
                        "priority": task_priority,
                        "status": "Open"
                    }).execute()
                    
                    st.success("✅ Task hinzugefügt!")
                    
                    # Clear cache and reload
                    load_tasks.clear()
                    time.sleep(0.5)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Fehler: {str(e)}")
            else:
                st.warning("⚠️ Bitte Titel eingeben")
    
    st.divider()
    
    # Quick Stats
    st.subheader("📊 Quick Stats")
    
    if not df_tasks.empty:
        # Tasks pro Kategorie
        tasks_by_category = df_tasks[df_tasks['status'] != 'Done'].groupby('category').size()
        
        st.write("**Offene Tasks nach Kategorie:**")
        for cat, count in tasks_by_category.items():
            st.write(f"- {cat}: {count}")
    else:
        st.info("Noch keine Tasks vorhanden")

# =============================================================================
# RECHTE SPALTE - TASK LISTE
# =============================================================================

with col_right:
    st.subheader("📋 Task Liste")
    
    if not df_tasks.empty:
        # Tabs für Offen/Erledigt
        tab_open, tab_done = st.tabs(["⏳ Offen", "✅ Erledigt"])
        
        # =============================================================================
        # TAB: OFFENE TASKS
        # =============================================================================
        
        with tab_open:
            # Filter offene Tasks
            df_open = df_tasks[df_tasks['status'] != 'Done'].copy()
            
            if not df_open.empty:
                # Sortiere nach Datum (fälligste zuerst) und Priorität
                priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
                df_open['priority_sort'] = df_open['priority'].map(priority_order)
                df_open = df_open.sort_values(['due_date', 'priority_sort'])
                
                # Formatiere Datum
                df_open['due_date_formatted'] = df_open['due_date'].dt.strftime('%d.%m.%Y')
                
                # Füge visuellen Indicator für High Priority hinzu
                df_open['title_display'] = df_open.apply(
                    lambda row: f"🔴 {row['title']}" if row['priority'] == 'High' else row['title'],
                    axis=1
                )
                
                # Prüfe überfällige Tasks
                today = pd.Timestamp(date.today())
                df_open['overdue'] = df_open['due_date'] < today
                
                # Wähle Spalten für Display
                display_columns = ['title_display', 'due_date_formatted', 'category', 'priority', 'status']
                df_display = df_open[['id'] + display_columns].copy()
                
                # Rename für bessere Lesbarkeit
                df_display = df_display.rename(columns={
                    'title_display': 'Titel',
                    'due_date_formatted': 'Fällig am',
                    'category': 'Kategorie',
                    'priority': 'Priorität',
                    'status': 'Status'
                })
                
                # Column Configuration
                column_config = {
                    "id": None,  # Verstecke ID
                    "Titel": st.column_config.TextColumn(
                        "Titel",
                        help="Task-Beschreibung",
                        max_chars=200,
                        width="large"
                    ),
                    "Fällig am": st.column_config.TextColumn(
                        "Fällig am",
                        help="Fälligkeitsdatum"
                    ),
                    "Kategorie": st.column_config.SelectboxColumn(
                        "Kategorie",
                        options=CATEGORIES
                    ),
                    "Priorität": st.column_config.SelectboxColumn(
                        "Priorität",
                        options=PRIORITIES
                    ),
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=STATUSES,
                        required=True
                    )
                }
                
                st.info("💡 **Tipp:** Ändere den Status auf 'Done' um Tasks abzuschließen.")
                
                # Warne bei überfälligen Tasks
                overdue_count = df_open['overdue'].sum()
                if overdue_count > 0:
                    st.warning(f"⚠️ **{overdue_count} überfällige Task(s)!**")
                
                # Data Editor
                edited_df = st.data_editor(
                    df_display,
                    column_config=column_config,
                    use_container_width=True,
                    num_rows="fixed",
                    key="task_editor_open",
                    hide_index=True
                )
                
                # Prüfe auf Änderungen und speichere
                if not edited_df.equals(df_display):
                    for idx in edited_df.index:
                        if idx in df_display.index:
                            original_row = df_display.loc[idx]
                            edited_row = edited_df.loc[idx]
                            
                            if not original_row.equals(edited_row):
                                task_id = edited_row["id"]
                                
                                # Update-Dict erstellen
                                update_data = {}
                                
                                # Status geändert?
                                if original_row['Status'] != edited_row['Status']:
                                    update_data['status'] = edited_row['Status']
                                
                                # Priorität geändert?
                                if original_row['Priorität'] != edited_row['Priorität']:
                                    update_data['priority'] = edited_row['Priorität']
                                
                                # Kategorie geändert?
                                if original_row['Kategorie'] != edited_row['Kategorie']:
                                    update_data['category'] = edited_row['Kategorie']
                                
                                if update_data:
                                    try:
                                        supabase.table("tasks").update(update_data).eq("id", task_id).execute()
                                        
                                        # Wenn Status auf Done gesetzt wurde, zeige Erfolg
                                        if update_data.get('status') == 'Done':
                                            st.success(f"🎉 Task '{original_row['Titel'][:30]}...' abgeschlossen!")
                                        else:
                                            st.success("✅ Task aktualisiert!")
                                    except Exception as e:
                                        st.error(f"❌ Fehler beim Update: {str(e)}")
                    
                    if st.button("🔄 Änderungen übernehmen", type="primary"):
                        load_tasks.clear()
                        time.sleep(0.5)
                        st.rerun()
            else:
                st.success("🎉 Keine offenen Tasks! Zeit für eine Pause.")
        
        # =============================================================================
        # TAB: ERLEDIGTE TASKS
        # =============================================================================
        
        with tab_done:
            # Filter erledigte Tasks
            df_done = df_tasks[df_tasks['status'] == 'Done'].copy()
            
            if not df_done.empty:
                # Sortiere nach created_at (neueste zuerst)
                df_done = df_done.sort_values('created_at', ascending=False)
                
                # Formatiere Datum
                df_done['due_date_formatted'] = df_done['due_date'].dt.strftime('%d.%m.%Y')
                
                # Zeige vereinfachte Tabelle
                df_done_display = df_done[['title', 'due_date_formatted', 'category', 'priority']].copy()
                df_done_display = df_done_display.rename(columns={
                    'title': 'Titel',
                    'due_date_formatted': 'Fällig war',
                    'category': 'Kategorie',
                    'priority': 'Priorität'
                })
                
                st.dataframe(
                    df_done_display,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.success(f"✅ {len(df_done)} Task(s) erledigt!")
                
                st.divider()
                
                # Archivierung (Löschen alter Tasks)
                st.subheader("🗄️ Archivierung")
                
                with st.expander("Erledigte Tasks löschen", expanded=False):
                    st.warning("⚠️ **Achtung:** Gelöschte Tasks können nicht wiederhergestellt werden!")
                    
                    if st.button("🗑️ Alle erledigten Tasks löschen", type="secondary"):
                        try:
                            # Lösche alle Done Tasks
                            supabase.table("tasks").delete().eq("user_id", user_id).eq("status", "Done").execute()
                            
                            st.success(f"✅ {len(df_done)} Task(s) gelöscht!")
                            
                            load_tasks.clear()
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Fehler: {str(e)}")
            else:
                st.info("Noch keine erledigten Tasks")
    else:
        st.info("📭 Noch keine Tasks vorhanden. Füge deine erste Aufgabe hinzu!")

st.divider()

# =============================================================================
# WOCHENÜBERSICHT (Bonus)
# =============================================================================

if not df_tasks.empty:
    st.subheader("📆 Diese Woche")
    
    # Filtere Tasks für diese Woche
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    df_this_week = df_tasks[
        (df_tasks['due_date'].dt.date >= week_start) & 
        (df_tasks['due_date'].dt.date <= week_end) &
        (df_tasks['status'] != 'Done')
    ].copy()
    
    if not df_this_week.empty:
        # Gruppiere nach Tag
        df_this_week['day_name'] = df_this_week['due_date'].dt.day_name()
        tasks_per_day = df_this_week.groupby('day_name').size()
        
        col_week1, col_week2 = st.columns(2)
        
        with col_week1:
            st.bar_chart(tasks_per_day)
        
        with col_week2:
            st.write(f"**{len(df_this_week)} Tasks diese Woche:**")
            for day, count in tasks_per_day.items():
                st.write(f"- {day}: {count} Task(s)")
    else:
        st.info("Keine offenen Tasks für diese Woche")

st.divider()
st.caption("CreatorOS v10.0 Multi-Page | Made with ❤️ for Creators")

