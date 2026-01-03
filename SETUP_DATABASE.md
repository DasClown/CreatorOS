# 🗄️ Datenbank Setup für CreatorOS

## Übersicht

CreatorOS nutzt **7 Haupttabellen** in Supabase. Diese müssen einmalig über den SQL Editor angelegt werden.

---

## 📋 Setup-Anleitung

### 1. Supabase Dashboard öffnen
- Gehe zu [supabase.com](https://supabase.com)
- Öffne dein Projekt
- Navigiere zu **SQL Editor**

### 2. Tabellen erstellen

Führe folgende SQL-Dateien **in dieser Reihenfolge** aus:

#### ✅ Schritt 1: User Settings (Optional)
> Diese Tabelle sollte bereits existieren, wenn du die Auth nutzt.

Falls nicht, erstelle sie manuell:
```sql
CREATE TABLE IF NOT EXISTS public.user_settings (
    user_id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    is_pro BOOLEAN DEFAULT FALSE,
    watermark_text TEXT DEFAULT '© CreatorOS',
    opacity INTEGER DEFAULT 180,
    padding INTEGER DEFAULT 50,
    output_format TEXT DEFAULT 'PNG',
    jpeg_quality INTEGER DEFAULT 85,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;
```

#### ✅ Schritt 2: Fans (CRM)
**Datei:** `supabase_fans_table.sql`

```bash
# Im SQL Editor:
# 1. Öffne die Datei supabase_fans_table.sql
# 2. Kopiere den gesamten Inhalt
# 3. Füge in SQL Editor ein
# 4. Klicke "Run"
```

**Features:**
- Fan-Management mit Status-Tracking
- Platform-Support (OnlyFans, Instagram, etc.)
- Umsatz-Tracking
- Row Level Security (RLS)

#### ✅ Schritt 3: Finance
**Datei:** `supabase_finance_table.sql`

```bash
# Im SQL Editor:
# 1. Öffne die Datei supabase_finance_table.sql
# 2. Kopiere den gesamten Inhalt
# 3. Füge in SQL Editor ein
# 4. Klicke "Run"
```

**Features:**
- Einnahmen & Ausgaben
- Kategorie-basierte Auswertungen
- Monatliche Views
- Check Constraints für Datenintegrität

#### ✅ Schritt 4: Tasks (Planner)
**Datei:** `supabase_tasks_table.sql`

```bash
# Im SQL Editor:
# 1. Öffne die Datei supabase_tasks_table.sql
# 2. Kopiere den gesamten Inhalt
# 3. Füge in SQL Editor ein
# 4. Klicke "Run"
```

**Features:**
- Task-Management mit Prioritäten
- Fälligkeitsdatum-Tracking
- Automatisches Completion-Tracking
- Überfälligkeits-Views

#### ✅ Schritt 5: Assets (Portfolio/Demo)
**Datei:** `supabase_assets_table.sql`

```bash
# Im SQL Editor:
# 1. Öffne die Datei supabase_assets_table.sql
# 2. Kopiere den gesamten Inhalt
# 3. Füge in SQL Editor ein
# 4. Klicke "Run"
```

**Features:**
- Portfolio-Management (Stocks, Crypto, ETFs)
- Asset-Tracking mit Mengen & Werten
- Performance-Berechnung
- Sortierung nach Wert
- Trade Republic Style Demo-Page

#### ✅ Schritt 6: Channels (Social Media)
**Datei:** `supabase_channels_table.sql`

```bash
# Im SQL Editor:
# 1. Öffne die Datei supabase_channels_table.sql
# 2. Kopiere den gesamten Inhalt
# 3. Füge in SQL Editor ein
# 4. Klicke "Run"
```

**Features:**
- Social Media Channel Management (Instagram, YouTube, TikTok, etc.)
- Reichweiten-Tracking (Follower, Subscribers)
- Engagement-Rate Monitoring
- 30-Tage Wachstums-Tracking
- Primary Channel Markierung
- Icon-Support für visuelle Darstellung

#### ✅ Schritt 7: Deals (Kooperationen & Brand Deals)
**Datei:** `supabase_deals_table.sql`

```bash
# Im SQL Editor:
# 1. Öffne die Datei supabase_deals_table.sql
# 2. Kopiere den gesamten Inhalt
# 3. Füge in SQL Editor ein
# 4. Klicke "Run"
```

**Features:**
- Deal & Collaboration Management
- Brand Partnership Tracking
- Pipeline Value Monitoring
- Deadline/Due Date Tracking
- Status-Workflow (Negotiation → Completed)
- Revenue-Tracking pro Deal
- Overdue-Alerts
- Contact Management

---

## 🔍 Verifizierung

### Prüfe ob alle Tabellen existieren:

1. Gehe zu **Table Editor** in Supabase
2. Du solltest folgende Tabellen sehen:
   - ✅ `user_settings`
   - ✅ `fans`
   - ✅ `finance_entries`
   - ✅ `tasks`
   - ✅ `assets`
   - ✅ `channels`
   - ✅ `deals`

### Test-Query:

```sql
-- Prüfe Anzahl der Tabellen
SELECT 
    table_name, 
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public'
AND table_name IN ('user_settings', 'fans', 'finance_entries', 'tasks', 'assets', 'channels', 'deals');
```

**Erwartetes Ergebnis:** 7 Zeilen

---

## 🔐 Row Level Security (RLS)

Alle Tabellen haben **RLS aktiviert**. Das bedeutet:

- ✅ Jeder User sieht nur seine eigenen Daten
- ✅ Keine Cross-User Datenlecks
- ✅ Automatische Filterung via `user_id`

### RLS Policies prüfen:

```sql
-- Zeige alle Policies
SELECT 
    schemaname, 
    tablename, 
    policyname, 
    roles, 
    cmd
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

**Erwartete Policies pro Tabelle:**
- `Users can view own X`
- `Users can insert own X`
- `Users can update own X`
- `Users can delete own X`

---

## 📊 Datenbank-Schema Übersicht

### `user_settings`
```
user_id (TEXT, PK)
├── email (TEXT)
├── is_pro (BOOLEAN)
├── watermark_text (TEXT)
├── opacity (INTEGER)
├── padding (INTEGER)
├── output_format (TEXT)
└── jpeg_quality (INTEGER)
```

### `fans`
```
id (UUID, PK)
├── user_id (TEXT, FK)
├── handle (TEXT)
├── platform (TEXT)
├── status (TEXT)
├── total_spend (NUMERIC)
├── notes (TEXT)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

### `finance_entries`
```
id (UUID, PK)
├── user_id (TEXT, FK)
├── type (TEXT: Einnahme|Ausgabe)
├── amount (NUMERIC)
├── category (TEXT)
├── description (TEXT)
├── date (DATE)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

### `tasks`
```
id (UUID, PK)
├── user_id (TEXT, FK)
├── title (TEXT)
├── due_date (DATE)
├── category (TEXT)
├── priority (TEXT: High|Medium|Low)
├── status (TEXT: Open|In Progress|Done)
├── description (TEXT)
├── created_at (TIMESTAMP)
├── updated_at (TIMESTAMP)
└── completed_at (TIMESTAMP)
```

### `assets`
```
id (UUID, PK)
├── user_id (TEXT, FK)
├── name (TEXT)
├── ticker (TEXT)
├── asset_type (TEXT: Stock|Crypto|ETF|Other)
├── quantity (NUMERIC)
├── purchase_price (NUMERIC)
├── current_value (NUMERIC)
├── change_24h (NUMERIC)           -- Performance letzte 24h in % (z.B. +2.4 oder -1.5)
├── last_updated (TIMESTAMP)
└── created_at (TIMESTAMP)
```

### `channels`
```
id (UUID, PK)
├── user_id (TEXT, FK)
├── platform (TEXT)                -- Instagram, YouTube, TikTok, etc.
├── handle (TEXT)                  -- @username
├── metric_main (TEXT)             -- Formatierte Anzeige (z.B. "125.5k Follower")
├── value_main (BIGINT)            -- Follower/Subscribers (Zahlenwert)
├── value_label (TEXT)             -- "Follower", "Subscribers", etc.
├── engagement_rate (NUMERIC)      -- Engagement-Rate in % (z.B. 3.8)
├── avg_views (BIGINT)             -- Durchschnittliche Views
├── change_24h (NUMERIC)           -- Performance 24h in % (z.B. +2.4)
├── growth_30d (NUMERIC)           -- Wachstum 30 Tage in % (z.B. +12.4)
├── revenue_mtd (NUMERIC)          -- Einnahmen Month-to-Date in € (z.B. 1250.50)
├── platform_icon (TEXT)           -- Emoji (z.B. "📸", "📺")
├── is_primary (BOOLEAN)           -- Hauptkanal?
├── notes (TEXT)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

### `deals`
```
id (UUID, PK)
├── user_id (TEXT, FK)
├── brand_name (TEXT)              -- Marke/Unternehmen (z.B. "Nike")
├── deal_type (TEXT)               -- Typ: "Sponsored Post", "Brand Ambassador", etc.
├── platform (TEXT)                -- Plattform für den Deal
├── status (TEXT)                  -- Status: Negotiation, Confirmed, In Progress, Completed, Cancelled
├── amount (NUMERIC)               -- Deal-Wert in € (z.B. 2500.00)
├── currency (TEXT)                -- Währung (EUR, USD, etc.)
├── due_date (DATE)                -- Fälligkeitsdatum / Deadline
├── deliverables (TEXT)            -- Was ist zu liefern?
├── notes (TEXT)                   -- Notizen zum Deal
├── contact_person (TEXT)          -- Ansprechpartner
├── contact_email (TEXT)           -- Email des Ansprechpartners
├── created_at (TIMESTAMP)
├── updated_at (TIMESTAMP)
└── completed_at (TIMESTAMP)       -- Automatisch gesetzt bei Status = "Completed"
```

---

## 🧪 Test-Daten (Optional)

Jede SQL-Datei enthält **kommentierte Test-Daten** am Ende.

Um Test-Daten zu erstellen:

1. Öffne die jeweilige SQL-Datei
2. Scrolle zum Ende (Abschnitt "Beispiel-Daten")
3. Entferne die `/* */` Kommentare
4. Ändere `test@example.com` zu deiner Email
5. Führe aus

**Beispiel:**
```sql
-- In supabase_fans_table.sql
INSERT INTO public.fans (user_id, handle, platform, status, total_spend) VALUES
    ('deine-email@example.com', '@testuser', 'OnlyFans', 'Whale', 1500.00);
```

---

## 🔄 Migrations (Bei Updates)

Wenn eine neue Version von CreatorOS neue Spalten/Tabellen benötigt:

1. Prüfe `CHANGELOG.md` für Schema-Änderungen
2. Führe die entsprechenden ALTER-Statements aus
3. **Niemals** bestehende Tabellen droppen (Datenverlust!)

### Migration: Assets Tabelle (change_24h Feld)

Falls du die `assets` Tabelle bereits **ohne** das `change_24h` Feld erstellt hast:

**Option 1: Migration Script ausführen**
```bash
# Im Supabase SQL Editor:
# Führe aus: supabase_assets_table_migration.sql
```

**Option 2: Manuell hinzufügen**
```sql
ALTER TABLE public.assets 
ADD COLUMN IF NOT EXISTS change_24h DECIMAL(10, 2) DEFAULT 0;
```

**Beispiel Migration:**
```sql
-- Neue Spalte zu fans hinzufügen
ALTER TABLE public.fans 
ADD COLUMN IF NOT EXISTS last_contact DATE;
```

---

## 🐛 Troubleshooting

### Fehler: "permission denied for table X"
**Lösung:** RLS ist aktiv, aber keine Policies definiert.
```sql
-- Policies erneut ausführen (siehe entsprechende SQL-Datei)
```

### Fehler: "relation X already exists"
**Lösung:** Tabelle existiert bereits. Überspringe CREATE, führe nur ALTER/INDEX aus.

### Fehler: "function gen_random_uuid() does not exist"
**Lösung:** UUID Extension aktivieren:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- oder
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

### Fehler: "check constraint X is violated"
**Lösung:** Prüfe Daten-Constraints:
- `finance_entries.type` muss 'Einnahme' oder 'Ausgabe' sein
- `finance_entries.amount` muss > 0 sein
- `tasks.priority` muss 'High', 'Medium' oder 'Low' sein
- `tasks.status` muss 'Open', 'In Progress' oder 'Done' sein

---

## ✅ Checkliste

Nach dem Setup solltest du:

- [ ] Alle 7 Tabellen in Table Editor sehen
- [ ] RLS aktiviert für alle Tabellen
- [ ] Policies existieren für alle Tabellen
- [ ] Indizes erstellt (prüfe in Database > Indexes)
- [ ] Trigger funktionieren (`updated_at` wird automatisch gesetzt)
- [ ] Test-Insert funktioniert ohne Fehler

**Test-Insert:**
```sql
-- Teste mit deiner Email
INSERT INTO public.fans (user_id, handle, platform, status, total_spend, notes)
VALUES ('deine-email@example.com', '@testfan', 'OnlyFans', 'New', 0.00, 'Test-Eintrag');

-- Wenn erfolgreich, lösche wieder:
DELETE FROM public.fans WHERE handle = '@testfan';
```

---

## 📚 Weitere Ressourcen

- [Supabase Docs - Tables](https://supabase.com/docs/guides/database/tables)
- [Supabase Docs - RLS](https://supabase.com/docs/guides/auth/row-level-security)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

## 💡 Backup

**Wichtig:** Erstelle regelmäßig Backups!

```sql
-- Exportiere alle Daten (via Supabase Dashboard)
-- Settings > Database > Backups > Create Backup
```

Oder nutze `pg_dump`:
```bash
pg_dump -h db.your-project.supabase.co -U postgres -d postgres > backup.sql
```

---

**Bei Fragen:** janick@icanhasbucket.de

