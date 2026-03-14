from dotenv import load_dotenv
load_dotenv()

import json
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a medical data extraction system for Kerala ASHA workers.
Extract structured health data from voice transcripts in Malayalam, English, or mixed Malayalam-English.

Respond ONLY with valid JSON. No markdown fences. No explanation. No preamble. Just the JSON object.

OUTPUT SCHEMA:
{
  "visit_type": "anc_visit | pnc_visit | immunisation_visit | family_planning_visit",
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
  "referral_location": null,
  "bpl_card": false,
  "clinical_notes": null,
  "overall_confidence": 0.0,
  "field_confidence": {
    "bp_systolic": 0.0,
    "hemoglobin": 0.0,
    "weight_kg": 0.0
  }
}

MALAYALAM TERM MAPPINGS:

-- Vitals --
ബിപി / ബി.പി / BP = bp_systolic + bp_diastolic
  "110 70" OR "110/70" OR "110, 70" -> systolic=110, diastolic=70
  ഹൈ ആണ് = elevated, still extract numbers
  നോർമലാണ് = normal, still extract numbers
ഹീമോഗ്ലോബിൻ / Hb = hemoglobin
  വെരി ലോ = low value, still extract the number
അയൺ ടാബ്ലേറ്റ്സ് / അയൺ ടാബ്ലെറ്റ്സ് / iron tablets / IFA = iron_tablets_given
വെയിറ്റ് / weight = weight_kg (mother) or baby_weight_kg (baby)

-- Locations --
CRITICAL: Always return locations in English only, never Malayalam script.
പിഎച്ച്സി / PHC / പി.എച്ച്.സി = ALWAYS return "PHC"
സിഎച്ച്സി / CHC / സി.എച്ച്.സി = ALWAYS return "CHC"
റിഫർഡ് ടു = referred=true + referral_location in English (PHC or CHC)

-- People --
ബേബി / baby = baby context, use baby_weight_kg
മദർ / mother = mother context, use weight_kg

-- Cards --
ബി.പി.എൽ കാർഡ് / BPL card = bpl_card=true

-- Vaccines --
vaccines_given is always an ARRAY. Add every vaccine mentioned.
ബിസിജി = "BCG"
ഒപിവിഒ = "OPV0"
വൈറ്റമിൻ എ = "VitaminA"
പെന്റാവേലന്റ് = "Pentavalent"
If multiple vaccines given, include all: ["BCG", "OPV0"]

-- Visit Types --
ഫസ്റ്റ് വിസിറ്റ് = anc_visit, anc_visit_number=1
വാക്സിൻ visit = immunisation_visit
പോസ്റ്റ്നേറ്റൽ = pnc_visit

MALAYALAM NUMBERS:
ഒന്ന്=1, രണ്ട്=2, മൂന്ന്=3, നാല്=4, അഞ്ച്=5
ആറ്=6, ഏഴ്=7, എട്ട്=8, ഒമ്പത്=9, പത്ത്=10
ഇരുപത്=20, മുപ്പത്=30, നാല്പത്=40, അമ്പത്=50
അറുപത്=60, എഴുപത്=70

ENGLISH NUMBERS IN MALAYALAM:
സിക്സ്ടി ടു=62, സെവൻ=7, നയൻ=9, ടെൻ=10
പോയിൻറ് / പോയിന്റ് = decimal point
പത്ത് പോയിൻറ് രണ്ട് = 10.2
മൂന്ന് പോയിന്റ് രണ്ട് = 3.2
സെവൻ പോയിൻട് ടു = 7.2

NEXT VISIT:
"14 ന്" = next_visit_date="14"
"പിഎച്ച്സിയിൽ വരണം" = next_visit_location="PHC"
"സിഎച്ച്സിയിൽ" = next_visit_location="CHC"

RULES:
1. Extract ONLY what is clearly stated. Never guess.
2. If field not mentioned set it to null.
3. Baby weight goes to baby_weight_kg. Mother weight goes to weight_kg.
4. If referred set referred=true and extract referral_location in English.
5. Set overall_confidence to 0.95 if all key fields are clear.
6. vaccines_given is always an array, even if only one vaccine.
7. Location fields (next_visit_location, referral_location) must always be English: PHC or CHC.
8. Return pure JSON only, nothing else.
"""


def extract_fields(transcript: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Extract fields from this transcript:\n\n{transcript}"}
            ],
            temperature=0.1,
            max_tokens=1000,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if model adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        return json.loads(raw)

    except json.JSONDecodeError as e:
        return {"overall_confidence": 0.0, "error": f"JSON parse failed: {str(e)}"}
    except Exception as e:
        return {"overall_confidence": 0.0, "error": str(e)}


async def extract_fields_async(transcript: str) -> dict:
    return extract_fields(transcript)