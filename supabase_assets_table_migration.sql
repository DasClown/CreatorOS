-- =============================================================================
-- Migration: Assets Tabelle um change_24h erweitern
-- =============================================================================
-- Falls du die assets Tabelle bereits OHNE das change_24h Feld erstellt hast,
-- führe dieses Script aus, um es nachträglich hinzuzufügen.

-- 1. Füge die Spalte hinzu (falls sie noch nicht existiert)
ALTER TABLE public.assets 
ADD COLUMN IF NOT EXISTS change_24h DECIMAL(10, 2) DEFAULT 0;

-- 2. Kommentar für die neue Spalte
COMMENT ON COLUMN public.assets.change_24h IS 'Performance letzte 24h in Prozent (z.B. +2.4 oder -1.5)';

-- 3. Aktualisiere bestehende Zeilen mit Beispiel-Werten (optional)
-- Hinweis: Du kannst diesen Block auskommentieren lassen oder echte Werte setzen
UPDATE public.assets
SET change_24h = (RANDOM() * 10 - 5)::DECIMAL(10, 2)  -- Zufällige Werte zwischen -5% und +5%
WHERE change_24h IS NULL OR change_24h = 0;

-- 4. Verifizierung
-- Prüfe ob die Spalte existiert und Werte hat
SELECT 
    name, 
    ticker, 
    current_value, 
    change_24h,
    CASE 
        WHEN change_24h > 0 THEN '▲ Gewinn'
        WHEN change_24h < 0 THEN '▼ Verlust'
        ELSE '→ Neutral'
    END as trend
FROM public.assets
ORDER BY current_value DESC
LIMIT 10;

-- =============================================================================
-- HINWEISE
-- =============================================================================
-- 1. Diese Migration ist idempotent (kann mehrfach ausgeführt werden)
-- 2. Bestehende Daten bleiben erhalten
-- 3. Das UPDATE-Statement setzt nur Beispiel-Werte
-- 4. Für echte Werte solltest du eine API-Integration nutzen
-- 5. Führe dieses Script NUR aus, wenn du die Tabelle bereits ohne change_24h hast

