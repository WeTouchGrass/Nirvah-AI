"""
data/scheme_eligibility.py — Government scheme eligibility checks for Nirvaah AI.

Contains eligibility rules for all major Kerala maternal health schemes
as pure Python functions. Each function takes the validated_fields dict
and returns either a scheme dict (if eligible) or None (if not eligible).
"""


def check_pmmvy(validated: dict) -> dict | None:
    """
    Pradhan Mantri Matru Vandana Yojana.
    Cash transfer of Rs 5000 for first live birth.
    Eligibility: first pregnancy (anc_visit_number=1),
    ANC registered before 19 weeks gestational age.
    """
    gestational_age = validated.get("gestational_age_weeks")
    anc_number = validated.get("anc_visit_number")

    # First ANC visit AND registered early enough
    if anc_number == 1 and gestational_age and gestational_age <= 19:
        return {
            "name": "PMMVY",
            "benefit": "Rs 5,000 cash transfer in instalments",
            "reason": "First ANC visit registered before 19 weeks",
            "action": "Initiate PMMVY registration at PHC"
        }
    return None


def check_jsy(validated: dict) -> dict | None:
    """
    Janani Suraksha Yojana.
    Institutional delivery incentive.
    Eligibility: BPL card OR age < 19.
    Only relevant for ANC visits (anticipating delivery).
    """
    if validated.get("visit_type") not in ["anc_visit"]:
        return None

    bpl = validated.get("bpl_card", False)
    age = validated.get("beneficiary_age")

    if bpl or (age and age < 19):
        return {
            "name": "JSY",
            "benefit": "Rs 700 (rural) / Rs 600 (urban) delivery cash",
            "reason": "BPL card holder or age below 19",
            "action": "Register for JSY at nearest PHC or CHC"
        }
    return None


def check_sneha_sparsham(validated: dict) -> dict | None:
    """
    Sneha Sparsham (Kerala state scheme).
    Transport and nutrition support for all pregnant women in Kerala.
    Eligibility: any pregnant woman registered at a Kerala PHC or CHC.
    This is a universal scheme — nearly all ANC visit beneficiaries qualify.
    """
    if validated.get("visit_type") == "anc_visit":
        location = validated.get("next_visit_location", "")
        if location in ["PHC", "CHC"]:
            return {
                "name": "Sneha Sparsham",
                "benefit": "Free transport + nutrition support",
                "reason": "Registered pregnant woman at Kerala PHC/CHC",
                "action": "Enroll at next PHC visit — ask health worker"
            }
    return None


def check_jssk(validated: dict) -> dict | None:
    """
    Janani Shishu Suraksha Karyakram.
    Free delivery, drugs, and referral transport.
    Eligibility: any pregnant woman or sick newborn — universal entitlement.
    """
    if validated.get("visit_type") in ["anc_visit", "pnc_visit"]:
        return {
            "name": "JSSK",
            "benefit": "Free delivery, free drugs, free referral transport",
            "reason": "Universal entitlement for all pregnant women and newborns",
            "action": "Remind beneficiary of free services at government facility"
        }
    return None


def check_pmsma(validated: dict) -> dict | None:
    """
    Pradhan Mantri Surakshit Matritva Abhiyan.
    Free ANC on the 9th of every month at PHC.
    Eligibility: all pregnant women at 4+ months gestation.
    """
    gestational_age = validated.get("gestational_age_weeks")
    if gestational_age and gestational_age >= 16:  # 4 months = ~16 weeks
        return {
            "name": "PMSMA",
            "benefit": "Free comprehensive ANC on 9th of every month",
            "reason": f"Gestational age {gestational_age} weeks (4+ months)",
            "action": "Visit nearest PHC on the 9th for free ANC checkup"
        }
    return None


def check_all_schemes(validated_fields: dict) -> list:
    """
    Run all scheme eligibility checks and return a list of schemes
    the beneficiary qualifies for.

    Returns a list of scheme dicts (may be empty if no schemes apply).
    Never raises — all individual checkers are wrapped in try/except.
    """
    checkers = [
        check_pmmvy,
        check_jsy,
        check_sneha_sparsham,
        check_jssk,
        check_pmsma
    ]

    eligible = []
    for checker in checkers:
        try:
            result = checker(validated_fields)
            if result is not None:
                eligible.append(result)
        except Exception as e:
            # A single checker failing should never block the others
            print(f"[SCHEME CHECK ERROR] {checker.__name__}: {e}")

    return eligible
