-- =============================================================================
-- Supabase Table Definition für Task Management (Planner)
-- =============================================================================
-- 
-- Diese Tabelle in Supabase anlegen:
-- 1. Gehe zu Supabase Dashboard > Table Editor
-- 2. "New Table" klicken oder SQL Editor öffnen
-- 3. Diesen Code ausführen
-- 
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    due_date DATE NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('High', 'Medium', 'Low')),
    status TEXT NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Done')),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Index für schnelle Abfragen nach user_id
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON public.tasks(user_id);

-- Index für Fälligkeitsdatum (wichtig für Sortierung)
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON public.tasks(due_date ASC);

-- Index für Status-Filter
CREATE INDEX IF NOT EXISTS idx_tasks_status ON public.tasks(status);

-- Index für Priorität
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON public.tasks(priority);

-- Composite Index für User + Status + Due Date (Performance-Boost)
CREATE INDEX IF NOT EXISTS idx_tasks_user_status_date ON public.tasks(user_id, status, due_date);

-- Composite Index für User + Category
CREATE INDEX IF NOT EXISTS idx_tasks_user_category ON public.tasks(user_id, category);

-- Row Level Security (RLS) aktivieren
ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;

-- Policy: User kann nur eigene Tasks sehen
CREATE POLICY "Users can view own tasks" ON public.tasks
    FOR SELECT
    USING (auth.uid()::text = user_id OR auth.email() = user_id);

-- Policy: User kann eigene Tasks erstellen
CREATE POLICY "Users can insert own tasks" ON public.tasks
    FOR INSERT
    WITH CHECK (auth.uid()::text = user_id OR auth.email() = user_id);

-- Policy: User kann eigene Tasks aktualisieren
CREATE POLICY "Users can update own tasks" ON public.tasks
    FOR UPDATE
    USING (auth.uid()::text = user_id OR auth.email() = user_id);

-- Policy: User kann eigene Tasks löschen
CREATE POLICY "Users can delete own tasks" ON public.tasks
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

CREATE TRIGGER set_updated_at_tasks
    BEFORE UPDATE ON public.tasks
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- Trigger für completed_at (automatisch setzen wenn Status = Done)
CREATE OR REPLACE FUNCTION public.handle_task_completion()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'Done' AND OLD.status != 'Done' THEN
        NEW.completed_at = NOW();
    ELSIF NEW.status != 'Done' THEN
        NEW.completed_at = NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_completed_at_tasks
    BEFORE UPDATE ON public.tasks
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_task_completion();

-- =============================================================================
-- Views für häufige Abfragen (Optional)
-- =============================================================================

-- View: Offene Tasks sortiert nach Priorität und Fälligkeit
CREATE OR REPLACE VIEW public.tasks_open_prioritized AS
SELECT 
    *,
    CASE 
        WHEN priority = 'High' THEN 1
        WHEN priority = 'Medium' THEN 2
        WHEN priority = 'Low' THEN 3
    END as priority_order,
    CASE 
        WHEN due_date < CURRENT_DATE THEN 'Overdue'
        WHEN due_date = CURRENT_DATE THEN 'Today'
        WHEN due_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'This Week'
        ELSE 'Later'
    END as due_status
FROM public.tasks
WHERE status != 'Done'
ORDER BY priority_order ASC, due_date ASC;

-- View: Statistiken pro User
CREATE OR REPLACE VIEW public.tasks_user_stats AS
SELECT 
    user_id,
    COUNT(*) as total_tasks,
    COUNT(*) FILTER (WHERE status = 'Open') as open_tasks,
    COUNT(*) FILTER (WHERE status = 'Done') as completed_tasks,
    COUNT(*) FILTER (WHERE priority = 'High' AND status != 'Done') as high_priority_open,
    COUNT(*) FILTER (WHERE due_date < CURRENT_DATE AND status != 'Done') as overdue_tasks
FROM public.tasks
GROUP BY user_id;

-- View: Tasks nach Kategorie und Status
CREATE OR REPLACE VIEW public.tasks_by_category AS
SELECT 
    user_id,
    category,
    status,
    COUNT(*) as task_count
FROM public.tasks
GROUP BY user_id, category, status
ORDER BY user_id, category, status;

-- =============================================================================
-- Kommentare für bessere Dokumentation
-- =============================================================================

COMMENT ON TABLE public.tasks IS 'Speichert Aufgaben und To-Dos für Content-Produktion';
COMMENT ON COLUMN public.tasks.user_id IS 'Supabase User ID oder Email des App-Users';
COMMENT ON COLUMN public.tasks.title IS 'Task-Titel/Beschreibung';
COMMENT ON COLUMN public.tasks.due_date IS 'Fälligkeitsdatum';
COMMENT ON COLUMN public.tasks.category IS 'Kategorie: Shooting, Editing, Posting, Admin, etc.';
COMMENT ON COLUMN public.tasks.priority IS 'Priorität: High, Medium, Low';
COMMENT ON COLUMN public.tasks.status IS 'Status: Open, In Progress, Done';
COMMENT ON COLUMN public.tasks.description IS 'Optional: Detaillierte Beschreibung';
COMMENT ON COLUMN public.tasks.completed_at IS 'Automatisch gesetzt wenn Status = Done';

-- =============================================================================
-- Beispiel-Daten (Optional, für Testing)
-- =============================================================================

-- Uncomment um Test-Daten zu erstellen:
/*
INSERT INTO public.tasks (user_id, title, due_date, category, priority, status) VALUES
    ('test@example.com', 'Shooting für Instagram Reel', CURRENT_DATE, 'Shooting', 'High', 'Open'),
    ('test@example.com', 'Video-Editing #342', CURRENT_DATE + INTERVAL '2 days', 'Editing', 'Medium', 'Open'),
    ('test@example.com', 'OnlyFans Post hochladen', CURRENT_DATE, 'Posting', 'High', 'In Progress'),
    ('test@example.com', 'Steuererklärung vorbereiten', CURRENT_DATE + INTERVAL '7 days', 'Admin', 'Low', 'Open');
*/

