"""
CreatorOS - Finance
Finanz-Tracking und Buchhaltung
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import time
from utils import check_auth, render_sidebar, init_session_state, init_supabase, inject_custom_css

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Finance - CreatorOS",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS
inject_custom_css()

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
def load_finance_entries(user_id):
    """Lade alle Finance-Einträge des aktuellen Users"""
    try:
        response = supabase.table("finance_entries").select("*").eq("user_id", user_id).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            # Konvertiere date string zu datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            return df
        else:
            return pd.DataFrame(columns=["id", "user_id", "type", "amount", "category", "description", "date", "created_at"])
    except Exception as e:
        st.error(f"Fehler beim Laden: {str(e)}")
        return pd.DataFrame(columns=["id", "user_id", "type", "amount", "category", "description", "date", "created_at"])

# Get User ID
user_id = user.id if hasattr(user, 'id') else user.email

# Load Finance Data
df_finance = load_finance_entries(user_id)

# =============================================================================
# KATEGORIEN
# =============================================================================

CATEGORIES_EINNAHME = [
    "OnlyFans",
    "Fansly",
    "Instagram",
    "Patreon",
    "Custom Content",
    "Sponsoring",
    "Sonstiges"
]

CATEGORIES_AUSGABE = [
    "Technik & Equipment",
    "Software & Tools",
    "Reise & Location",
    "Werbung & Marketing",
    "Outfits & Requisiten",
    "Assistenz & Services",
    "Sonstiges"
]

# =============================================================================
# MAIN AREA
# =============================================================================

st.title("💸 Finance Tracking")
st.write("Verwalte deine Einnahmen und Ausgaben")

st.divider()

# =============================================================================
# METRIKEN BERECHNEN
# =============================================================================

if not df_finance.empty and 'amount' in df_finance.columns and 'type' in df_finance.columns:
    einnahmen = df_finance[df_finance['type'] == 'Einnahme']['amount'].sum()
    ausgaben = df_finance[df_finance['type'] == 'Ausgabe']['amount'].sum()
    gewinn = einnahmen - ausgaben
else:
    einnahmen = 0.0
    ausgaben = 0.0
    gewinn = 0.0

# =============================================================================
# METRIKEN ANZEIGEN
# =============================================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "📈 Gesamteinnahmen",
        f"€{einnahmen:,.2f}",
        delta=None
    )

with col2:
    st.metric(
        "📉 Gesamtausgaben",
        f"€{ausgaben:,.2f}",
        delta=None
    )

with col3:
    delta_color = "normal" if gewinn >= 0 else "inverse"
    st.metric(
        "💰 Gewinn",
        f"€{gewinn:,.2f}",
        delta=f"{'🟢' if gewinn >= 0 else '🔴'} {abs(gewinn):,.2f}",
        delta_color=delta_color
    )

st.divider()

# =============================================================================
# NEUE BUCHUNG HINZUFÜGEN
# =============================================================================

with st.expander("💰 Buchung hinzufügen", expanded=False):
    st.subheader("Neue Buchung")
    
    # Typ-Auswahl
    entry_type = st.radio(
        "Typ",
        ["Einnahme", "Ausgabe"],
        horizontal=True
    )
    
    # Dynamische Kategorien basierend auf Typ
    if entry_type == "Einnahme":
        categories = CATEGORIES_EINNAHME
    else:
        categories = CATEGORIES_AUSGABE
    
    with st.form("add_entry_form", clear_on_submit=True):
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            entry_amount = st.number_input(
                "Betrag (€)",
                min_value=0.01,
                step=10.0,
                value=10.0
            )
            entry_date = st.date_input(
                "Datum",
                value=date.today()
            )
        
        with col_form2:
            entry_category = st.selectbox(
                "Kategorie",
                categories
            )
            entry_description = st.text_input(
                "Beschreibung",
                placeholder="z.B. OnlyFans Subscription, Equipment-Kauf..."
            )
        
        submitted = st.form_submit_button(
            f"✅ {entry_type} buchen",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if entry_amount > 0:
                try:
                    # Insert in DB
                    supabase.table("finance_entries").insert({
                        "user_id": user_id,
                        "type": entry_type,
                        "amount": float(entry_amount),
                        "category": entry_category,
                        "description": entry_description,
                        "date": entry_date.isoformat()
                    }).execute()
                    
                    st.success(f"✅ {entry_type} von €{entry_amount:.2f} gebucht!")
                    
                    # Clear cache and reload
                    load_finance_entries.clear()
                    time.sleep(0.5)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Fehler: {str(e)}")
            else:
                st.warning("⚠️ Betrag muss größer als 0 sein")

st.divider()

# =============================================================================
# ANALYSE & CHARTS
# =============================================================================

st.subheader("📊 Analyse")

tab1, tab2 = st.tabs(["📈 Übersicht", "📋 Daten"])

with tab1:
    if not df_finance.empty:
        # =============================================================================
        # MONATLICHE ÜBERSICHT (Balkendiagramm)
        # =============================================================================
        
        st.subheader("Einnahmen vs. Ausgaben pro Monat")
        
        # Erstelle eine Kopie für die Analyse
        df_analysis = df_finance.copy()
        
        # Extrahiere Jahr-Monat
        df_analysis['year_month'] = df_analysis['date'].dt.to_period('M').astype(str)
        
        # Pivot: Einnahmen und Ausgaben pro Monat
        monthly_summary = df_analysis.groupby(['year_month', 'type'])['amount'].sum().unstack(fill_value=0)
        
        # Stelle sicher, dass beide Spalten existieren
        if 'Einnahme' not in monthly_summary.columns:
            monthly_summary['Einnahme'] = 0
        if 'Ausgabe' not in monthly_summary.columns:
            monthly_summary['Ausgabe'] = 0
        
        # Sortiere nach Datum
        monthly_summary = monthly_summary.sort_index()
        
        # Chart
        st.bar_chart(monthly_summary[['Einnahme', 'Ausgabe']])
        
        st.divider()
        
        # =============================================================================
        # KATEGORIE-ANALYSE (Ausgaben)
        # =============================================================================
        
        col_cat1, col_cat2 = st.columns(2)
        
        with col_cat1:
            st.subheader("💸 Ausgaben nach Kategorie")
            
            ausgaben_by_category = df_finance[df_finance['type'] == 'Ausgabe'].groupby('category')['amount'].sum().sort_values(ascending=False)
            
            if not ausgaben_by_category.empty:
                st.bar_chart(ausgaben_by_category)
            else:
                st.info("Noch keine Ausgaben vorhanden")
        
        with col_cat2:
            st.subheader("📈 Einnahmen nach Kategorie")
            
            einnahmen_by_category = df_finance[df_finance['type'] == 'Einnahme'].groupby('category')['amount'].sum().sort_values(ascending=False)
            
            if not einnahmen_by_category.empty:
                st.bar_chart(einnahmen_by_category)
            else:
                st.info("Noch keine Einnahmen vorhanden")
        
        st.divider()
        
        # =============================================================================
        # TOP KATEGORIEN
        # =============================================================================
        
        st.subheader("🏆 Top Kategorien")
        
        col_top1, col_top2 = st.columns(2)
        
        with col_top1:
            st.write("**Höchste Einnahmen:**")
            if not einnahmen_by_category.empty:
                for idx, (cat, amount) in enumerate(einnahmen_by_category.head(3).items(), 1):
                    st.write(f"{idx}. **{cat}**: €{amount:,.2f}")
            else:
                st.info("Keine Daten")
        
        with col_top2:
            st.write("**Höchste Ausgaben:**")
            if not ausgaben_by_category.empty:
                for idx, (cat, amount) in enumerate(ausgaben_by_category.head(3).items(), 1):
                    st.write(f"{idx}. **{cat}**: €{amount:,.2f}")
            else:
                st.info("Keine Daten")
    
    else:
        st.info("📭 Noch keine Buchungen vorhanden. Füge deine erste Buchung hinzu!")

with tab2:
    st.subheader("📋 Alle Buchungen")
    
    if not df_finance.empty:
        # Sortiere nach Datum (neueste zuerst)
        df_display = df_finance.sort_values('date', ascending=False).copy()
        
        # Formatiere Datum für bessere Lesbarkeit
        df_display['date_formatted'] = df_display['date'].dt.strftime('%d.%m.%Y')
        
        # Wähle relevante Spalten
        display_columns = ['date_formatted', 'type', 'category', 'amount', 'description']
        
        # Stelle sicher, dass alle Spalten existieren
        for col in display_columns:
            if col not in df_display.columns and col != 'date_formatted':
                df_display[col] = ""
        
        # Zeige als Dataframe mit ID für Lösch-Funktion
        df_show = df_display[['id'] + display_columns].copy()
        
        # Formatiere Amount
        df_show['amount'] = df_show['amount'].apply(lambda x: f"€{x:,.2f}")
        
        # Rename für bessere Lesbarkeit
        df_show = df_show.rename(columns={
            'date_formatted': 'Datum',
            'type': 'Typ',
            'category': 'Kategorie',
            'amount': 'Betrag',
            'description': 'Beschreibung'
        })
        
        st.dataframe(
            df_show.drop('id', axis=1),
            use_container_width=True,
            hide_index=True
        )
        
        st.divider()
        
        # =============================================================================
        # BUCHUNG LÖSCHEN
        # =============================================================================
        
        st.subheader("🗑️ Buchung löschen")
        
        with st.expander("Buchung entfernen", expanded=False):
            st.warning("⚠️ **Achtung:** Das Löschen kann nicht rückgängig gemacht werden!")
            
            # Erstelle aussagekräftige Labels für Selectbox
            entry_labels = []
            entry_ids = []
            
            for idx, row in df_display.iterrows():
                label = f"{row['date'].strftime('%d.%m.%Y')} - {row['type']} - €{row['amount']:.2f} - {row['category']}"
                if pd.notna(row.get('description')) and row['description']:
                    label += f" ({row['description'][:30]}...)" if len(row['description']) > 30 else f" ({row['description']})"
                
                entry_labels.append(label)
                entry_ids.append(row['id'])
            
            if entry_labels:
                selected_entry_label = st.selectbox(
                    "Buchung auswählen",
                    entry_labels,
                    key="delete_entry_select"
                )
                
                selected_idx = entry_labels.index(selected_entry_label)
                selected_id = entry_ids[selected_idx]
                
                if st.button("🗑️ Buchung löschen", type="secondary"):
                    try:
                        # Lösche aus DB
                        supabase.table("finance_entries").delete().eq("id", selected_id).execute()
                        
                        st.success("✅ Buchung gelöscht!")
                        
                        # Clear cache und reload
                        load_finance_entries.clear()
                        time.sleep(0.5)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Fehler: {str(e)}")
            else:
                st.info("Keine Buchungen zum Löschen vorhanden")
        
        st.divider()
        
        # =============================================================================
        # EXPORT
        # =============================================================================
        
        st.subheader("📤 Export")
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            # CSV Export
            csv = df_finance.to_csv(index=False)
            st.download_button(
                "⬇️ Als CSV exportieren",
                csv,
                "finance_export.csv",
                "text/csv",
                use_container_width=True
            )
        
        with col_export2:
            # JSON Export
            json_str = df_finance.to_json(orient="records", indent=2, date_format='iso')
            st.download_button(
                "⬇️ Als JSON exportieren",
                json_str,
                "finance_export.json",
                "application/json",
                use_container_width=True
            )
    
    else:
        st.info("📭 Noch keine Buchungen vorhanden.")

st.divider()
st.caption("CreatorOS v10.0 Multi-Page | Made with ❤️ for Creators")
