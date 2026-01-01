"""
CreatorOS - CRM
Fan- und Kundenmanagement
"""

import streamlit as st
import pandas as pd
import time
from utils import check_auth, render_sidebar, init_session_state, init_supabase

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="CRM - CreatorOS",
    page_icon="💎",
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
def load_fans(user_id):
    """Lade alle Fans des aktuellen Users"""
    try:
        response = supabase.table("fans").select("*").eq("user_id", user_id).execute()
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame(columns=["id", "user_id", "handle", "platform", "status", "total_spend", "notes", "created_at"])
    except Exception as e:
        st.error(f"Fehler beim Laden: {str(e)}")
        return pd.DataFrame(columns=["id", "user_id", "handle", "platform", "status", "total_spend", "notes", "created_at"])

# Get User ID (Supabase user.id)
user_id = user.id if hasattr(user, 'id') else user.email

# Load Fans
df_fans = load_fans(user_id)

# =============================================================================
# MAIN AREA
# =============================================================================

st.title("💎 Fan Management (CRM)")
st.write("Verwalte deine Fans und Kunden")

st.divider()

# =============================================================================
# METRIKEN
# =============================================================================

col1, col2, col3 = st.columns(3)

with col1:
    total_fans = len(df_fans)
    st.metric("👥 Anzahl Fans", total_fans)

with col2:
    whales = len(df_fans[df_fans["status"] == "Whale"]) if not df_fans.empty else 0
    st.metric("🐋 Whales", whales)

with col3:
    if not df_fans.empty and "total_spend" in df_fans.columns:
        total_revenue = df_fans["total_spend"].sum()
        st.metric("💰 Gesamt-Umsatz", f"€{total_revenue:.2f}")
    else:
        st.metric("💰 Gesamt-Umsatz", "€0.00")

st.divider()

# =============================================================================
# NEUER FAN HINZUFÜGEN
# =============================================================================

with st.expander("➕ Fan hinzufügen", expanded=False):
    st.subheader("Neuer Fan")
    
    with st.form("add_fan_form", clear_on_submit=True):
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            new_handle = st.text_input("Handle / Username", placeholder="@username")
            new_platform = st.selectbox(
                "Platform",
                ["OnlyFans", "Instagram", "Twitter", "Snapchat", "Other"]
            )
            new_status = st.selectbox(
                "Status",
                ["New", "Regular", "VIP", "Whale"]
            )
        
        with col_form2:
            new_spend = st.number_input(
                "Gesamt-Umsatz (€)",
                min_value=0.0,
                step=10.0,
                value=0.0
            )
            new_notes = st.text_area(
                "Notizen",
                placeholder="Besondere Informationen..."
            )
        
        submitted = st.form_submit_button("✅ Fan hinzufügen", use_container_width=True, type="primary")
        
        if submitted:
            if new_handle:
                try:
                    # Insert in DB
                    supabase.table("fans").insert({
                        "user_id": user_id,
                        "handle": new_handle,
                        "platform": new_platform,
                        "status": new_status,
                        "total_spend": new_spend,
                        "notes": new_notes
                    }).execute()
                    
                    st.success(f"✅ Fan '{new_handle}' hinzugefügt!")
                    
                    # Clear cache and reload
                    load_fans.clear()
                    time.sleep(0.5)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Fehler: {str(e)}")
            else:
                st.warning("⚠️ Bitte Handle eingeben")

st.divider()

# =============================================================================
# FAN LISTE & BEARBEITUNG
# =============================================================================

st.subheader("📋 Fan-Liste")

