-- =============================================================================
-- CreatorOS: Assets Table (Portfolio Management)
-- =============================================================================
-- Diese Tabelle speichert Investments/Assets für das Portfolio-Feature
-- Verwendung: Demo-Page, Finance-Tracking, Investment-Übersicht

-- 1. Erstelle die Tabelle
CREATE TABLE IF NOT EXISTS public.assets (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,                  -- Asset Name (z.B. "Apple Inc.", "Bitcoin")
    ticker TEXT,                         -- Ticker Symbol (z.B. "AAPL", "BTC")
    asset_type TEXT NOT NULL,            -- Typ: "Stock", "Crypto", "ETF", "Other"
    quantity DECIMAL(18, 8) DEFAULT 0,   -- Anzahl/Menge (z.B. 12 Aktien, 0.45 BTC)
    purchase_price DECIMAL(18, 2),       -- Einkaufspreis pro Einheit
    current_value DECIMAL(18, 2),        -- Aktueller Gesamtwert
    change_24h DECIMAL(10, 2) DEFAULT 0, -- Performance letzte 24h in Prozent (z.B. +2.4 oder -1.5)
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Erstelle Index für Performance
CREATE INDEX IF NOT EXISTS idx_assets_user_id ON public.assets(user_id);
CREATE INDEX IF NOT EXISTS idx_assets_current_value ON public.assets(current_value DESC);

-- 3. Row Level Security (RLS) aktivieren
ALTER TABLE public.assets ENABLE ROW LEVEL SECURITY;

-- 4. RLS Policy: User kann nur eigene Assets sehen
CREATE POLICY "Users can view own assets"
    ON public.assets
    FOR SELECT
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'email');

-- 5. RLS Policy: User kann eigene Assets erstellen
CREATE POLICY "Users can insert own assets"
    ON public.assets
    FOR INSERT
    WITH CHECK (user_id = current_setting('request.jwt.claims', true)::json->>'email');

-- 6. RLS Policy: User kann eigene Assets aktualisieren
CREATE POLICY "Users can update own assets"
    ON public.assets
    FOR UPDATE
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'email');

-- 7. RLS Policy: User kann eigene Assets löschen
CREATE POLICY "Users can delete own assets"
    ON public.assets
    FOR DELETE
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'email');

-- 8. Trigger: Auto-Update last_updated
CREATE OR REPLACE FUNCTION update_assets_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_assets_timestamp
    BEFORE UPDATE ON public.assets
    FOR EACH ROW
    EXECUTE FUNCTION update_assets_timestamp();

-- 9. View: Portfolio Summary pro User
CREATE OR REPLACE VIEW public.portfolio_summary AS
SELECT 
    user_id,
    COUNT(*) as total_assets,
    SUM(current_value) as total_value,
    asset_type,
    COUNT(*) as count_per_type
FROM public.assets
GROUP BY user_id, asset_type;

-- =============================================================================
-- DEMO DATA (Optional - für Testing)
-- =============================================================================
-- Hinweis: Ersetze 'demo@creatorOs.com' mit einer echten Test-User-Email

INSERT INTO public.assets (user_id, name, ticker, asset_type, quantity, purchase_price, current_value, change_24h)
VALUES 
    ('demo@creatorOs.com', 'Apple Inc.', 'AAPL', 'Stock', 12, 180.00, 2334.00, 2.4),
    ('demo@creatorOs.com', 'Tesla', 'TSLA', 'Stock', 5, 200.00, 1051.00, -1.2),
    ('demo@creatorOs.com', 'Bitcoin', 'BTC', 'Crypto', 0.45, 35000.00, 17775.00, 5.8),
    ('demo@creatorOs.com', 'Microsoft', 'MSFT', 'Stock', 8, 380.00, 3298.40, 0.9),
    ('demo@creatorOs.com', 'Ethereum', 'ETH', 'Crypto', 2.5, 2000.00, 5500.00, 3.2)
ON CONFLICT DO NOTHING;

-- =============================================================================
-- HINWEISE
-- =============================================================================
-- 1. Führe dieses SQL in Supabase SQL Editor aus
-- 2. RLS ist aktiviert - User können nur eigene Assets sehen
-- 3. Die View 'portfolio_summary' bietet aggregierte Daten
-- 4. Passe die Demo-Daten an oder lösche sie
-- 5. Für Echtzeit-Preise: Integriere externe API (z.B. Alpha Vantage, CoinGecko)
-- 6. Das Feld 'change_24h' speichert die Performance in Prozent (positiv/negativ)
-- 7. Für bestehende Tabellen: Nutze supabase_assets_table_migration.sql

