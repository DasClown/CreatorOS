# 📈 Portfolio Demo - Setup Guide

## Übersicht

Die **Portfolio Demo-Page** zeigt CreatorOS im minimalistischen **Trade Republic / Banking App Style**.

**Features:**
- 📊 Portfolio-Übersicht mit Gesamtwert & Cash
- 💰 Asset-Liste mit Live-Performance (▲/▼)
- 🎨 Cleanes, modernes UI (Light Theme)
- 🔄 Echtzeit-Daten aus Supabase
- 📱 Mobile-First Design

---

## 🚀 Quick Start

### 1. Datenbank einrichten

**Option A: Neue Installation**

```bash
# Im Supabase SQL Editor:
1. Öffne: https://supabase.com/dashboard
2. Navigiere zu: SQL Editor
3. Führe aus: supabase_assets_table.sql (komplettes File)
```

**Option B: Bestehende Tabelle erweitern**

Falls du die `assets` Tabelle bereits hast:

```bash
# Im Supabase SQL Editor:
# Führe aus: supabase_assets_table_migration.sql
```

---

### 2. Demo-Daten einfügen

Erstelle Test-Assets in deinem Account:

```sql
-- Ersetze 'deine-email@example.com' mit deiner Login-Email
INSERT INTO public.assets (user_id, name, ticker, asset_type, quantity, purchase_price, current_value, change_24h)
VALUES 
    ('deine-email@example.com', 'Apple Inc.', 'AAPL', 'Stock', 12, 180.00, 2334.00, 2.4),
    ('deine-email@example.com', 'Tesla', 'TSLA', 'Stock', 5, 200.00, 1051.00, -1.2),
    ('deine-email@example.com', 'Bitcoin', 'BTC', 'Crypto', 0.45, 35000.00, 17775.00, 5.8),
    ('deine-email@example.com', 'Microsoft', 'MSFT', 'Stock', 8, 380.00, 3298.40, 0.9),
    ('deine-email@example.com', 'Ethereum', 'ETH', 'Crypto', 2.5, 2000.00, 5500.00, 3.2);
```

**Wichtig:** Nutze die Email, mit der du in CreatorOS eingeloggt bist!

---

### 3. App starten

```bash
# Im Terminal:
cd /Users/janickthum/Desktop/creatorOS
source .venv/bin/activate
streamlit run Hello.py
```

---

### 4. Demo-Page öffnen

```
http://localhost:8501
→ Sidebar: Klicke auf "📈 Demo"
```

---

## 📊 Datenbank-Schema

### `assets` Tabelle

| Spalte          | Typ        | Beschreibung                                      |
|-----------------|------------|---------------------------------------------------|
| `id`            | UUID       | Primärschlüssel (automatisch)                     |
| `user_id`       | TEXT       | Email des Users                                   |
| `name`          | TEXT       | Asset-Name (z.B. "Apple Inc.")                    |
| `ticker`        | TEXT       | Ticker-Symbol (z.B. "AAPL", "BTC")                |
| `asset_type`    | TEXT       | Typ: "Stock", "Crypto", "ETF", "Other"            |
| `quantity`      | NUMERIC    | Menge/Anzahl (z.B. 12 Aktien, 0.45 BTC)           |
| `purchase_price`| NUMERIC    | Einkaufspreis pro Einheit                         |
| `current_value` | NUMERIC    | Aktueller Gesamtwert                              |
| `change_24h`    | NUMERIC    | **Neu!** Performance 24h in % (z.B. +2.4, -1.5)  |
| `created_at`    | TIMESTAMP  | Erstelldatum                                      |
| `last_updated`  | TIMESTAMP  | Letztes Update                                    |

---

## 💡 Assets hinzufügen

### Via Supabase Table Editor:

1. Gehe zu: https://supabase.com/dashboard
2. Öffne: **Table Editor** → `assets`
3. Klicke: **Insert Row**
4. Fülle aus:
   - `user_id`: Deine Email
   - `name`: "Tesla"
   - `ticker`: "TSLA"
   - `asset_type`: "Stock"
   - `quantity`: 5
   - `purchase_price`: 200.00
   - `current_value`: 1051.00
   - `change_24h`: -1.2
5. **Save**

### Via SQL:

```sql
INSERT INTO public.assets (user_id, name, ticker, asset_type, quantity, purchase_price, current_value, change_24h)
VALUES ('deine-email@example.com', 'Tesla', 'TSLA', 'Stock', 5, 200.00, 1051.00, -1.2);
```

---

## 🔄 Performance-Updates (change_24h)

### Manuell:

```sql
UPDATE public.assets
SET change_24h = 3.5, current_value = 2450.00
WHERE ticker = 'AAPL' AND user_id = 'deine-email@example.com';
```

### Automatisch (API-Integration):

Für Echtzeit-Preise kannst du APIs integrieren:

**Crypto (CoinGecko):**
```python
import requests

def update_crypto_prices():
    response = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={
            "ids": "bitcoin,ethereum",
            "vs_currencies": "eur",
            "include_24hr_change": "true"
        }
    )
    data = response.json()
    
    # Update Bitcoin
    supabase.table("assets").update({
        "change_24h": data["bitcoin"]["eur_24h_change"]
    }).eq("ticker", "BTC").execute()
```

