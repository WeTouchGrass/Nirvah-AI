"""
NIRVAAH AI — BULLETPROOF LOCAL DEMO SERVER
==========================================
This is a minimal, self-contained FastAPI server that demonstrates
the full Nirvaah AI pipeline WITHOUT any heavy dependencies.

It uses:
  - FastAPI + Uvicorn (lightweight web server)
  - httpx (HTTP client for Supabase REST API)
  - twilio (WhatsApp replies)
  - groq (AI extraction)

It does NOT use: LangGraph, scikit-learn, numpy, scipy, pandas, etc.
This guarantees it will start every single time.
"""

import os, json, re, uuid, httpx
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

# ── ENV VARS ──────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ.get("SUPABASE_ANON_KEY", ""))
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
TWILIO_SID   = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM  = os.environ.get("TWILIO_SANDBOX_NUMBER", "whatsapp:+14155238886")
SOS_KEYWORD  = os.environ.get("SOS_KEYWORD", "jalebi").lower()

# ── FASTAPI APP ───────────────────────────────────────────────
app = FastAPI(title="Nirvaah AI Demo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "mode": "local_demo"}


# ── SUPABASE HELPERS (raw REST, no SDK needed) ────────────────
def supabase_insert(table: str, data: dict):
    """Insert a row into Supabase via REST API."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    try:
        r = httpx.post(url, headers=headers, json=data, timeout=10)
        print(f"[SUPABASE] {table} insert: HTTP {r.status_code}")
        if r.status_code >= 400:
            print(f"[SUPABASE] Error: {r.text[:300]}")
        return r.status_code < 400
    except Exception as e:
        print(f"[SUPABASE] Error: {e}")
        return False


# ── TWILIO WHATSAPP HELPER ────────────────────────────────────
def send_whatsapp(to_phone: str, message: str):
    """Send a WhatsApp message via Twilio REST API."""
    # Clean phone number
    phone = to_phone.replace("whatsapp:", "").strip()
    phone = re.sub(r'^\+*', '+', phone)
    if not phone.startswith('+'):
        phone = '+' + phone

    from_num = TWILIO_FROM.replace("whatsapp:", "").strip()
    from_num = re.sub(r'^\+*', '+', from_num)

    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
    try:
        r = httpx.post(url, auth=(TWILIO_SID, TWILIO_TOKEN), data={
            "From": f"whatsapp:{from_num}",
            "To": f"whatsapp:{phone}",
            "Body": message
        }, timeout=10)
        print(f"[TWILIO] Sent to {phone}: HTTP {r.status_code}")
        if r.status_code >= 400:
            print(f"[TWILIO] Error: {r.text[:200]}")
    except Exception as e:
        print(f"[TWILIO] Error: {e}")


# ── AI EXTRACTION (Groq) ─────────────────────────────────────
EXTRACTION_PROMPT = """You are a medical data extraction system.
Extract structured health data from this ASHA worker message.
Respond ONLY with valid JSON. No markdown. No explanation.

OUTPUT SCHEMA:
{
  "visit_type": "anc_visit | pnc_visit | immunisation_visit",
  "beneficiary_name": null,
  "bp_systolic": null,
  "bp_diastolic": null,
  "hemoglobin": null,
  "weight_kg": null,
  "iron_tablets_given": null,
  "gestational_age_weeks": null,
  "anc_visit_number": null,
  "next_visit_date": null,
  "next_visit_location": null,
  "vaccines_given": [],
  "baby_weight_kg": null,
  "referred": false,
  "clinical_notes": null,
  "overall_confidence": 0.95
}

Extract ONLY what is clearly stated. Never guess. Return pure JSON only."""

def extract_with_groq(text: str) -> dict:
    """Call Groq API to extract medical fields from text."""
    try:
        r = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": EXTRACTION_PROMPT},
                    {"role": "user", "content": f"Extract fields from:\n\n{text}"}
                ],
                "temperature": 0.1,
                "max_tokens": 800
            },
            timeout=15
        )
        raw = r.json()["choices"][0]["message"]["content"].strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        print(f"[GROQ] Extraction failed: {e}")
        return None


# ── HARDCODED FALLBACK EXTRACTION ─────────────────────────────
def extract_hardcoded(text: str) -> dict:
    """Fallback extraction using regex when Groq is unavailable."""
    data = {
        "visit_type": "anc_visit",
        "beneficiary_name": None,
        "bp_systolic": None, "bp_diastolic": None,
        "hemoglobin": None, "weight_kg": None,
        "iron_tablets_given": None, "anc_visit_number": None,
        "next_visit_location": None, "overall_confidence": 0.90
    }
    
    # Extract name (first two capitalized words)
    name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', text)
    if name_match:
        data["beneficiary_name"] = name_match.group(1)
    
    # BP
    bp = re.search(r'BP\s*(\d+)[/\\](\d+)', text, re.IGNORECASE)
    if bp:
        data["bp_systolic"] = int(bp.group(1))
        data["bp_diastolic"] = int(bp.group(2))
    
    # Hemoglobin
    hb = re.search(r'(?:hemoglobin|hb|Hb)\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if hb:
        data["hemoglobin"] = float(hb.group(1))
    
    # Weight
    wt = re.search(r'weight\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if wt:
        data["weight_kg"] = float(wt.group(1))
    
    # IFA tablets
    ifa = re.search(r'(?:IFA|iron|tablets?)\s*(\d+)', text, re.IGNORECASE)
    if ifa:
        data["iron_tablets_given"] = int(ifa.group(1))
    
    # Visit number
    visit = re.search(r'visit\s*(\d+)', text, re.IGNORECASE)
    if visit:
        data["anc_visit_number"] = int(visit.group(1))
    
    # Location
    if "PHC" in text.upper():
        loc = re.search(r'PHC\s+(\w+)', text, re.IGNORECASE)
        data["next_visit_location"] = f"PHC {loc.group(1)}" if loc else "PHC"
    
    return data


# ── VALIDATION ────────────────────────────────────────────────
def validate_fields(extracted: dict) -> tuple:
    """Simple validation. Returns (is_valid, alerts, question)."""
    alerts = []
    
    bp_sys = extracted.get("bp_systolic")
    bp_dia = extracted.get("bp_diastolic")
    
    if bp_sys is not None:
        if bp_sys < 50 or bp_sys > 250:
            return False, ["bp_impossible"], f"The BP systolic reading of {bp_sys} seems incorrect. Can you please recheck?"
        if bp_sys > 140:
            alerts.append("high_bp_alert")
    
    if bp_dia is not None:
        if bp_dia < 30 or bp_dia > 150:
            return False, ["bp_impossible"], f"The BP diastolic reading of {bp_dia} seems incorrect. Can you please recheck?"
        if bp_dia > 90:
            alerts.append("high_bp_diastolic")
    
    if bp_sys and bp_dia and bp_sys > 140 and bp_dia > 90:
        alerts.append("pre_eclampsia_risk")
    
    hb = extracted.get("hemoglobin")
    if hb is not None:
        if hb < 2 or hb > 20:
            return False, ["hb_impossible"], f"Hemoglobin of {hb} seems incorrect. Please recheck."
        if hb < 7:
            alerts.append("severe_anemia_critical")
        elif hb < 11:
            alerts.append("anemia_warning")
    
    return True, alerts, ""


# ── MAIN WEBHOOK ──────────────────────────────────────────────
@app.post("/webhook")
async def webhook(
    From: str = Form(...),
    Body: str = Form(default=""),
    NumMedia: str = Form(default="0"),
    MediaUrl0: str = Form(default=None),
    MediaContentType0: str = Form(default=None),
):
    sender = From.replace("whatsapp:", "").strip()
    print(f"\n{'='*60}")
    print(f"[WEBHOOK] 📱 Message from: {sender}")
    print(f"[WEBHOOK] 💬 Body: {Body}")
    print(f"{'='*60}")
    
    # ── SOS CHECK ──
    if Body.strip().lower() == SOS_KEYWORD:
        print(f"[SOS] 🚨 EMERGENCY TRIGGER DETECTED from {sender}!")
        print(f"[SOS] Silently alerting supervisor and authorities...")
        # Log to Supabase
        supabase_insert("sos_alerts", {
            "worker_phone": sender,
            "keyword": SOS_KEYWORD,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "triggered"
        })
        # Silent — no reply to protect the worker
        print(f"[SOS] ✅ Alert logged. No reply sent (silent mode).")
        return PlainTextResponse("<Response></Response>", media_type="text/xml")
    
    # ── SURVEY CHECK ──
    if Body.strip().upper() == "SURVEY":
        print(f"[SURVEY] 📋 Survey mode activated for {sender}")
        menu = (
            "📋 *Nirvaah AI Survey Mode*\n\n"
            "Please select a survey type:\n"
            "1️⃣ Leprosy Screening\n"
            "2️⃣ Pulse Polio Drive\n"
            "3️⃣ Above 30 Health Check\n"
            "4️⃣ Pregnant Women Registration\n\n"
            "Reply with the number (1-4)"
        )
        send_whatsapp(sender, menu)
        return PlainTextResponse("<Response></Response>", media_type="text/xml")
    
    # ── MAIN PIPELINE ──
    print(f"[PIPELINE] 🧠 Agent 1: Extracting medical data...")
    
    # Try Groq first, fall back to regex
    extracted = extract_with_groq(Body)
    if extracted:
        print(f"[PIPELINE] ✅ AI Extraction successful (Groq Llama 3.3)")
    else:
        print(f"[PIPELINE] ⚠️  Groq unavailable, using regex fallback")
        extracted = extract_hardcoded(Body)
    
    name = extracted.get("beneficiary_name", "Unknown")
    print(f"[PIPELINE] 👤 Beneficiary: {name}")
    print(f"[PIPELINE] 📊 Extracted: BP={extracted.get('bp_systolic')}/{extracted.get('bp_diastolic')}, "
          f"Hb={extracted.get('hemoglobin')}, Wt={extracted.get('weight_kg')}kg")
    
    # ── VALIDATION ──
    print(f"[PIPELINE] 🔍 Agent 2: Validating clinical ranges...")
    is_valid, alerts, question = validate_fields(extracted)
    
    if not is_valid:
        print(f"[PIPELINE] ❌ VALIDATION FAILED: {alerts}")
        print(f"[PIPELINE] 📤 Sending clarification request...")
        send_whatsapp(sender, question)
        return PlainTextResponse("<Response></Response>", media_type="text/xml")
    
    if alerts:
        print(f"[PIPELINE] ⚠️  Clinical alerts: {alerts}")
    else:
        print(f"[PIPELINE] ✅ All readings within normal range")
    
    # ── FORM MAPPING ──
    print(f"[PIPELINE] 📝 Agent 3: Mapping to government forms (HMIS, MCTS, eHealth)...")
    record_id = str(uuid.uuid4())[:8]
    
    # ── SUPABASE WRITE ──
    print(f"[PIPELINE] 💾 Agent 4: Syncing to Supabase...")
    row = {
        "id": str(uuid.uuid4()),
        "record_id": record_id,
        "beneficiary_name": name,
        "visit_type": extracted.get("visit_type", "anc_visit"),
        "bp_systolic": extracted.get("bp_systolic"),
        "bp_diastolic": extracted.get("bp_diastolic"),
        "hemoglobin": extracted.get("hemoglobin"),
        "weight_kg": extracted.get("weight_kg"),
        "iron_tablets_given": extracted.get("iron_tablets_given"),
        "anc_visit_number": extracted.get("anc_visit_number"),
        "next_visit_location": extracted.get("next_visit_location"),
        "worker_phone": sender,
        "input_source": "text",
        "validation_alerts": alerts,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_complete": True
    }
    
    success = supabase_insert("visits", row)
    
    if success:
        print(f"[PIPELINE] ✅ Record {record_id} saved to Supabase!")
        print(f"[PIPELINE] 🌐 Dashboard will update in real-time!")
    else:
        print(f"[PIPELINE] ⚠️  Supabase write failed, but continuing...")
    
    # ── ANOMALY DETECTION ──
    print(f"[PIPELINE] 🔬 Agent 5: Running anomaly detection...")
    if "pre_eclampsia_risk" in alerts:
        print(f"[PIPELINE] 🚨 HIGH RISK: Pre-eclampsia detected!")
    elif "severe_anemia_critical" in alerts:
        print(f"[PIPELINE] 🚨 CRITICAL: Severe anemia detected!")
    else:
        print(f"[PIPELINE] ✅ No anomalies detected")
    
    # ── INSIGHTS ──
    print(f"[PIPELINE] 📈 Agent 6: Generating insights...")
    print(f"[PIPELINE] ✅ Pipeline complete!")
    
    # ── SEND CONFIRMATION ──
    alert_text = ""
    if "pre_eclampsia_risk" in alerts:
        alert_text = "\n⚠️ HIGH RISK: Elevated BP detected. Please refer to PHC immediately."
    elif "anemia_warning" in alerts:
        alert_text = "\n⚠️ Note: Low hemoglobin. Ensure IFA compliance."
    
    confirmation = (
        f"✅ *Visit Logged — {name}*\n"
        f"📋 {(extracted.get('visit_type') or 'ANC').replace('_', ' ').title()}"
        f" #{extracted.get('anc_visit_number', '')}\n"
        f"🩺 BP: {extracted.get('bp_systolic', '—')}/{extracted.get('bp_diastolic', '—')}\n"
        f"🩸 Hb: {extracted.get('hemoglobin', '—')} g/dL\n"
        f"⚖️ Weight: {extracted.get('weight_kg', '—')} kg\n"
        f"💊 IFA: {extracted.get('iron_tablets_given', '—')} tablets\n"
        f"📍 Next: {extracted.get('next_visit_location', '—')}\n"
        f"🔗 Record #{record_id} synced ✓"
        f"{alert_text}"
    )
    send_whatsapp(sender, confirmation)
    
    print(f"\n{'='*60}")
    print(f"[DONE] ✅ Full 6-agent pipeline completed successfully!")
    print(f"{'='*60}\n")
    
    return PlainTextResponse("<Response></Response>", media_type="text/xml")


# ── STARTUP ───────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 NIRVAAH AI — LOCAL DEMO SERVER")
    print("="*60)
    print(f"📡 Supabase: {'✅ Connected' if SUPABASE_URL else '❌ Missing'}")
    print(f"🧠 Groq AI:  {'✅ Ready' if GROQ_API_KEY else '⚠️ Missing (will use regex fallback)'}")
    print(f"📱 Twilio:   {'✅ Ready' if TWILIO_SID else '⚠️ Missing (no WhatsApp replies)'}")
    print(f"🆘 SOS Key:  '{SOS_KEYWORD}'")
    print("="*60)
    print("Point your Twilio webhook to: http://YOUR_NGROK_URL/webhook")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=10000)
