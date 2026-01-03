-- =============================================================================
-- Migration: Channels Tabelle um neue Felder erweitern
-- =============================================================================
-- Falls du die channels Tabelle bereits OHNE metric_main, change_24h, revenue_mtd
-- erstellt hast, führe dieses Script aus.

-- 1. Füge die neuen Spalten hinzu (falls sie noch nicht existieren)
ALTER TABLE public.channels 
ADD COLUMN IF NOT EXISTS metric_main TEXT;

ALTER TABLE public.channels 
ADD COLUMN IF NOT EXISTS change_24h DECIMAL(10, 2) DEFAULT 0;

ALTER TABLE public.channels 
ADD COLUMN IF NOT EXISTS revenue_mtd DECIMAL(12, 2) DEFAULT 0;

-- 2. Kommentare für die neuen Spalten
COMMENT ON COLUMN public.channels.metric_main IS 'Formatierte Anzeige der Haupt-Metrik (z.B. "125.5k Follower")';
COMMENT ON COLUMN public.channels.change_24h IS 'Performance letzte 24h in Prozent (z.B. +2.4 oder -1.5)';
COMMENT ON COLUMN public.channels.revenue_mtd IS 'Einnahmen Month-to-Date in EUR (z.B. 1250.50)';

-- 3. Populate metric_main mit bestehenden Daten (optional)
-- Dies erstellt einen formatierten String aus value_main und value_label
UPDATE public.channels
SET metric_main = CASE
    WHEN value_main >= 1000000 THEN ROUND(value_main::DECIMAL / 1000000, 1) || 'M ' || COALESCE(value_label, '')
    WHEN value_main >= 1000 THEN ROUND(value_main::DECIMAL / 1000, 1) || 'k ' || COALESCE(value_label, '')
    ELSE value_main || ' ' || COALESCE(value_label, '')
END
WHERE metric_main IS NULL OR metric_main = '';

-- 4. Setze Beispiel-Werte für change_24h (optional)
-- Nutzt growth_30d wenn vorhanden, sonst zufällige Werte
UPDATE public.channels
SET change_24h = CASE
    WHEN growth_30d IS NOT NULL THEN growth_30d / 10  -- Grobe Annäherung: 30d / 10 ≈ 3d
    ELSE (RANDOM() * 5 - 2.5)::DECIMAL(10, 2)  -- Zufällig zwischen -2.5% und +2.5%
END
WHERE change_24h IS NULL OR change_24h = 0;

-- 5. Setze Beispiel-Werte für revenue_mtd (optional)
-- Basierend auf Plattform und Größe
UPDATE public.channels
SET revenue_mtd = CASE
    WHEN platform IN ('OnlyFans', 'Patreon') THEN (value_main * 4.5)::DECIMAL(12, 2)  -- ~4.5€ pro Subscriber
    WHEN platform IN ('YouTube') THEN (avg_views * 0.02)::DECIMAL(12, 2)  -- ~2 Cent CPM
    WHEN platform IN ('Instagram', 'TikTok') THEN (value_main * 0.01)::DECIMAL(12, 2)  -- ~1 Cent pro Follower
    ELSE 0
END
WHERE revenue_mtd IS NULL OR revenue_mtd = 0;

-- 6. Verifizierung
-- Prüfe ob die neuen Spalten existieren und Werte haben
SELECT 
    platform,
    metric_main,
    value_main,
    change_24h,
    revenue_mtd,
    CASE 
        WHEN revenue_mtd > 0 THEN '💰 Revenue-Tracking aktiv'
        ELSE '⚪ Kein Revenue'
    END as revenue_status
FROM public.channels
ORDER BY revenue_mtd DESC
LIMIT 10;

-- =============================================================================
-- HINWEISE
-- =============================================================================
-- 1. Diese Migration ist idempotent (kann mehrfach ausgeführt werden)
-- 2. Bestehende Daten bleiben erhalten
-- 3. Die UPDATE-Statements setzen nur Beispiel-Werte
-- 4. Für echte Revenue-Daten solltest du die Werte manuell oder via API setzen
-- 5. Führe dieses Script NUR aus, wenn du die Tabelle bereits ohne diese Felder hast

