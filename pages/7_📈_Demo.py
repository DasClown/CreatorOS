"""
CreatorOS - Portfolio Demo
Minimalistisches Trade Republic / Banking App Style
"""

import streamlit as st
from utils import (
    inject_custom_css, 
    init_supabase, 
    render_card, 
    get_assets, 
    format_currency,
    check_auth,
    render_sidebar,
    init_session_state
)

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Portfolio - CreatorOS",
    page_icon="📈",
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

# Header (Minimalistisch)
st.markdown("## Portfolio")
st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# Lade Assets aus der Datenbank
assets = get_assets()

# Berechnungen für Portfolio-Gesamtwert
total_value = sum(item.get('current_value', 0) for item in assets) if assets else 0
cash_value = 3200.00  # Simulierter Cash-Bestand (könnte auch aus DB kommen)

# Top Stats (Gesamtübersicht)
col1, col2 = st.columns(2)
with col1:
    render_card(
        "Gesamtvermögen", 
        format_currency(total_value + cash_value), 
        "inkl. Cash", 
        trend=1.2
    )
with col2:
    render_card(
        "Verfügbar (Cash)", 
        format_currency(cash_value), 
        "Verrechnungskonto"
    )

st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

# Quick Actions
st.markdown("### Aktionen")
st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

col_a, col_b = st.columns(2, gap="small")
with col_a:
    if st.button("💰 Einzahlen", use_container_width=True):
        st.toast("💰 Einzahlung vorbereitet...")
with col_b:
    if st.button("💸 Auszahlen", use_container_width=True):
        st.toast("💸 Auszahlung vorbereitet...")

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# Asset Liste (Aus der Datenbank)
st.markdown("### Investments")

if not assets:
    st.markdown("""
        <div class="st-card" style="text-align: center; padding: 32px 20px;">
            <div style="font-size: 48px; margin-bottom: 16px;">📊</div>
            <h3 style="font-size: 18px; font-weight: 600; margin: 0 0 8px 0; color: #111827;">Noch keine Assets</h3>
            <p style="font-size: 14px; color: #6B7280; margin: 0;">Füge dein erstes Investment hinzu</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📝 Anleitung: Assets hinzufügen", expanded=True):
        st.markdown("""
        **Via Supabase Dashboard:**
        
        1. Öffne [Supabase Dashboard](https://supabase.com/dashboard)
        2. **Table Editor** → `assets` → **Insert Row**
        3. Fülle die Felder aus:
           - `user_id`: Deine Email
           - `name`: z.B. "Apple Inc."
           - `ticker`: z.B. "AAPL"
           - `asset_type`: "Stock", "Crypto", "ETF"
           - `quantity`: 12
           - `purchase_price`: 180.00
           - `current_value`: 2334.00
           - `change_24h`: 2.4
        
        **Via SQL (Schneller):**
        ```sql
        -- Ersetze mit deiner Email
        INSERT INTO public.assets 
        (user_id, name, ticker, asset_type, quantity, purchase_price, current_value, change_24h)
        VALUES 
        ('deine-email@example.com', 'Apple Inc.', 'AAPL', 'Stock', 12, 180.00, 2334.00, 2.4),
        ('deine-email@example.com', 'Bitcoin', 'BTC', 'Crypto', 0.45, 35000.00, 17775.00, 5.8);
        ```
        """)
else:
    for asset in assets:
        # Dynamische Farbe für Prozentanzeige mit Badge-Style
        change = asset.get('change_24h', 0)
        color = "#10B981" if change > 0 else "#EF4444" if change < 0 else "#6B7280"
        arrow = "▲" if change > 0 else "▼" if change < 0 else ""
        prefix = "+" if change > 0 else ""
        
        # Formatiere Quantity
        quantity_text = asset.get('quantity', 'N/A')
        if isinstance(quantity_text, (int, float)):
            # Zeige nur 2 Dezimalstellen für cleane Darstellung
            quantity_text = f"{quantity_text:.2f}".rstrip('0').rstrip('.')
        
        with st.container():
            st.markdown(f"""
                <div class="st-card" style="display: flex; justify-content: space-between; align-items: center; padding: 18px;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 16px; color: #111827; margin-bottom: 4px;">{asset.get('name', 'Unknown')}</div>
                        <div style="color: #9CA3AF; font-size: 13px;">{quantity_text} {asset.get('asset_type', 'Stk')}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: 700; font-size: 17px; color: #111827; margin-bottom: 6px;">
                            {format_currency(asset.get('current_value', 0))}
                        </div>
                        <div style="display: inline-block; font-size: 12px; font-weight: 600; color: {color}; background: {color}15; padding: 2px 6px; border-radius: 4px;">
                            {arrow} {prefix}{abs(change)}%
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.markdown("<div style='margin-top: 32px; margin-bottom: 16px; border-top: 1px solid #F3F4F6;'></div>", unsafe_allow_html=True)

# Performance Hinweis
st.markdown("""
<div style='background: #F9FAFB; border-radius: 12px; padding: 16px; border: 1px solid #F3F4F6;'>
    <div style='font-size: 13px; color: #6B7280; line-height: 1.6;'>
        💡 <strong>Tipp:</strong> Für Echtzeit-Preise kannst du APIs wie CoinGecko (Crypto) oder Alpha Vantage (Stocks) integrieren.<br>
        📊 Portfolio-Werte werden aus der Supabase <code>assets</code> Tabelle geladen.
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
