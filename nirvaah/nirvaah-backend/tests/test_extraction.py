from dotenv import load_dotenv
load_dotenv()

import json
import sys
from pathlib import Path

# Ensure nirvaah-backend/ is on the path when running directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.extraction import extract_fields

TRANSCRIPTS = [
    {
        "note": 1,
        "text": "സുനിത തോമസിന് വിസിറ്റ് ചെയ്തു. ബിപി 110 70 നോർമലാണ്. ഹീമോഗ്ലോബിൻ പത്ത് പോയിൻറ് രണ്ട്. അയൺ ടാബ്‌ലേറ്റ്സ് മുപ്പത് കൊടുത്തു. അടുത്ത വിസിറ്റ് 14 ന് പിഎച്ച്സിയിൽ വരണം. വെയിറ്റ് സിക്സ്ടി ടു കെജി.",
        "expected": {"bp_systolic": 110, "bp_diastolic": 70, "hemoglobin": 10.2, "iron_tablets_given": 30, "weight_kg": 62.0}
    },
    {
        "note": 2,
        "text": "മായാ കൃഷ്ണന് ഫസ്റ്റ് വിസിറ്റ്. ബി.പി 108, 68, ഹീമോഗ്ലോബിൻ 8.2 വെരി ലോ. അയൺ ടാബ്‌ലെറ്റ്സ് 20 കൊടുത്തു. ബി.പി.എൽ കാർഡുണ്ട്.",
        "expected": {"bp_systolic": 108, "bp_diastolic": 68, "hemoglobin": 8.2, "iron_tablets_given": 20, "bpl_card": True}
    },
    {
        "note": 3,
        "text": "ഗീതാ നായർ വിസിറ്റ് ചെയ്തു. ബിപി 140/92 ഹൈ ആണ്. ഹീമോഗ്ലോബിൻ 10.5. റിഫർഡ് ടു സിഎച്ച്സി ഇമേഡിയറ്റിലി.",
        "expected": {"bp_systolic": 140, "bp_diastolic": 92, "hemoglobin": 10.5, "referred": True, "referral_location": "CHC"}
    },
    {
        "note": 4,
        "text": "ബേബിക്ക് ബിസിജി വാക്സിൻ കൊടുത്തു. വെയിറ്റ് മൂന്ന് പോയിന്റ് രണ്ട് കെജി. ഒപിവിഒ കൊടുത്തു. മദർ ഓക്കെ ആണ്.",
        "expected": {"vaccines_given": ["BCG", "OPV0"], "baby_weight_kg": 3.2}
    },
    {
        "note": 5,
        "text": "വൈറ്റമിൻ എ ഡോസ് കൊടുത്തു. ബേബി നയൻ മണ്ത്സ്. വെയിറ്റ് സെവൻ പോയിൻട് ടു കെ ജി. ഗ്രോത്ത് നോർമൽ ആണ്.",
        "expected": {"vaccines_given": ["VitaminA"], "baby_weight_kg": 7.2}
    },

    {
    "note": 6,
    "text": "ആനി തോമസിന്റെ ANC രണ്ടാമത്തെ വിസിറ്റ്. ബിപി 120/80. ഹീമോഗ്ലോബിൻ 11.5. വെയിറ്റ് അമ്പത്തഞ്ച് കെജി. അയൺ ടാബ്‌ലേറ്റ്സ് അറുപത് കൊടുത്തു.",
    "expected": {"bp_systolic": 120, "bp_diastolic": 80, "hemoglobin": 11.5, "weight_kg": 55.0, "iron_tablets_given": 60}
},
{
    "note": 7,
    "text": "റീന ജോസഫ് വിസിറ്റ്. ബിപി 150/95 ഹൈ ആണ്. പ്രീ എക്ലാംസിയ സംശയം. റിഫർഡ് ടു ഡിസ്ട്രിക്ട് ഹോസ്പിറ്റൽ ഇമീഡിയറ്റ്‌ലി.",
    "expected": {"bp_systolic": 150, "bp_diastolic": 95, "referred": True}
},
{
    "note": 8,
    "text": "ശ്രീദേവി നായർ ANC മൂന്നാമത്തെ വിസിറ്റ്. ബിപി 115/75. ഹീമോഗ്ലോബിൻ 9.5 അനീമിയ ഉണ്ട്. IFA 90 കൊടുത്തു. അടുത്ത വിസിറ്റ് 28ന് പിഎച്ച്സിയിൽ.",
    "expected": {"bp_systolic": 115, "bp_diastolic": 75, "hemoglobin": 9.5, "iron_tablets_given": 90, "next_visit_date": "28", "next_visit_location": "PHC"}
}
]


def check_fields(result, expected):
    correct, wrong = 0, []
    for field, exp_val in expected.items():
        got = result.get(field)
        if isinstance(exp_val, float):
            ok = got is not None and abs(float(got) - exp_val) < 0.15
        elif isinstance(exp_val, bool):
            ok = got == exp_val
        elif isinstance(exp_val, list):
            ok = isinstance(got, list) and set(got) == set(exp_val)
        else:
            ok = got == exp_val
        if ok:
            correct += 1
        else:
            wrong.append(f"{field}: expected={exp_val}, got={got}")
    return correct, len(expected), wrong


def main():
    print("=" * 60)
    print("NIRVAAH AI — Extraction Prompt Test")
    print("=" * 60)

    total_pass = 0

    for t in TRANSCRIPTS:
        result = extract_fields(t["text"])
        conf   = result.get("overall_confidence", 0)
        correct, total, wrong = check_fields(result, t["expected"])
        passed = len(wrong) == 0
        status = "✓ PASS" if passed else "✗ FAIL"
        total_pass += int(passed)

        print(f"\n{status} — Note {t['note']}  confidence={conf:.2f}  fields={correct}/{total}")

        if wrong:
            print("  Wrong fields:")
            for w in wrong:
                print(f"    - {w}")

        print(f"  name={result.get('beneficiary_name')}  "
              f"bp={result.get('bp_systolic')}/{result.get('bp_diastolic')}  "
              f"hb={result.get('hemoglobin')}  "
              f"weight={result.get('weight_kg') or result.get('baby_weight_kg')}  "
              f"vaccines={result.get('vaccines_given')}  "
              f"referred={result.get('referred')}")

        if result.get("error"):
            print(f"  ERROR: {result['error']}")

    print(f"\n{'=' * 60}")
    print(f"RESULT: {total_pass}/8 passed")
    if total_pass >= 6:
        print("✓ Extraction prompt ready for pipeline integration.")
    else:
        print("✗ Needs tuning — paste full output to fix.")
    print("=" * 60)


if __name__ == "__main__":
    main()
