-- =============================================================================
-- Supabase Table Definition für Fan-Management (CRM)
-- =============================================================================
-- 
-- Diese Tabelle in Supabase anlegen:
-- 1. Gehe zu Supabase Dashboard > Table Editor
-- 2. "New Table" klicken oder SQL Editor öffnen
-- 3. Diesen Code ausführen
-- 
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.fans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    handle TEXT NOT NULL,
    platform TEXT NOT NULL DEFAULT 'OnlyFans',
    status TEXT NOT NULL DEFAULT 'New',
    total_spend NUMERIC(10, 2) DEFAULT 0.00,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Index für schnelle Abfragen nach user_id
CREATE INDEX IF NOT EXISTS idx_fans_user_id ON public.fans(user_id);

-- Index für Status-Filter
CREATE INDEX IF NOT EXISTS idx_fans_status ON public.fans(status);

-- Row Level Security (RLS) aktivieren
ALTER TABLE public.fans ENABLE ROW LEVEL SECURITY;

-- Policy: User kann nur eigene Fans sehen
CREATE POLICY "Users can view own fans" ON public.fans
    FOR SELECT
    USING (auth.uid()::text = user_id OR auth.email() = user_id);

-- Policy: User kann eigene Fans erstellen
CREATE POLICY "Users can insert own fans" ON public.fans
    FOR INSERT
    WITH CHECK (auth.uid()::text = user_id OR auth.email() = user_id);

-- Policy: User kann eigene Fans aktualisieren
CREATE POLICY "Users can update own fans" ON public.fans
    FOR UPDATE
    USING (auth.uid()::text = user_id OR auth.email() = user_id);

-- Policy: User kann eigene Fans löschen
CREATE POLICY "Users can delete own fans" ON public.fans
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

CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON public.fans
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- =============================================================================
-- Kommentare für bessere Dokumentation
-- =============================================================================

COMMENT ON TABLE public.fans IS 'Speichert Fans und Kunden für das CRM-System';
COMMENT ON COLUMN public.fans.user_id IS 'Supabase User ID oder Email des App-Users';
COMMENT ON COLUMN public.fans.handle IS 'Username/Handle des Fans (z.B. @username)';
COMMENT ON COLUMN public.fans.platform IS 'Social Media Platform (OnlyFans, Instagram, etc.)';
COMMENT ON COLUMN public.fans.status IS 'Fan Status: New, Regular, VIP, Whale, Time-Waster';
COMMENT ON COLUMN public.fans.total_spend IS 'Gesamtumsatz des Fans in Euro';
COMMENT ON COLUMN public.fans.notes IS 'Interne Notizen zum Fan';

