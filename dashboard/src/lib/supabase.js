import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://lygxujzvugkmipkzjrwh.supabase.co'

// Use service-role key to bypass RLS (safe for local supervisor dashboard)
const supabaseKey = import.meta.env.VITE_SUPABASE_SERVICE_KEY
  || import.meta.env.VITE_SUPABASE_ANON_KEY
  || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx5Z3h1anp2dWdrbWlwa3pqcndoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMzODk0OTgsImV4cCI6MjA4ODk2NTQ5OH0.am4pC2NtsjWCNm3J_Re6-B2mk9tzugN33JuqiBWD_sM'

export const supabase = createClient(supabaseUrl, supabaseKey)

