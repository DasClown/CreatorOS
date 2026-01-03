-- Supabase Table Schema for CreatorDeck Content Planner
-- Table: content_plan

CREATE TABLE IF NOT EXISTS content_plan (
    id BIGSERIAL PRIMARY KEY,
    datum DATE NOT NULL,
    titel TEXT NOT NULL,
    format TEXT NOT NULL CHECK (format IN ('Reel', 'Post', 'Carousel', 'Story')),
    status TEXT NOT NULL CHECK (status IN ('Idee', 'Draft', 'Ready', 'Published')),
    notizen TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index für schnellere Abfragen nach Datum
CREATE INDEX IF NOT EXISTS idx_content_plan_datum ON content_plan(datum DESC);

-- Index für Status-Filterung
CREATE INDEX IF NOT EXISTS idx_content_plan_status ON content_plan(status);

-- Trigger für automatisches Update von updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_content_plan_updated_at
    BEFORE UPDATE ON content_plan
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) aktivieren
ALTER TABLE content_plan ENABLE ROW LEVEL SECURITY;

-- Policy: Alle können lesen (für Demo-Zwecke)
-- WICHTIG: In Production solltest du user-spezifische Policies erstellen!
CREATE POLICY "Enable read access for all users" ON content_plan
    FOR SELECT USING (true);

-- Policy: Alle können einfügen (für Demo-Zwecke)
CREATE POLICY "Enable insert access for all users" ON content_plan
    FOR INSERT WITH CHECK (true);

-- Policy: Alle können updaten (für Demo-Zwecke)
CREATE POLICY "Enable update access for all users" ON content_plan
    FOR UPDATE USING (true);

-- Policy: Alle können löschen (für Demo-Zwecke)
CREATE POLICY "Enable delete access for all users" ON content_plan
    FOR DELETE USING (true);

-- Demo-Daten einfügen (optional)
INSERT INTO content_plan (datum, titel, format, status, notizen) VALUES
    (CURRENT_DATE, 'Hinter den Kulissen', 'Reel', 'Idee', 'Fokus auf Setup'),
    (CURRENT_DATE, 'Tutorial: Streamlit', 'Post', 'Draft', 'Code-Beispiele zeigen')
ON CONFLICT DO NOTHING;
