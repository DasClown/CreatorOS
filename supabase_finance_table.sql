-- =============================================================================
-- Supabase Table Definition für Finance Tracking
-- =============================================================================
-- 
-- Diese Tabelle in Supabase anlegen:
-- 1. Gehe zu Supabase Dashboard > Table Editor
-- 2. "New Table" klicken oder SQL Editor öffnen
-- 3. Diesen Code ausführen
-- 
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.finance_entries (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('Einnahme', 'Ausgabe')),
    amount NUMERIC(10, 2) NOT NULL CHECK (amount > 0),
    category TEXT NOT NULL,
    description TEXT,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Index für schnelle Abfragen nach user_id
CREATE INDEX IF NOT EXISTS idx_finance_user_id ON public.finance_entries(user_id);

-- Index für Datums-Abfragen (wichtig für monatliche Auswertungen)
CREATE INDEX IF NOT EXISTS idx_finance_date ON public.finance_entries(date DESC);

-- Index für Typ-Filter
CREATE INDEX IF NOT EXISTS idx_finance_type ON public.finance_entries(type);

-- Index für Kategorie-Analysen
CREATE INDEX IF NOT EXISTS idx_finance_category ON public.finance_entries(category);

-- Composite Index für User + Datum (Performance-Boost für Dashboards)
CREATE INDEX IF NOT EXISTS idx_finance_user_date ON public.finance_entries(user_id, date DESC);

-- Row Level Security (RLS) aktivieren
ALTER TABLE public.finance_entries ENABLE ROW LEVEL SECURITY;

-- Policy: User kann nur eigene Einträge sehen
CREATE POLICY "Users can view own finance entries" ON public.finance_entries
    FOR SELECT
    USING (auth.uid()::text = user_id OR auth.email() = user_id);

-- Policy: User kann eigene Einträge erstellen
CREATE POLICY "Users can insert own finance entries" ON public.finance_entries
    FOR INSERT
    WITH CHECK (auth.uid()::text = user_id OR auth.email() = user_id);

-- Policy: User kann eigene Einträge aktualisieren
CREATE POLICY "Users can update own finance entries" ON public.finance_entries
    FOR UPDATE
    USING (auth.uid()::text = user_id OR auth.email() = user_id);

-- Policy: User kann eigene Einträge löschen
CREATE POLICY "Users can delete own finance entries" ON public.finance_entries
    FOR DELETE
    USING (auth.uid()::text = user_id OR auth.email() = user_id);

-- Trigger für updated_at
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at_finance
    BEFORE UPDATE ON public.finance_entries
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- =============================================================================
-- Views für häufige Abfragen (Optional, aber empfohlen für Performance)
-- =============================================================================

-- View: Monatliche Zusammenfassung pro User
CREATE OR REPLACE VIEW public.finance_monthly_summary AS
SELECT 
    user_id,
    DATE_TRUNC('month', date) as month,
    type,
    SUM(amount) as total_amount,
    COUNT(*) as entry_count
FROM public.finance_entries
GROUP BY user_id, DATE_TRUNC('month', date), type
ORDER BY month DESC, type;

-- View: Kategorie-Zusammenfassung pro User
CREATE OR REPLACE VIEW public.finance_category_summary AS
SELECT 
    user_id,
    type,
    category,
    SUM(amount) as total_amount,
    COUNT(*) as entry_count,
    AVG(amount) as avg_amount
FROM public.finance_entries
GROUP BY user_id, type, category
ORDER BY total_amount DESC;

-- =============================================================================
-- Kommentare für bessere Dokumentation
-- =============================================================================

COMMENT ON TABLE public.finance_entries IS 'Speichert Einnahmen und Ausgaben für das Finance-Tracking';
COMMENT ON COLUMN public.finance_entries.user_id IS 'Supabase User ID oder Email des App-Users';
COMMENT ON COLUMN public.finance_entries.type IS 'Art der Buchung: Einnahme oder Ausgabe';
COMMENT ON COLUMN public.finance_entries.amount IS 'Betrag in Euro (immer positiv)';
COMMENT ON COLUMN public.finance_entries.category IS 'Kategorie der Buchung (z.B. OnlyFans, Technik, etc.)';
COMMENT ON COLUMN public.finance_entries.description IS 'Optional: Zusätzliche Beschreibung';
COMMENT ON COLUMN public.finance_entries.date IS 'Datum der Buchung';

-- =============================================================================
-- Beispiel-Daten (Optional, für Testing)
-- =============================================================================

-- Uncomment um Test-Daten zu erstellen:
/*
INSERT INTO public.finance_entries (user_id, type, amount, category, description, date) VALUES
    ('test@example.com', 'Einnahme', 1500.00, 'OnlyFans', 'Monatliche Subscriptions', '2025-01-01'),
    ('test@example.com', 'Einnahme', 800.00, 'Fansly', 'Custom Content', '2025-01-05'),
    ('test@example.com', 'Ausgabe', 299.99, 'Technik & Equipment', 'Neue Kamera', '2025-01-10'),
    ('test@example.com', 'Ausgabe', 50.00, 'Werbung & Marketing', 'Instagram Ads', '2025-01-15');
*/

