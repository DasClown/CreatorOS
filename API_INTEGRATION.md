# 🔌 API-Integration Guide für CreatorOS

## Übersicht

CreatorOS unterstützt automatische Synchronisation deiner Social Media Statistiken via APIs.

**Unterstützte APIs:**
- ✅ **YouTube Data API v3** (implementiert)
- 🚧 **Instagram Graph API** (geplant)
- 🚧 **TikTok For Developers** (geplant)
- 🚧 **Twitter API v2** (geplant)

---

## 📺 YouTube Data API v3

### Setup

#### 1. Google Cloud Projekt erstellen

1. Gehe zu [Google Cloud Console](https://console.cloud.google.com/)
2. Erstelle ein neues Projekt (oder wähle bestehendes)
3. Notiere dir die Projekt-ID

#### 2. YouTube Data API aktivieren

1. In der Console: **APIs & Services** → **Library**
2. Suche nach **"YouTube Data API v3"**
3. Klicke **Enable**

#### 3. API-Key erstellen

1. Gehe zu **APIs & Services** → **Credentials**
2. Klicke **Create Credentials** → **API Key**
3. Kopiere den generierten API-Key
4. **WICHTIG:** Klicke **Edit API Key** und beschränke ihn:
   - **Application restrictions:** HTTP referrers (Websites)
   - **API restrictions:** YouTube Data API v3

#### 4. API-Key zu secrets.toml hinzufügen

```toml
# .streamlit/secrets.toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
YOUTUBE_API_KEY = "AIzaSy_YOUR_API_KEY_HERE"
```

---

### YouTube Channel ID finden

**Methode 1: Via URL**
```
https://www.youtube.com/@ChannelHandle
→ Klicke auf den Kanal
→ URL wird zu: https://www.youtube.com/channel/UC...
→ Der Teil nach /channel/ ist deine Channel ID
```

**Methode 2: Via YouTube Studio**
```
1. Gehe zu studio.youtube.com
2. Settings → Advanced Settings
3. Kopiere "Channel ID"
```

**Format:** UCxxxxxxxxxxxxxxxxxxxxxx (24 Zeichen)

---

### Nutzung in CreatorOS

#### Via UI (Empfohlen):

1. Gehe zu **📊 Channels** in der Sidebar
2. Scrolle nach unten zu **🔄 API-Sync**
3. Öffne **"YouTube-Statistiken aktualisieren"**
4. Gib deine **YouTube Channel ID** ein
5. Klicke **🔄 Sync**

#### Via Python (Programmatisch):

```python
from utils import sync_youtube_channel

# Synchronisiere YouTube-Kanal
channel_id = "UCxxxxxxxxxxxxxxxxxxxxxx"
handle = "@yourhandle"

stats = sync_youtube_channel(channel_id, handle)

if stats:
    print(f"Subscribers: {stats['subscribers']}")
    print(f"Total Views: {stats['view_count']}")
    print(f"Videos: {stats['video_count']}")
```

---

### Was wird synchronisiert?

| Feld          | Quelle                        | Update in DB       |
|---------------|-------------------------------|--------------------|
| Subscribers   | `statistics.subscriberCount`  | `value_main`       |
| Total Views   | `statistics.viewCount`        | (Anzeige)          |
| Video Count   | `statistics.videoCount`       | (Anzeige)          |
| Channel Title | `snippet.title`               | (Verifizierung)    |

**Automatische Updates:**
- `value_main` → Subscriber-Zahl
- `metric_main` → Formatiert (z.B. "125.5k Subscribers")

---

### Quotas & Limits

**YouTube Data API v3 Quotas:**
- **Default:** 10.000 Einheiten/Tag
- **Kosten pro Request:**
  - `channels.list`: 1 Einheit
  - CreatorOS benötigt: **1 Einheit pro Sync**

**Maximale Syncs pro Tag:** ~10.000

**Tipp:** Synchronisiere maximal 1x pro Stunde, um Quotas zu schonen.

---

### Troubleshooting

#### Fehler: "API key not valid"
```
Lösung:
1. Prüfe ob der Key korrekt in secrets.toml ist
2. Stelle sicher, dass YouTube Data API v3 aktiviert ist
3. Warte 1-2 Minuten nach Key-Erstellung
```

#### Fehler: "Quota exceeded"
```
Lösung:
1. Warte bis Mitternacht (Pacific Time) für Reset
2. Reduziere Sync-Frequenz
3. Beantrage Quota-Erhöhung bei Google
```

#### Fehler: "Channel not found"
```
Lösung:
1. Prüfe ob Channel ID korrekt ist (24 Zeichen, beginnt mit "UC")
2. Stelle sicher, dass der Kanal öffentlich ist
3. Teste die ID in YouTube URL: youtube.com/channel/UC...
```

---

## 📸 Instagram Graph API (Geplant)

### Vorbereitung

**Hinweis:** Instagram API hat strikte Limitierungen für persönliche Accounts.

**Anforderungen:**
- Facebook Developer Account
- Instagram Business oder Creator Account
- Facebook Page verbunden mit Instagram

**API-Features:**
- Follower-Count
- Media-Count
- Engagement-Rate

**Status:** 🚧 In Entwicklung

---

## 🎵 TikTok For Developers (Geplant)

### Vorbereitung

**Anforderungen:**
- TikTok Developer Account (Bewerbung erforderlich)
- TikTok Business Account

**API-Features:**
- Follower-Count
- Video-Count
- Likes/Views

**Status:** 🚧 In Entwicklung

---

## 🐦 Twitter API v2 (Geplant)

### Vorbereitung

**Anforderungen:**
- Twitter Developer Account
- API Tier: Essential (kostenlos) oder höher

**API-Features:**
- Follower-Count
- Tweet-Count
- Engagement-Metrics

**Status:** 🚧 In Entwicklung

---

## 🔒 Sicherheit & Best Practices

### API-Keys schützen

```bash
# .gitignore muss enthalten:
.streamlit/secrets.toml
*.toml
!secrets.toml.example
```

### Key-Rotation

```
1. Erstelle neuen API-Key in Google Cloud Console
2. Update secrets.toml mit neuem Key
3. Teste Funktionalität
4. Lösche alten Key in Console
```

### Monitoring

```python
# Überwache API-Aufrufe in Google Cloud Console:
# "APIs & Services" → "Dashboard" → "YouTube Data API v3"
```

---

## 📊 Automatisierung

### Scheduled Syncs (Erweitert)

**Option 1: Streamlit Cloud (Empfohlen)**
```python
# Nutze Streamlit's st.rerun() mit Timer
import time

if time.time() % 3600 < 60:  # Jede Stunde
    sync_youtube_channel(channel_id, handle)
```

**Option 2: Cron Job**
```bash
# crontab -e
0 * * * * cd /path/to/creatorOS && python sync_channels.py
```

**Option 3: GitHub Actions**
```yaml
# .github/workflows/sync.yml
name: Sync Channels
on:
  schedule:
    - cron: '0 * * * *'  # Jede Stunde
```

---

## 💰 Kosten

| API                | Free Tier        | Kosten danach        |
|--------------------|------------------|----------------------|
| YouTube Data API   | 10k Einheiten/Tag| $0 (nur Quotas)      |
| Instagram Graph    | Kostenlos        | $0                   |
| TikTok             | Kostenlos        | $0                   |
| Twitter API        | 1.5k Tweets/mo   | $100/mo (Basic)      |

**CreatorOS Empfehlung:** Nutze nur kostenlose Tiers.

---

## 🧪 Testing

### Test-API-Key

```python
# In Python Console:
from utils import fetch_youtube_stats

# Test mit öffentlichem YouTube-Kanal
test_id = "UCuAXFkgsw1L7xaCfnd5JJOw"  # YouTube Creator Academy
stats = fetch_youtube_stats(test_id)
print(stats)
```

**Erwartete Ausgabe:**
```python
{
    'subscribers': 500000,
    'view_count': 10000000,
    'video_count': 200,
    'channel_title': 'YouTube Creator Academy'
}
```

---

## 📚 Weiterführende Links

- [YouTube Data API Docs](https://developers.google.com/youtube/v3)
- [Instagram Graph API Docs](https://developers.facebook.com/docs/instagram-api)
- [TikTok For Developers](https://developers.tiktok.com/)
- [Twitter API Docs](https://developer.twitter.com/en/docs/twitter-api)
- [Google Cloud Console](https://console.cloud.google.com/)

---

## ✅ Checkliste

Nach der API-Integration solltest du:

- [ ] YouTube API-Key erstellt und getestet
- [ ] API-Key in secrets.toml gespeichert
- [ ] YouTube Channel ID gefunden
- [ ] Ersten Sync erfolgreich durchgeführt
- [ ] Datenbank aktualisiert (value_main updated)
- [ ] Dashboard zeigt neue Werte
- [ ] Quotas im Blick (Google Cloud Console)

---

**Bei Fragen:** janick@icanhasbucket.de

**Aktuelle API-Status:**
- ✅ YouTube: Produktionsreif
- 🚧 Instagram: In Entwicklung
- 🚧 TikTok: Geplant
- 🚧 Twitter: Geplant

