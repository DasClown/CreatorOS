-- =============================================================================
-- CreatorOS: Deals Table (Brand Deals & Collaborations Management)
-- =============================================================================
-- Diese Tabelle speichert Kooperationen, Sponsorings und Brand Deals
-- Verwendung: Deal-Tracking, Revenue-Management, Deadline-Monitoring

-- 1. Erstelle die Tabelle
CREATE TABLE IF NOT EXISTS public.deals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    brand_name TEXT NOT NULL,            -- Marke/Unternehmen (z.B. "Nike", "Red Bull")
    deal_type TEXT NOT NULL,             -- Typ: "Sponsored Post", "Brand Ambassador", "Affiliate", etc.
    platform TEXT,                       -- Plattform: "Instagram", "YouTube", "Multi-Channel"
    status TEXT DEFAULT 'Negotiation',   -- Status: "Negotiation", "Confirmed", "In Progress", "Completed", "Cancelled"
    amount DECIMAL(12, 2),               -- Deal-Wert in € (z.B. 2500.00)
    currency TEXT DEFAULT 'EUR',         -- Währung (EUR, USD, etc.)
    due_date DATE,                       -- Fälligkeitsdatum / Deadline
    deliverables TEXT,                   -- Was ist zu liefern? (z.B. "3 Instagram Posts, 1 Story")
    notes TEXT,                          -- Notizen zum Deal
    contact_person TEXT,                 -- Ansprechpartner
    contact_email TEXT,                  -- Email des Ansprechpartners
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 2. Erstelle Indizes für Performance
CREATE INDEX IF NOT EXISTS idx_deals_user_id ON public.deals(user_id);
CREATE INDEX IF NOT EXISTS idx_deals_status ON public.deals(status);
CREATE INDEX IF NOT EXISTS idx_deals_due_date ON public.deals(due_date);
CREATE INDEX IF NOT EXISTS idx_deals_platform ON public.deals(platform);

-- 3. Row Level Security (RLS) aktivieren
ALTER TABLE public.deals ENABLE ROW LEVEL SECURITY;

-- 4. RLS Policy: User kann nur eigene Deals sehen
CREATE POLICY "Users can view own deals"
    ON public.deals
    FOR SELECT
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'email');

-- 5. RLS Policy: User kann eigene Deals erstellen
CREATE POLICY "Users can insert own deals"
    ON public.deals
    FOR INSERT
    WITH CHECK (user_id = current_setting('request.jwt.claims', true)::json->>'email');

-- 6. RLS Policy: User kann eigene Deals aktualisieren
CREATE POLICY "Users can update own deals"
    ON public.deals
    FOR UPDATE
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'email');

-- 7. RLS Policy: User kann eigene Deals löschen
CREATE POLICY "Users can delete own deals"
    ON public.deals
    FOR DELETE
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'email');

-- 8. Trigger: Auto-Update updated_at
CREATE OR REPLACE FUNCTION update_deals_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_deals_timestamp
    BEFORE UPDATE ON public.deals
    FOR EACH ROW
    EXECUTE FUNCTION update_deals_timestamp();

-- 9. Trigger: Auto-Set completed_at bei Status "Completed"
CREATE OR REPLACE FUNCTION set_deals_completed_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'Completed' AND OLD.status != 'Completed' THEN
        NEW.completed_at = NOW();
    ELSIF NEW.status != 'Completed' THEN
        NEW.completed_at = NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_deals_completed
    BEFORE UPDATE ON public.deals
    FOR EACH ROW
    EXECUTE FUNCTION set_deals_completed_timestamp();

-- 10. View: Deals Summary pro User
CREATE OR REPLACE VIEW public.deals_summary AS
SELECT 
    user_id,
    COUNT(*) as total_deals,
    COUNT(*) FILTER (WHERE status = 'Confirmed') as confirmed_deals,
    COUNT(*) FILTER (WHERE status = 'Completed') as completed_deals,
    SUM(amount) FILTER (WHERE status = 'Completed') as total_revenue,
    SUM(amount) FILTER (WHERE status IN ('Confirmed', 'In Progress')) as pending_revenue
