# ⚡ Quick Sync Setup - 5 Minuten

## Ziel

**1-Klick Social Stats Sync** direkt im Dashboard.

---

## Setup (3 Schritte)

### 1️⃣ YouTube API-Key erstellen

```
1. https://console.cloud.google.com/
2. Neues Projekt → "CreatorOS"
3. APIs & Services → Library → "YouTube Data API v3" → Enable
4. Credentials → Create Credentials → API Key
5. Key kopieren
```

### 2️⃣ API-Key zu secrets.toml hinzufügen

```bash
# Öffne:
nano .streamlit/secrets.toml

# Füge hinzu:
YOUTUBE_API_KEY = "AIzaSy_DEIN_KEY_HIER"
```

### 3️⃣ YouTube Channel ID in Datenbank eintragen

**Option A: Via Supabase Dashboard (Empfohlen)**

```
1. Gehe zu https://supabase.com/dashboard
2. Table Editor → channels
3. Suche deinen YouTube-Kanal
4. Bearbeite die Zeile
5. Füge zu "notes" hinzu: UCxxxxxxxxxxxxxxxxxxxxxx
6. Save
```

**Option B: Via SQL**

```sql
-- Ersetze mit deiner Email und Channel ID
UPDATE public.channels
SET notes = 'UCxxxxxxxxxxxxxxxxxxxxxx'
WHERE platform = 'YouTube' 
AND user_id = 'deine-email@example.com';
```

---

## YouTube Channel ID finden

```
1. Gehe zu: youtube.com/@yourhandle
2. Klicke auf deinen Kanal
3. URL wird zu: youtube.com/channel/UCxxxxxx
4. Kopiere die ID (UCxxxxxxxxxxxxxxxxxxxxxx)
5. Die ID hat 24 Zeichen und beginnt mit "UC"
```

---

## Nutzung

### Im Dashboard:

```
1. Öffne Dashboard (🏠)
2. Sidebar → 🔄 Social Stats Sync
3. Klick!
4. ✅ "YouTube synchronisiert!"
5. Zahlen sind aktualisiert
```

**Fertig!** 🎉

---

## Alternative: Manuelle Channel-IDs Config

Falls du Channel IDs lieber zentral verwalten willst:

```bash
# Erstelle channel_ids.toml
cp .streamlit/channel_ids.toml.example .streamlit/channel_ids.toml

# Bearbeite:
nano .streamlit/channel_ids.toml
```

```toml
[youtube]
"@JanickTech" = "UCxxxxxxxxxxxxxxxxxxxxxx"
"@CreatorChannel" = "UCyyyyyyyyyyyyyyyyyyyyy"
```

**Hinweis:** Das Dashboard liest aktuell aus den **notes** in der Datenbank. Die channel_ids.toml ist für zukünftige Erweiterungen.

---

## Beispiel-Code für eigenes Setup

Falls du den Sync-Button anders implementieren willst:

```python
from utils import fetch_youtube_stats, update_channel_in_db

# Deine YouTube Channel ID
YT_CHANNEL_ID = "UCxxxxxxxxxxxxxxxxxxxxxx"

# Button in Sidebar
with st.sidebar:
    if st.button("🔄 YouTube Sync"):
        with st.spinner("Lade Live-Daten..."):
            # 1. Stats holen
            yt_data = fetch_youtube_stats(YT_CHANNEL_ID)
            
            if yt_data:
                # 2. In DB speichern
                update_channel_in_db(
                    platform="YouTube",
                    handle="@JanickTech",  # Dein Handle aus DB
                    value_main=yt_data['subscribers']
                )
                
                st.success(f"✅ Synchronisiert: {yt_data['subscribers']:,} Subs")
                st.rerun()
```

---

## Troubleshooting

### Button erscheint nicht

```
Prüfe:
1. YOUTUBE_API_KEY in secrets.toml vorhanden?
2. google-api-python-client installiert?
   → pip install google-api-python-client
3. App neu gestartet?
```

### "Keine YouTube-Kanäle mit Channel ID gefunden"

```
Lösung:
1. Gehe zu Supabase → Table Editor → channels
2. Suche deinen YouTube-Kanal
3. Füge die Channel ID zu "notes" hinzu
4. Format: UCxxxxxxxxxxxxxxxxxxxxxx (24 Zeichen)
```

### "YouTube API Fehler"

```
Prüfe:
1. API-Key korrekt?
2. YouTube Data API v3 aktiviert?
3. Channel ID korrekt? (24 Zeichen, beginnt mit UC)
4. Quotas nicht überschritten? (Max 10.000/Tag)
```

---

## Automatisierung (Optional)

### Stündlicher Auto-Sync

```python
# In Hello.py oder Dashboard hinzufügen:
import time
from datetime import datetime

# Auto-Sync alle 60 Minuten
if "last_sync" not in st.session_state:
    st.session_state["last_sync"] = 0

current_time = time.time()
time_since_sync = current_time - st.session_state["last_sync"]

if time_since_sync > 3600:  # 1 Stunde = 3600 Sekunden
    # Auto-Sync ausführen
    yt_data = fetch_youtube_stats(YT_CHANNEL_ID)
    if yt_data:
        update_channel_in_db("YouTube", "@YourHandle", yt_data['subscribers'])
        st.session_state["last_sync"] = current_time
```

---

## Kosten

**YouTube Data API v3:**
- ✅ Kostenlos (10.000 Einheiten/Tag)
- ✅ 1 Sync = 1 Einheit
- ✅ Bis zu 10.000 Syncs/Tag möglich

**Empfehlung:** Maximal 1x pro Stunde synchronisieren.

---

## Nächste Schritte

1. ✅ YouTube API läuft
2. 🚧 Instagram Graph API (in Entwicklung)
3. 🚧 TikTok For Developers (geplant)

---

**Vollständige Dokumentation:** `API_INTEGRATION.md`

**Support:** janick@icanhasbucket.de

