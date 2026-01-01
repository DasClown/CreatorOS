# 🎯 CreatorOS

**All-in-One Management Platform für Content Creator**

Eine Multi-Page Streamlit App mit Supabase Backend für Fan-Management, Finanz-Tracking und Content-Processing.

---

## 🚀 Features

### 1. 🎯 **Dashboard**
- Übersicht über alle wichtigen KPIs
- Quick Navigation zu allen Modulen
- User Status (FREE/PRO/ADMIN)

### 2. 💎 **CRM - Fan Management**
- Fan-Datenbank mit Status-Tracking (New, Regular, VIP, Whale)
- Multi-Platform Support (OnlyFans, Instagram, Twitter, etc.)
- Umsatz-Tracking pro Fan
- Live-Editing in der Tabelle
- Export als CSV/JSON

### 3. 💸 **Finance Tracking**
- Einnahmen & Ausgaben buchen
- Automatische Gewinn-Berechnung
- Monatliche Charts & Analysen
- Kategorie-basierte Auswertungen
- Export-Funktionen

### 4. 🎨 **Content Factory**
- Metadaten-Entfernung (EXIF)
- Wasserzeichen hinzufügen (Text, tiled)
- Batch-Processing (bis zu X Bilder)
- ZIP-Download
- Live-Vorschau
- Export-Settings (PNG/JPEG, Qualität)

### 5. ⚙️ **Einstellungen**
- Account-Verwaltung
- Subscription-Status
- Admin Panel (User-Management)
- Wasserzeichen-Einstellungen

---

## 📦 Installation

### 1. Repository klonen
```bash
git clone https://github.com/DasClown/CreatorOS.git
cd creatorOS
```

### 2. Virtual Environment erstellen
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# oder
.venv\Scripts\activate     # Windows
```

### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 4. Supabase Setup

#### 4.1 Supabase Projekt erstellen
1. Gehe zu [supabase.com](https://supabase.com)
2. Erstelle ein neues Projekt
3. Kopiere **Project URL** und **anon/public Key**

#### 4.2 Secrets konfigurieren
Erstelle `.streamlit/secrets.toml`:

```toml
[supabase]
url = "https://your-project.supabase.co"
key = "your-anon-key"
```

#### 4.3 Datenbank-Tabellen anlegen

Öffne den **SQL Editor** in Supabase und führe folgende SQL-Dateien aus:

1. **User Settings** (bereits existiert in Supabase)
2. **Fans Table** → `supabase_fans_table.sql`
3. **Finance Table** → `supabase_finance_table.sql`

```bash
# Im Supabase SQL Editor:
# 1. Öffne supabase_fans_table.sql
# 2. Kopiere den Inhalt
# 3. Führe aus
# 4. Wiederhole für supabase_finance_table.sql
```

### 5. App starten
```bash
streamlit run Hello.py
```

Die App öffnet sich automatisch im Browser unter `http://localhost:8501`

---

## 🗂️ Projekt-Struktur

```
creatorOS/
├── Hello.py                          # 🎯 Entry Point & Dashboard
├── utils.py                          # 🔧 Shared Functions (Auth, DB)
├── requirements.txt                  # 📦 Python Dependencies
├── .gitignore                        # 🚫 Git Ignore
├── README.md                         # 📖 Diese Datei
│
├── .streamlit/
│   └── secrets.toml                  # 🔐 Supabase Credentials (nicht in Git!)
│
├── pages/                            # 📄 Streamlit Pages
│   ├── 1_💎_CRM.py                  # Fan-Management
│   ├── 2_💸_Finance.py              # Finanz-Tracking
│   ├── 3_🎨_Content_Factory.py      # Bild-Processing
│   └── 4_⚙️_Einstellungen.py        # Settings & Admin
│
└── SQL/                              # 🗄️ Supabase Schema
    ├── supabase_fans_table.sql       # CRM Tabelle
    └── supabase_finance_table.sql    # Finance Tabelle
```

---

## 🔐 Authentifizierung

### User Registration
1. Öffne die App
2. Klicke auf "Registrieren"
3. Gib Email & Passwort ein (min. 6 Zeichen)
4. Account wird in Supabase erstellt

### Login
1. Gib deine Email & Passwort ein
2. Session bleibt über alle Pages erhalten

### Admin-Zugang
Der User `janick@icanhasbucket.de` hat Admin-Rechte:
- Sieht Admin-Panel in Einstellungen
- Kann User zu PRO upgraden/downgraden
- Sieht alle User-Daten

---

## 💎 Freemium Model

### FREE Plan
- ✅ 1 Bild pro Batch (Content Factory)
- ✅ Fester Wasserzeichen-Text: "Created with CreatorOS"
- ✅ CRM & Finance unbegrenzt
- ❌ Keine Custom Watermarks
- ❌ Kein Logo-Upload

