from dotenv import load_dotenv
load_dotenv()
import httpx, os

print("=" * 60)
print("NIRVAAH AI - COMPONENT TESTS")
print("=" * 60)

# TEST 1: Groq API
print("\n[TEST] Groq API call...")
try:
    r = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + os.environ["GROQ_API_KEY"],
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 50
        },
        timeout=15
    )
    print("  Status:", r.status_code)
    if r.status_code == 200:
        msg = r.json()["choices"][0]["message"]["content"]
        print("  PASS - Groq replied:", msg[:80])
    else:
        print("  FAIL -", r.text[:200])
except Exception as e:
    print("  FAIL -", e)

# TEST 2: Groq Medical Extraction
print("\n[TEST] Groq medical extraction...")
try:
    r = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + os.environ["GROQ_API_KEY"],
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "Extract structured health data. Respond ONLY with valid JSON."},
                {"role": "user", "content": "Sunitha Thomas ANC visit 3 BP 138/92 hemoglobin 9.5 weight 58kg IFA 30 tablets next visit PHC Thrissur"}
            ],
            "temperature": 0.1,
            "max_tokens": 800
        },
        timeout=15
    )
    raw = r.json()["choices"][0]["message"]["content"]
    print("  PASS - Extracted:")
    print(" ", raw[:300])
except Exception as e:
    print("  FAIL -", e)

# TEST 3: Twilio Credentials
print("\n[TEST] Twilio credentials...")
try:
    sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    r = httpx.get(
        "https://api.twilio.com/2010-04-01/Accounts/" + sid + ".json",
        auth=(sid, token)
    )
    print("  Status:", r.status_code)
    if r.status_code == 200:
        print("  PASS - Account:", r.json().get("friendly_name", "N/A"))
    else:
        print("  FAIL -", r.text[:200])
except Exception as e:
    print("  FAIL -", e)

print("\n" + "=" * 60)
print("TESTS COMPLETE")
print("=" * 60)
