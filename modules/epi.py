def normalize(value, max_value):
    """
    تبدیل مقدار عددی به امتیاز 0 تا 10.
    اگر مقدار از سقف تعیین‌شده بیشتر باشد، امتیاز 10 داده می‌شود.
    """

    if max_value == 0:
        return 0

    score = (value / max_value) * 10

    if score > 10:
        score = 10

    return score


def bool_score(value):
    """
    تبدیل مقدار درست/غلط به امتیاز 0 یا 10.
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
    محاسبه شاخص اولویت اضطراری EPI برای گزارش عمومی/مردمی.

    این نسخه از کاربر تشخیص تخصصی مثل نیاز به جراحی نمی‌خواهد.
    به جای آن از نشانه‌های قابل مشاهده استفاده می‌کند:
    بدحالی، بیهوشی، خونریزی شدید، گیر افتادگی و کمبودها.
    """

    # امتیاز تعداد افراد درگیر
    affected_people_score = normalize(affected_people, 200)

    # امتیاز تعداد تقریبی زخمی‌ها
    injured_score = normalize(estimated_injured, 50)

    # ترکیب داده‌های دستی و NLP
    final_has_critical_case = has_critical_case or nlp_result.get("has_critical_case", False)
    final_has_unconscious = has_unconscious or nlp_result.get("has_unconscious", False)
    final_has_severe_bleeding = has_severe_bleeding or nlp_result.get("has_severe_bleeding", False)
    final_has_trapped_people = has_trapped_people or nlp_result.get("has_trapped_people", False)

    final_route_blocked = route_blocked_manual or nlp_result.get("route_blocked", False)

    # کمبودها: هم عددی از فرم، هم نشانه متنی
    water_score = water_shortage
    food_score = food_shortage
    medicine_score = medicine_shortage

    if nlp_result.get("needs_water", False):
        water_score = max(water_score, 7)

    if nlp_result.get("needs_food", False):
        food_score = max(food_score, 7)

    if nlp_result.get("needs_medicine", False):
        medicine_score = max(medicine_score, 7)

    # امتیازهای Boolean
    critical_score = bool_score(final_has_critical_case)
    unconscious_score = bool_score(final_has_unconscious)
    bleeding_score = bool_score(final_has_severe_bleeding)
    trapped_score = bool_score(final_has_trapped_people)
    route_score = bool_score(final_route_blocked)
    vulnerable_score = bool_score(nlp_result.get("has_vulnerable_group", False))
    medical_need_score = bool_score(nlp_result.get("needs_medical_team", False))

    # فوریت استخراج‌شده از NLP
    urgency_score = nlp_result.get("urgency_score", 0)

    # فرمول EPI در مقیاس داخلی 0 تا 10
    epi_score_0_to_10 = (
        affected_people_score * 0.08 +
        injured_score * 0.12 +
        critical_score * 0.14 +
        unconscious_score * 0.12 +
        bleeding_score * 0.10 +
        trapped_score * 0.10 +
        water_score * 0.08 +
        food_score * 0.05 +
        medicine_score * 0.08 +
        route_score * 0.05 +
        vulnerable_score * 0.04 +
        medical_need_score * 0.04 +
        urgency_score * 0.10
    )

    # تبدیل به مقیاس 0 تا 100
    epi_score = epi_score_0_to_10 * 10

    if epi_score > 100:
        epi_score = 100

    return round(epi_score, 2)


def get_priority_level(epi_score):
    """
    تعیین سطح اولویت بر اساس امتیاز EPI.
    """

    if epi_score >= 75:
        return "بحرانی"
    elif epi_score >= 50:
        return "بالا"
    elif epi_score >= 25:
        return "متوسط"
    else:
        return "پایین"
