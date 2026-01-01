# 🗄️ Datenbank Setup für CreatorOS

## Übersicht

CreatorOS nutzt **4 Haupttabellen** in Supabase. Diese müssen einmalig über den SQL Editor angelegt werden.

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

---

## 🔍 Verifizierung

### Prüfe ob alle Tabellen existieren:

1. Gehe zu **Table Editor** in Supabase
2. Du solltest folgende Tabellen sehen:
   - ✅ `user_settings`
   - ✅ `fans`
   - ✅ `finance_entries`
   - ✅ `tasks`

### Test-Query:

```sql
-- Prüfe Anzahl der Tabellen
SELECT 
    table_name, 
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public'
AND table_name IN ('user_settings', 'fans', 'finance_entries', 'tasks');
```

**Erwartetes Ergebnis:** 4 Zeilen

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

- [ ] Alle 4 Tabellen in Table Editor sehen
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

