import time
import httpx

# Replace this with your actual Render URL
RENDER_URL = 'https://nirvaah-ai-jucz.onrender.com/health'

print('Keep-alive started. Press Ctrl+C to stop.')
while True:
    try:
        r = httpx.get(RENDER_URL, timeout=10)
        print(f'Ping OK: {r.status_code} — server is awake')
    except Exception as e:
        print(f'Ping failed: {e}')
    time.sleep(600)  # ping every 10 minutes
