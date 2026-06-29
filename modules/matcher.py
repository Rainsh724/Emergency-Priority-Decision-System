
def recommend_resources(
    epi_score,
    priority_level,
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
    پیشنهاد منابع عملیاتی بر اساس:
    - داده‌های فرم
    - خروجی NLP
    - امتیاز EPI
    """

    teams = set()
    items = set()
    transport = set()
    actions = set()

    # -------------------------
    # Merge Manual + NLP
    # -------------------------

    critical = (
        has_critical_case
        or nlp_result.get("has_critical_case", False)
    )

    unconscious = (
        has_unconscious
        or nlp_result.get("has_unconscious", False)
    )

    bleeding = (
        has_severe_bleeding
        or nlp_result.get("has_severe_bleeding", False)
    )

    trapped = (
        has_trapped_people
        or nlp_result.get("has_trapped_people", False)
    )

    route_blocked = (
        route_blocked_manual
        or nlp_result.get("route_blocked", False)
    )

    needs_medical = (
        estimated_injured > 0
        or critical
        or unconscious
        or bleeding
        or nlp_result.get("needs_medical_team", False)
    )

    needs_water = (
        water_shortage >= 5
        or nlp_result.get("needs_water", False)
    )

    needs_food = (
        food_shortage >= 5
        or nlp_result.get("needs_food", False)
    )

    needs_medicine = (
        medicine_shortage >= 5
        or nlp_result.get("needs_medicine", False)
    )

    vulnerable_group = (
        nlp_result.get("has_vulnerable_group", False)
    )

    psychological_support = (
        nlp_result.get("needs_psychological_help", False)
    )

    # -------------------------
    # Teams
    # -------------------------

    if needs_medical:
        teams.add("تیم امداد و درمان اولیه")

    if critical or unconscious or bleeding:
        teams.add("تیم فوریت‌های پزشکی")
        teams.add("آمبولانس")

    if trapped:
        teams.add("تیم جستجو و نجات")

    if needs_water or needs_food or needs_medicine:
        teams.add("تیم پشتیبانی و توزیع اقلام")

    if vulnerable_group:
        teams.add("تیم حمایت از گروه‌های آسیب‌پذیر")

    if psychological_support:
        teams.add("تیم حمایت روانی")

    # -------------------------
    # Items
    # -------------------------

    if needs_water:
        items.add("آب آشامیدنی")

    if needs_food:
        items.add("بسته غذایی اضطراری")

    if needs_medicine:
        items.add("دارو و تجهیزات پزشکی پایه")

    if needs_medical:
        items.add("کیت کمک‌های اولیه")

    if bleeding:
        items.add("پانسمان و تجهیزات کنترل خونریزی")

    if trapped:
        items.add("تجهیزات جستجو و نجات")

    if affected_people >= 50:
        items.add("بسته پشتیبانی جمعی")

    if affected_people >= 200:
        items.add("چادر اسکان اضطراری")

    # -------------------------
    # Transport
    # -------------------------

    if route_blocked:
        transport.add(
            "خودروی امدادی ویژه مسیر دشوار"
        )
        transport.add(
            "بررسی و استفاده از مسیر جایگزین"
        )
    else:
        transport.add(
            "خودروی امدادی استاندارد"
        )

    if critical or unconscious:
        transport.add("آمبولانس")

    # -------------------------
    # Priority Based Actions
    # -------------------------

    if priority_level == "بحرانی":

        actions.add(
            "اعزام فوری در بالاترین سطح اولویت"
        )

        actions.add(
            "اطلاع به مرکز فرماندهی بحران"
        )

        actions.add(
            "پایش لحظه‌ای وضعیت منطقه"
        )

    elif priority_level == "بالا":

        actions.add(
            "اعزام سریع تیم‌های منتخب"
        )

        actions.add(
            "پایش مستمر وضعیت"
        )

    elif priority_level == "متوسط":

        actions.add(
            "ثبت در صف عملیات کوتاه‌مدت"
        )

    else:

        actions.add(
            "ثبت و پایش گزارش"
        )

    # -------------------------
    # Additional Actions
    # -------------------------

    if trapped:
        actions.add(
            "هماهنگی فوری با تیم نجات"
        )

    if unconscious or bleeding:
        actions.add(
            "اولویت انتقال مصدومان بدحال"
        )

    if vulnerable_group:
        actions.add(
            "رسیدگی ویژه به کودکان و سالمندان"
        )

    # -------------------------
    # High EPI Enhancements
    # -------------------------

    if epi_score >= 85:

        actions.add(
            "اعلام وضعیت فوق‌العاده عملیاتی"
        )

        teams.add(
            "فرمانده عملیات میدانی"
        )

    if epi_score >= 90:

        actions.add(
            "آماده‌سازی ظرفیت پشتیبان منطقه‌ای"
        )

    return {
        "teams": sorted(list(teams)),
        "items": sorted(list(items)),
        "transport": sorted(list(transport)),
        "actions": sorted(list(actions))
    }