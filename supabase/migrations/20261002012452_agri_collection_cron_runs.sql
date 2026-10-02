BEGIN;
CREATE TABLE IF NOT EXISTS public.agri_collection_runs (
    run_id varchar(36) PRIMARY KEY,
    source_id text NOT NULL CHECK (source_id IN ('mofcom','xinfadi','wuhan','guangzhou','moa_daily','moa_milk')),
    target_date date NOT NULL,
    status text NOT NULL CHECK (status IN ('running','completed','no_data','partial','failed')),
    started_at timestamptz NOT NULL,
    lease_until timestamptz NOT NULL,
    finished_at timestamptz,
    inserted integer NOT NULL DEFAULT 0 CHECK (inserted >= 0),
    updated integer NOT NULL DEFAULT 0 CHECK (updated >= 0),
    observed integer NOT NULL DEFAULT 0 CHECK (observed >= 0),
    errors jsonb NOT NULL DEFAULT '[]'::jsonb
);
CREATE UNIQUE INDEX IF NOT EXISTS agri_collection_one_running_source
    ON public.agri_collection_runs (source_id) WHERE status = 'running';
CREATE INDEX IF NOT EXISTS agri_collection_recent ON public.agri_collection_runs (started_at DESC);
ALTER TABLE public.agri_collection_runs ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.agri_collection_runs FROM PUBLIC, anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON public.agri_collection_runs TO service_role;
COMMENT ON TABLE public.agri_collection_runs IS 'Backend-only Vercel market collection audit and six-minute source lease. Errors contain class names only.';
COMMIT;
