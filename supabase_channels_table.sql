-- =============================================================================
-- CreatorOS: Channels Table (Social Media Channel Management)
-- =============================================================================
-- Diese Tabelle speichert Social Media Kanäle für Creator (Instagram, YouTube, etc.)
-- Verwendung: Analytics, Channel-Übersicht, Performance-Tracking

-- 1. Erstelle die Tabelle
CREATE TABLE IF NOT EXISTS public.channels (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    platform TEXT NOT NULL,              -- Plattform: "Instagram", "YouTube", "TikTok", "OnlyFans", etc.
    handle TEXT,                         -- Username/Handle (z.B. "@username")
    metric_main TEXT,                    -- Label für die Haupt-Metrik (z.B. "12.5k Follower", "8.2k Subscribers")
    value_main BIGINT DEFAULT 0,         -- Haupt-Metrik-Wert (Follower, Subscribers, etc.)
    value_label TEXT,                    -- Einheit (z.B. "Follower", "Subscribers")
    engagement_rate DECIMAL(5, 2),       -- Engagement-Rate in % (z.B. 3.5)
    avg_views BIGINT,                    -- Durchschnittliche Views pro Post/Video
    change_24h DECIMAL(10, 2) DEFAULT 0, -- Performance letzte 24h in % (z.B. +2.4 oder -1.5)
    growth_30d DECIMAL(10, 2),           -- Wachstum letzte 30 Tage in % (z.B. +15.3 oder -2.1)
    revenue_mtd DECIMAL(12, 2) DEFAULT 0,-- Einnahmen Month-to-Date (z.B. 1250.50)
    platform_icon TEXT,                  -- Emoji/Icon für die Plattform (z.B. "📸", "📺")
    is_primary BOOLEAN DEFAULT FALSE,    -- Ist das der Hauptkanal?
    notes TEXT,                          -- Notizen zum Kanal
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Erstelle Index für Performance
CREATE INDEX IF NOT EXISTS idx_channels_user_id ON public.channels(user_id);
CREATE INDEX IF NOT EXISTS idx_channels_platform ON public.channels(platform);
CREATE INDEX IF NOT EXISTS idx_channels_value_main ON public.channels(value_main DESC);

-- 3. Row Level Security (RLS) aktivieren
ALTER TABLE public.channels ENABLE ROW LEVEL SECURITY;

-- 4. RLS Policy: User kann nur eigene Channels sehen
CREATE POLICY "Users can view own channels"
    ON public.channels
    FOR SELECT
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'email');

-- 5. RLS Policy: User kann eigene Channels erstellen
CREATE POLICY "Users can insert own channels"
    ON public.channels
    FOR INSERT
    WITH CHECK (user_id = current_setting('request.jwt.claims', true)::json->>'email');

-- 6. RLS Policy: User kann eigene Channels aktualisieren
CREATE POLICY "Users can update own channels"
    ON public.channels
    FOR UPDATE
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'email');

-- 7. RLS Policy: User kann eigene Channels löschen
CREATE POLICY "Users can delete own channels"
    ON public.channels
    FOR DELETE
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'email');

-- 8. Trigger: Auto-Update updated_at
CREATE OR REPLACE FUNCTION update_channels_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_channels_timestamp
    BEFORE UPDATE ON public.channels
    FOR EACH ROW
    EXECUTE FUNCTION update_channels_timestamp();

-- 9. View: Channel Summary pro User
CREATE OR REPLACE VIEW public.channels_summary AS
SELECT 
    user_id,
    COUNT(*) as total_channels,
    SUM(value_main) as total_reach,
    AVG(engagement_rate) as avg_engagement,
    MAX(value_main) as biggest_channel
FROM public.channels
GROUP BY user_id;

-- =============================================================================
-- DEMO DATA (Optional - für Testing)
-- =============================================================================
-- Hinweis: Ersetze 'demo@creatorOs.com' mit einer echten Test-User-Email

INSERT INTO public.channels (user_id, platform, handle, metric_main, value_main, value_label, engagement_rate, avg_views, change_24h, growth_30d, revenue_mtd, platform_icon, is_primary)
VALUES 
    ('demo@creatorOs.com', 'Instagram', '@creator_demo', '125.5k Follower', 125500, 'Follower', 3.8, 8500, 2.4, 12.4, 1250.50, '📸', true),
    ('demo@creatorOs.com', 'TikTok', '@creatordemo', '89.2k Follower', 89200, 'Follower', 5.2, 45000, 5.1, 22.3, 890.00, '🎵', false),
    ('demo@creatorOs.com', 'YouTube', 'Creator Demo', '34.8k Subscribers', 34800, 'Subscribers', 4.1, 12000, 1.8, 8.7, 2340.00, '📺', false),
    ('demo@creatorOs.com', 'OnlyFans', '@creatordemo', '1.2k Subscribers', 1240, 'Subscribers', 15.3, NULL, 3.2, 5.2, 5680.00, '🔥', false),
    ('demo@creatorOs.com', 'LinkedIn', 'Creator Demo', '8.9k Connections', 8900, 'Connections', 2.8, NULL, 0.9, 4.2, 0, '💼', false),
    ('demo@creatorOs.com', 'Newsletter', 'creator@demo.com', '4.2k Subscribers', 4200, 'Subscribers', 18.5, NULL, 1.5, 6.3, 0, '📩', false)
ON CONFLICT DO NOTHING;

-- =============================================================================
-- HINWEISE
-- =============================================================================
-- 1. Führe dieses SQL in Supabase SQL Editor aus
-- 2. RLS ist aktiviert - User können nur eigene Channels sehen
-- 3. Die View 'channels_summary' bietet aggregierte Daten
-- 4. Passe die Demo-Daten an oder lösche sie
-- 5. `value_main` wird für Sortierung verwendet (größter Kanal zuerst)
-- 6. `growth_30d` kann positiv oder negativ sein
-- 7. `platform_icon` enthält Emojis für visuelle Darstellung
-- 8. Für API-Integration: Nutze Instagram Graph API, YouTube Data API, etc.

-- =============================================================================
-- PLATTFORM-VORSCHLÄGE
-- =============================================================================
-- Instagram: value_label = "Follower", icon = "📸"
-- TikTok: value_label = "Follower", icon = "🎵"
-- YouTube: value_label = "Subscribers", icon = "📺"
-- OnlyFans: value_label = "Subscribers", icon = "🔥"
-- Twitter/X: value_label = "Follower", icon = "🐦"
-- Snapchat: value_label = "Follower", icon = "👻"
-- Twitch: value_label = "Follower", icon = "🎮"
-- Facebook: value_label = "Follower", icon = "📘"
-- LinkedIn: value_label = "Connections", icon = "💼"