FROM public.deals
GROUP BY user_id;

-- 11. View: Überfällige Deals
CREATE OR REPLACE VIEW public.overdue_deals AS
SELECT 
    id,
    user_id,
    brand_name,
    deal_type,
    amount,
    due_date,
    status,
    CURRENT_DATE - due_date as days_overdue
FROM public.deals
WHERE due_date < CURRENT_DATE 
AND status NOT IN ('Completed', 'Cancelled')
ORDER BY due_date ASC;

-- =============================================================================
-- DEMO DATA (Optional - für Testing)
-- =============================================================================
-- Hinweis: Ersetze 'demo@creatorOs.com' mit einer echten Test-User-Email

INSERT INTO public.deals (user_id, brand_name, deal_type, platform, status, amount, due_date, deliverables, contact_person)
VALUES 
    ('demo@creatorOs.com', 'Nike', 'Sponsored Post', 'Instagram', 'Confirmed', 2500.00, CURRENT_DATE + INTERVAL '7 days', '3 Instagram Posts, 2 Stories', 'Sarah Marketing'),
    ('demo@creatorOs.com', 'Red Bull', 'Brand Ambassador', 'Multi-Channel', 'In Progress', 15000.00, CURRENT_DATE + INTERVAL '30 days', 'Monatliche Content-Serie', 'Max Sponsoring'),
    ('demo@creatorOs.com', 'Gymshark', 'Affiliate Deal', 'YouTube', 'Negotiation', 1200.00, CURRENT_DATE + INTERVAL '14 days', '2 YouTube Videos mit Link', 'Lisa Partnerships'),
    ('demo@creatorOs.com', 'HelloFresh', 'Sponsored Video', 'YouTube', 'Completed', 3000.00, CURRENT_DATE - INTERVAL '5 days', '1 Dedicated Video', 'Tom Creator Relations'),
    ('demo@creatorOs.com', 'Asus', 'Product Review', 'Multi-Channel', 'Confirmed', 1800.00, CURRENT_DATE + INTERVAL '21 days', 'Unboxing + Review', 'Anna PR')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- HINWEISE
-- =============================================================================
-- 1. Führe dieses SQL in Supabase SQL Editor aus
-- 2. RLS ist aktiviert - User können nur eigene Deals sehen
-- 3. Die View 'deals_summary' bietet aggregierte Daten
-- 4. Die View 'overdue_deals' zeigt überfällige Deals
-- 5. `due_date` wird für Sortierung verwendet (nächste Deadline zuerst)
-- 6. `completed_at` wird automatisch gesetzt bei Status = "Completed"
-- 7. Status-Optionen: Negotiation, Confirmed, In Progress, Completed, Cancelled

-- =============================================================================
-- STATUS-WORKFLOW
-- =============================================================================
-- Negotiation  → Erste Gespräche, noch nicht bestätigt
-- Confirmed    → Deal ist bestätigt, noch nicht begonnen
-- In Progress  → Content wird erstellt
-- Completed    → Deal abgeschlossen, Zahlung erhalten
-- Cancelled    → Deal wurde abgesagt

-- =============================================================================
-- DEAL-TYP VORSCHLÄGE
-- =============================================================================
-- "Sponsored Post"       → Einzelner bezahlter Post
-- "Sponsored Video"      → Bezahltes Video
-- "Brand Ambassador"     → Langfristige Partnerschaft
-- "Affiliate Deal"       → Provision-basiert
-- "Product Review"       → Produkt-Review ohne direkte Zahlung
-- "Event Appearance"     → Live-Event Auftritt
-- "Content Series"       → Mehrteilige Content-Serie
-- "Giveaway"             → Gewinnspiel-Kooperation