if not df_fans.empty:
    st.info("💡 **Tipp:** Du kannst Felder direkt in der Tabelle bearbeiten. Änderungen werden automatisch gespeichert.")
    
    # Sortiere nach created_at (neueste zuerst)
    if "created_at" in df_fans.columns:
        df_fans = df_fans.sort_values("created_at", ascending=False)
    
    # Wähle relevante Spalten für die Anzeige
    display_columns = ["handle", "platform", "status", "total_spend", "notes"]
    
    # Stelle sicher, dass alle Spalten existieren
    for col in display_columns:
        if col not in df_fans.columns:
            df_fans[col] = ""
    
    # Behalte 'id' für Updates, aber zeige es nicht
    df_display = df_fans[["id"] + display_columns].copy()
    
    # Column Configuration
    column_config = {
        "id": None,  # Verstecke ID
        "handle": st.column_config.TextColumn(
            "Handle",
            help="Username oder Handle des Fans",
            max_chars=100,
            required=True
        ),
        "platform": st.column_config.SelectboxColumn(
            "Platform",
            options=["OnlyFans", "Instagram", "Twitter", "Snapchat", "Other"],
            required=True
        ),
        "status": st.column_config.SelectboxColumn(
            "Status",
            options=["New", "Regular", "VIP", "Whale", "Time-Waster"],
            required=True
        ),
        "total_spend": st.column_config.NumberColumn(
            "Umsatz",
            help="Gesamtumsatz in Euro",
            format="%.2f €",
            min_value=0.0,
            step=10.0
        ),
        "notes": st.column_config.TextColumn(
            "Notizen",
            help="Interne Notizen",
            max_chars=500
        )
    }
    
    # Data Editor
    edited_df = st.data_editor(
        df_display,
        column_config=column_config,
        use_container_width=True,
        num_rows="fixed",  # Keine neuen Rows direkt im Editor (nutze Formular)
        key="fan_editor",
        hide_index=True
    )
    
    # =============================================================================
    # ÄNDERUNGEN SPEICHERN
    # =============================================================================
    
    # Prüfe ob Änderungen vorgenommen wurden
    if not edited_df.equals(df_display):
        st.info("💾 Änderungen erkannt...")
        
        # Finde geänderte Rows
        # Vergleiche jede Row einzeln
        for idx in edited_df.index:
            if idx in df_display.index:
                original_row = df_display.loc[idx]
                edited_row = edited_df.loc[idx]
                
                # Prüfe ob sich etwas geändert hat
                if not original_row.equals(edited_row):
                    fan_id = edited_row["id"]
                    
                    # Erstelle Update-Dict (nur für die Spalten die sich geändert haben)
                    update_data = {}
                    
                    for col in display_columns:
                        if original_row[col] != edited_row[col]:
                            update_data[col] = edited_row[col]
                    
                    if update_data:
                        try:
                            # Update in Supabase
                            supabase.table("fans").update(update_data).eq("id", fan_id).execute()
                            st.success(f"✅ Fan '{edited_row['handle']}' aktualisiert!")
                        except Exception as e:
                            st.error(f"❌ Fehler beim Update: {str(e)}")
        
        # Clear cache und reload nach Updates
        if st.button("🔄 Änderungen übernehmen", type="primary"):
            load_fans.clear()
            time.sleep(0.5)
            st.rerun()
    
    st.divider()
    
    # =============================================================================
    # FANS LÖSCHEN
    # =============================================================================
    
    st.subheader("🗑️ Fan löschen")
    
    with st.expander("Fan entfernen", expanded=False):
        st.warning("⚠️ **Achtung:** Das Löschen kann nicht rückgängig gemacht werden!")
        
        # Selectbox mit allen Fan-Handles
        fan_handles = df_fans["handle"].tolist()
        
        if fan_handles:
            selected_fan = st.selectbox(
                "Fan auswählen",
                fan_handles,
                key="delete_fan_select"
            )
            
            if st.button("🗑️ Fan löschen", type="secondary"):
                try:
                    # Finde die Fan-ID
                    fan_id = df_fans[df_fans["handle"] == selected_fan]["id"].iloc[0]
                    
                    # Lösche aus DB
                    supabase.table("fans").delete().eq("id", fan_id).execute()
                    
                    st.success(f"✅ Fan '{selected_fan}' gelöscht!")
                    
                    # Clear cache und reload
                    load_fans.clear()
                    time.sleep(0.5)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Fehler: {str(e)}")
        else:
            st.info("Keine Fans zum Löschen vorhanden")

else:
    st.info("📭 Noch keine Fans vorhanden. Füge deinen ersten Fan hinzu!")

st.divider()

# =============================================================================
# EXPORT
# =============================================================================

if not df_fans.empty:
    st.subheader("📤 Export")
    
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        # CSV Export
        csv = df_fans.to_csv(index=False)
        st.download_button(
            "⬇️ Als CSV exportieren",
            csv,
            "fans_export.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col_export2:
        # JSON Export
        json_str = df_fans.to_json(orient="records", indent=2)
        st.download_button(
            "⬇️ Als JSON exportieren",
            json_str,
            "fans_export.json",
            "application/json",
            use_container_width=True
        )

st.divider()
st.caption("CreatorOS v10.0 Multi-Page | Made with ❤️ for Creators")
