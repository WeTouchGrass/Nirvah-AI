from fastapi import FastAPI
from app.webhook import router as webhook_router
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os, threading, time, httpx

load_dotenv()

# ── Keep-alive: pings /health every 10 min to prevent Render free-tier sleep ──
def _keep_alive_loop():
    url = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
    if not url:
        print("[KEEP-ALIVE] No RENDER_EXTERNAL_URL set, skipping.")
        return
    print(f"[KEEP-ALIVE] Pinging {url}/health every 10 minutes.")
    while True:
        time.sleep(600)
        try:
            r = httpx.get(f"{url}/health", timeout=10)
            print(f"[KEEP-ALIVE] Ping OK: {r.status_code}")
        except Exception as e:
            print(f"[KEEP-ALIVE] Ping failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    t = threading.Thread(target=_keep_alive_loop, daemon=True)
    t.start()
    yield

app = FastAPI(title='Nirvaah AI Backend', lifespan=lifespan)
app.include_router(webhook_router)

@app.get('/health')
async def health_check():
    return {'status': 'ok', 'service': 'nirvaah-ai'}


@app.get('/audit/verify')
async def audit_verify():
    """
    Verifies the full SHA-256 audit chain integrity.
    Called by the supervisor dashboard's AuditChain component.
    Returns {valid: true} or a list of tamper alerts.
    """
    from app.verify_integrity import verify_full_chain
    from app.database import supabase, log_access
    log_access('supervisor', 'SUPERVISOR', 'READ', 'audit_log')
    try:
        entries = supabase.table('audit_log') \
            .select('*') \
            .order('id') \
            .execute().data
        result = verify_full_chain(entries)
        return {'valid': result, 'total_entries': len(entries)}
    except Exception as e:
        return {'valid': False, 'error': str(e)}