**Stocks (Alpha Vantage):**
```python
import requests

def update_stock_prices():
    API_KEY = "dein-api-key"
    response = requests.get(
        f"https://www.alphavantage.co/query",
        params={
            "function": "GLOBAL_QUOTE",
            "symbol": "AAPL",
            "apikey": API_KEY
        }
    )
    data = response.json()["Global Quote"]
    
    # Update Apple
    supabase.table("assets").update({
        "current_value": float(data["05. price"]) * quantity,
        "change_24h": float(data["10. change percent"].rstrip('%'))
    }).eq("ticker", "AAPL").execute()
```

---

## 🎨 UI-Anpassungen

### Farben ändern:

**In `utils.py` → `inject_custom_css()`:**

```python
# Performance Grün/Rot
"#10B981"  # Grün für positive Performance
"#EF4444"  # Rot für negative Performance
"#6B7280"  # Grau für neutral

# Buttons
"#000000"  # Schwarz (Primary)
"#333333"  # Hover
```

### Card-Hover-Effekt deaktivieren:

```python
# In utils.py, entferne:
transition: transform 0.1s, border-color 0.2s;
transform: translateY(-1px);
```

---

## 🔐 Sicherheit

### Row Level Security (RLS):

Die `assets` Tabelle hat **RLS aktiviert**:

```sql
-- User können nur eigene Assets sehen
CREATE POLICY "Users can view own assets"
    ON public.assets
    FOR SELECT
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'email');
```

**Das bedeutet:**
- ✅ Jeder User sieht nur seine eigenen Assets
- ✅ Keine Cross-User Datenlecks
- ✅ Automatische Filterung

---

## 🧪 Testing

### Verifiziere dass die Tabelle existiert:

```sql
SELECT COUNT(*) FROM public.assets;
```

**Erwartetes Ergebnis:** `>= 0` (keine Errors)

### Teste RLS:

```sql
-- Zeige meine Assets
SELECT * FROM public.assets WHERE user_id = 'deine-email@example.com';
```

**Erwartetes Ergebnis:** Nur deine Assets werden angezeigt.

---

## 📱 Mobile Ansicht

Das UI ist **Mobile-First**:

- Max-Width: 800px (zentriert)
- Responsive Columns
- Touch-freundliche Buttons (min. 45px Höhe)

Teste es:
```
http://localhost:8501
→ Browser-Dev-Tools (F12)
→ Toggle Device Toolbar
→ Wähle "iPhone 12 Pro"
```

---

## 🐛 Troubleshooting

### "Keine Assets gefunden"

**Mögliche Ursachen:**
1. Keine Daten in der DB für deine Email
2. RLS-Policies blockieren den Zugriff
3. `user_id` stimmt nicht mit deiner Login-Email überein

**Lösung:**
```sql
-- Prüfe ob Daten existieren
SELECT * FROM public.assets;

-- Prüfe user_id
SELECT user_id, name FROM public.assets LIMIT 10;

-- Vergleiche mit deiner Session
-- In Streamlit: st.write(st.session_state["user"].email)
```

### Fehler: "column change_24h does not exist"

**Lösung:** Führe das Migration-Script aus:
```bash
# Im Supabase SQL Editor:
# Führe aus: supabase_assets_table_migration.sql
```

### Performance-Werte werden nicht angezeigt

**Prüfe:**
```sql
SELECT name, change_24h FROM public.assets;
```

Wenn `change_24h` `NULL` oder `0` ist:
```sql
UPDATE public.assets
SET change_24h = (RANDOM() * 10 - 5)::DECIMAL(10, 2);
```

---

## 📚 Weiterführende Themen

### Real-Time Updates (Supabase Realtime):

```python
# In utils.py
def subscribe_to_assets():
    supabase.table("assets") \
        .on("*", lambda payload: st.rerun()) \
        .subscribe()
```

### Export-Funktion:

```python
# In Demo.py
import pandas as pd

if st.button("Exportieren als CSV"):
    df = pd.DataFrame(assets)
    csv = df.to_csv(index=False)
    st.download_button("Download", csv, "portfolio.csv", "text/csv")
```

### Chart-Integration:

```python
import plotly.express as px

# Pie Chart: Asset-Verteilung
fig = px.pie(assets, values='current_value', names='name')
st.plotly_chart(fig)
```

---

## ✅ Checkliste

Nach dem Setup solltest du:

- [ ] Assets-Tabelle in Supabase erstellt
- [ ] Demo-Daten mit deiner Email eingefügt
- [ ] Page unter `localhost:8501` → 📈 Demo sichtbar
- [ ] Assets werden korrekt angezeigt
- [ ] Performance-Farben (grün/rot) funktionieren
- [ ] "Neu laden" Button funktioniert
- [ ] Mobile-Ansicht getestet

---

## 💬 Support

Bei Fragen oder Problemen:

**Email:** janick@icanhasbucket.de

**Häufige Fragen:**
- Siehe `SETUP_DATABASE.md` für allgemeine DB-Probleme
- Siehe `README.md` für App-Setup
- Siehe `CHANGELOG.md` für Updates

---

**Viel Erfolg! 🚀**

