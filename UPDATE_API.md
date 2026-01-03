# 🔄 Update Guide: YouTube API-Integration

## Quick Update

```bash
# 1. Aktiviere virtuelle Umgebung
cd /Users/janickthum/Desktop/creatorOS
source .venv/bin/activate

# 2. Installiere neue Dependencies
pip install google-api-python-client pandas

# 3. Erstelle secrets.toml (falls noch nicht vorhanden)
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# 4. Füge YouTube API-Key hinzu
# Öffne .streamlit/secrets.toml und füge hinzu:
# YOUTUBE_API_KEY = "dein-api-key-hier"

# 5. Starte die App
streamlit run Hello.py
```

---

## Was ist neu?

✅ **YouTube API-Integration**
- Automatische Synchronisation von Subscriber-Zahlen
- Über UI: Gehe zu **📊 Channels** → **🔄 API-Sync**

✅ **Neue Dependencies**
- `google-api-python-client` (YouTube API)
- `pandas` (Datenverarbeitung)

✅ **Neue Funktionen in utils.py**
- `fetch_youtube_stats()` → Holt YouTube-Statistiken
- `update_channel_in_db()` → Aktualisiert Datenbank
- `sync_youtube_channel()` → Kompletter Sync-Workflow

---

## YouTube API-Key erstellen

### 1. Google Cloud Console öffnen
https://console.cloud.google.com/

### 2. Neues Projekt erstellen (oder bestehendes wählen)

### 3. YouTube Data API v3 aktivieren
1. **APIs & Services** → **Library**
2. Suche "YouTube Data API v3"
3. Klicke **Enable**

### 4. API-Key erstellen
1. **APIs & Services** → **Credentials**
2. **Create Credentials** → **API Key**
3. Kopiere den Key
4. Füge ihn zu `.streamlit/secrets.toml` hinzu:

```toml
# .streamlit/secrets.toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
YOUTUBE_API_KEY = "AIzaSy_YOUR_API_KEY_HERE"  # ← NEU
```

---

## YouTube Channel ID finden

**Option 1: Via Browser**
```
1. Gehe zu deinem YouTube-Kanal
2. URL ist: youtube.com/@YourHandle
3. Klicke auf den Kanal
4. URL ändert sich zu: youtube.com/channel/UCxxxxxx...
5. Der Teil nach /channel/ ist deine Channel ID
```

**Option 2: Via YouTube Studio**
```
1. Gehe zu studio.youtube.com
2. Settings → Advanced
3. Kopiere "Channel ID"
```

**Format:** UCxxxxxxxxxxxxxxxxxxxxxx (24 Zeichen)

---

## Erste Synchronisation

### Via UI:

1. Starte die App: `streamlit run Hello.py`
2. Gehe zu **📊 Channels** (in Sidebar)
3. Scrolle nach unten zu **🔄 API-Sync**
4. Öffne **"YouTube-Statistiken aktualisieren"**
5. Gib deine **YouTube Channel ID** ein
6. Klicke **🔄 Sync**
7. ✅ Erfolgsmeldung → Subscriber-Zahlen sind aktualisiert!

### Via Python (Testing):

```python
# In Python Console:
from utils import fetch_youtube_stats

# Test mit YouTube Creator Academy Channel
test_id = "UCuAXFkgsw1L7xaCfnd5JJOw"
stats = fetch_youtube_stats(test_id)
print(stats)

# Output:
# {
#     'subscribers': 500000,
#     'view_count': 10000000,
#     'video_count': 200,
#     'channel_title': 'YouTube Creator Academy'
# }
```

---

## Troubleshooting

### ImportError: No module named 'googleapiclient'

```bash
# Lösung:
pip install google-api-python-client
```

### Fehler: "YouTube API nicht verfügbar"

```bash
# Prüfe Installation:
pip show google-api-python-client

# Wenn nicht installiert:
pip install google-api-python-client
```

### Fehler: "YOUTUBE_API_KEY nicht gefunden"

```bash
# Lösung:
# 1. Prüfe ob .streamlit/secrets.toml existiert
ls -la .streamlit/secrets.toml

# 2. Öffne und prüfe Inhalt:
cat .streamlit/secrets.toml

# 3. Füge hinzu:
# YOUTUBE_API_KEY = "dein-key-hier"
```

### Fehler: "API key not valid"

```
Lösung:
1. Prüfe ob YouTube Data API v3 in Google Cloud Console aktiviert ist
2. Warte 1-2 Minuten nach Key-Erstellung
3. Stelle sicher, dass der Key korrekt kopiert wurde (keine Leerzeichen)
```

---

## Dateien, die geändert wurden

```
✅ utils.py                              (API-Funktionen hinzugefügt)
✅ pages/8_📊_Channels.py                (API-Sync UI hinzugefügt)
✅ requirements.txt                      (google-api-python-client, pandas)
✅ .streamlit/secrets.toml.example       (NEU - Vorlage für API-Keys)
✅ API_INTEGRATION.md                    (NEU - Vollständige Dokumentation)
✅ UPDATE_API.md                         (NEU - Diese Datei)
```

---

## Nächste Schritte (Optional)

1. **Automatisierung:** Setze einen Cron-Job für stündliche Syncs
2. **Instagram API:** Erweitere um Instagram Graph API
3. **TikTok API:** Bewerbe dich für TikTok Developer Access
4. **Monitoring:** Überwache API-Quotas in Google Cloud Console

---

## Weitere Hilfe

📚 **Dokumentation:** `API_INTEGRATION.md` (vollständige Anleitung)  
💬 **Support:** janick@icanhasbucket.de  
🐛 **Issues:** Check `API_INTEGRATION.md` → Troubleshooting

---

**Viel Erfolg mit der YouTube API-Integration! 🎉**