### PRO Plan
- ✅ Unbegrenzte Batch-Verarbeitung
- ✅ Custom Wasserzeichen-Text
- ✅ Logo-Upload (Coming Soon)
- ✅ Prioritäts-Support

**Upgrade:**  
[Stripe Payment Link](https://buy.stripe.com/28E8wO0W59Y46rM8rG6J200)

---

## 📊 Datenbank-Schema

### `user_settings`
```sql
- user_id (TEXT, PRIMARY KEY)
- email (TEXT)
- is_pro (BOOLEAN)
- watermark_text (TEXT)
- opacity (INTEGER)
- padding (INTEGER)
- output_format (TEXT)
- jpeg_quality (INTEGER)
```

### `fans`
```sql
- id (UUID, PRIMARY KEY)
- user_id (TEXT, FK)
- handle (TEXT)
- platform (TEXT)
- status (TEXT)
- total_spend (NUMERIC)
- notes (TEXT)
- created_at (TIMESTAMP)
```

### `finance_entries`
```sql
- id (UUID, PRIMARY KEY)
- user_id (TEXT, FK)
- type (TEXT: 'Einnahme' | 'Ausgabe')
- amount (NUMERIC)
- category (TEXT)
- description (TEXT)
- date (DATE)
- created_at (TIMESTAMP)
```

---

## 🛠️ Entwicklung

### Code-Style
- Python 3.8+
- Streamlit Best Practices
- Modular aufgebaut (utils.py für shared functions)
- Session State Management

### Neue Page hinzufügen
1. Erstelle `pages/X_🎨_Name.py`
2. Importiere utils: `from utils import check_auth, render_sidebar`
3. Füge Auth-Check hinzu: `user = check_auth()`
4. Rendere Sidebar: `render_sidebar()`
5. Streamlit erstellt automatisch Navigation

### Neue Tabelle hinzufügen
1. Erstelle SQL-Schema in `supabase_*.sql`
2. Füge in Supabase SQL Editor ein
3. Erstelle Loader-Funktion in Page
4. Nutze Caching: `@st.cache_data(ttl=10)`

---

## 🚀 Deployment

### Streamlit Cloud
1. Pushe Code zu GitHub
2. Gehe zu [share.streamlit.io](https://share.streamlit.io)
3. Verbinde Repository
4. Setze Secrets in Streamlit Cloud Dashboard
5. Deploy!

### Secrets in Streamlit Cloud
```toml
[supabase]
url = "https://your-project.supabase.co"
key = "your-anon-key"
```

---

## 📝 TODO / Roadmap

### Phase 1 (✅ Completed)
- [x] Multi-Page App Setup
- [x] Supabase Auth Integration
- [x] CRM mit Fan-Management
- [x] Finance Tracking
- [x] Content Factory (Watermarks)
- [x] Admin Panel
- [x] Freemium Model

### Phase 2 (🚧 In Progress)
- [ ] Logo-Upload für Wasserzeichen
- [ ] Advanced Charts (Plotly)
- [ ] Email-Benachrichtigungen
- [ ] API-Integration (OnlyFans, Fansly)

### Phase 3 (📋 Planned)
- [ ] Mobile-Optimierung
- [ ] Dunkelmodus
- [ ] Multi-Language Support
- [ ] Backup & Restore
- [ ] Team-Funktionen

---

## 🐛 Troubleshooting

### App startet nicht
```bash
# Prüfe Python-Version
python --version  # Sollte 3.8+ sein

# Prüfe ob venv aktiviert ist
which python  # Sollte auf .venv/bin/python zeigen

# Reinstalliere Dependencies
pip install --upgrade -r requirements.txt
```

### Supabase Connection Error
1. Prüfe `.streamlit/secrets.toml`
2. Verifiziere URL & Key im Supabase Dashboard
3. Prüfe RLS Policies (sollten für user_id funktionieren)

### Tabelle nicht gefunden
```bash
# Stelle sicher, dass alle SQL-Skripte ausgeführt wurden
# Prüfe in Supabase > Table Editor
```

---

## 📧 Support

- **Email:** janick@icanhasbucket.de
- **GitHub Issues:** [CreatorOS Issues](https://github.com/DasClown/CreatorOS/issues)
- **Website:** [creatordeckapp.com](https://creatordeckapp.com)

---

## 📄 Lizenz

© 2025 CreatorDeck  
[Impressum](https://creatordeckapp.com/impressum) | [Datenschutz](https://creatordeckapp.com/datenschutz)

---

## 🙏 Credits

- Built with [Streamlit](https://streamlit.io)
- Backend: [Supabase](https://supabase.com)
- Payments: [Stripe](https://stripe.com)
- Made with ❤️ for Content Creators

