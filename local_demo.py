import time
import httpx

API_URL = "http://127.0.0.1:10000/webhook"
PHONE = "whatsapp:+919876543210"

def send_message(body: str, description: str):
    print(f"\n=======================================================")
    print(f"▶ {description}")
    print(f"💬 Sending: '{body}'")
    print(f"=======================================================")
    
    start_time = time.time()
    try:
        response = httpx.post(
            API_URL, 
            data={"From": PHONE, "Body": body, "NumMedia": "0"},
            timeout=15.0
        )
        print(f"✅ Webhook received (HTTP {response.status_code}) in {time.time() - start_time:.2f} seconds.")
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        print("💡 Make sure you are running 'uvicorn app.main:app --host 0.0.0.0 --port 10000' in another terminal!")
    
    print("-" * 55)
    time.sleep(3) # Wait for background processing


print("🚀 STARTING NIRVAAH AI LOCAL DEMO MODE 🚀")
print("This script simulates WhatsApp messages bypassing Twilio.")
print("Watch the FastAPI terminal to see the AI Pipeline in action!\n")

# 1. Standard ANC Visit
send_message(
    "Sunitha Thomas third ANC visit. BP 138/92 hemoglobin 9.5 weight 58kg gave her 30 IFA tablets. Next visit PHC Thrissur.", 
    "TEST 1: Standard ANC Health Visit"
)

# 2. Impossible Anomaly (Pushback)
send_message(
    "Meera Devi first ANC visit. BP is 300/120.", 
    "TEST 2: The Anomaly / Pushback Demo"
)

# 3. SOS Emergency Protocol
send_message(
    "jalebi", 
    "TEST 3: The Secret SOS Emergency Code"
)

# 4. Survey
send_message(
    "SURVEY", 
    "TEST 4A: Triggering Survey Mode"
)
send_message(
    "1", 
    "TEST 4B: Selecting Leprosy Survey"
)

print("\n🎉 DEMO SIMULATION COMPLETE! Check your Vercel Dashboard or Local Dashboard!")
