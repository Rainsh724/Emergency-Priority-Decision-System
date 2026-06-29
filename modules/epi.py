
# -----------------------------
# EPI Configuration
# -----------------------------

WEIGHTS = {
    "affected_people": 0.08,
    "injured": 0.12,
    "critical": 0.14,
    "unconscious": 0.12,
    "bleeding": 0.10,
    "trapped": 0.10,
    "water": 0.08,
    "food": 0.05,
    "medicine": 0.08,
    "route": 0.05,
    "vulnerable": 0.04,
    "medical_need": 0.04,
    "urgency": 0.10
}


def normalize(value, max_value):
    """
    تبدیل مقدار عددی به بازه 0 تا 10
    """

    if max_value <= 0:
        return 0

    score = (value / max_value) * 10

    return min(score, 10)


def bool_score(value):
    """
    تبدیل True / False به 10 / 0
    """

    return 10 if value else 0


def calculate_epi(
    affected_people,
    estimated_injured,
    has_critical_case,
    has_unconscious,
    has_severe_bleeding,
    has_trapped_people,
    water_shortage,
    food_shortage,
    medicine_shortage,
    route_blocked_manual,
    nlp_result
):
    """
    محاسبه شاخص اولویت اضطراری (EPI)

    خروجی:
        عددی بین 0 تا 100
    """

    # -----------------------------
    # Numeric Scores
    # -----------------------------

    affected_people_score = normalize(
        affected_people,
        200
    )

    injured_score = normalize(
        estimated_injured,
        50
    )

    # -----------------------------
    # Merge Manual + NLP
    # -----------------------------

    final_has_critical_case = (
        has_critical_case
        or nlp_result.get("has_critical_case", False)
    )

    final_has_unconscious = (
        has_unconscious
        or nlp_result.get("has_unconscious", False)
    )

    final_has_severe_bleeding = (
        has_severe_bleeding
        or nlp_result.get("has_severe_bleeding", False)
    )

    final_has_trapped_people = (
        has_trapped_people
        or nlp_result.get("has_trapped_people", False)
    )

    final_route_blocked = (
        route_blocked_manual
        or nlp_result.get("route_blocked", False)
    )

    # -----------------------------
    # Resource Need Scores
    # -----------------------------

    water_score = water_shortage
    food_score = food_shortage
    medicine_score = medicine_shortage

    if nlp_result.get("needs_water", False):
        water_score = max(water_score, 7)

    if nlp_result.get("needs_food", False):
        food_score = max(food_score, 7)

    if nlp_result.get("needs_medicine", False):
        medicine_score = max(medicine_score, 7)

    # -----------------------------
    # Boolean Scores
    # -----------------------------

    critical_score = bool_score(
        final_has_critical_case
    )

    unconscious_score = bool_score(
        final_has_unconscious
    )

    bleeding_score = bool_score(
        final_has_severe_bleeding
    )

    trapped_score = bool_score(
        final_has_trapped_people
    )

    route_score = bool_score(
        final_route_blocked
    )

    vulnerable_score = bool_score(
        nlp_result.get(
            "has_vulnerable_group",
            False
        )
    )

    medical_need_score = bool_score(
        nlp_result.get(
            "needs_medical_team",
            False
        )
    )

    urgency_score = nlp_result.get(
        "urgency_score",
        0
    )

    # -----------------------------
    # Final Score (0-10)
    # -----------------------------

    epi_score_0_to_10 = (
        affected_people_score * WEIGHTS["affected_people"] +
        injured_score * WEIGHTS["injured"] +
        critical_score * WEIGHTS["critical"] +
        unconscious_score * WEIGHTS["unconscious"] +
        bleeding_score * WEIGHTS["bleeding"] +
        trapped_score * WEIGHTS["trapped"] +
        water_score * WEIGHTS["water"] +
        food_score * WEIGHTS["food"] +
        medicine_score * WEIGHTS["medicine"] +
        route_score * WEIGHTS["route"] +
        vulnerable_score * WEIGHTS["vulnerable"] +
        medical_need_score * WEIGHTS["medical_need"] +
        urgency_score * WEIGHTS["urgency"]
    )

    epi_score = round(
        min(epi_score_0_to_10 * 10, 100),
        2
    )

    return epi_score


def get_priority_level(epi_score):
    """
    تعیین سطح بحران
    """

    if epi_score >= 75:
        return "بحرانی"

    if epi_score >= 50:
        return "بالا"

    if epi_score >= 25:
        return "متوسط"

    return "پایین"
