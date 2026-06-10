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
    پیشنهاد منابع و تیم‌های مناسب بر اساس داده‌های فرم، خروجی NLP و امتیاز EPI
    """

    teams = []
    items = []
    transport = []
    actions = []

    # ترکیب داده دستی و NLP
    final_has_critical_case = has_critical_case or nlp_result.get("has_critical_case", False)
    final_has_unconscious = has_unconscious or nlp_result.get("has_unconscious", False)
    final_has_severe_bleeding = has_severe_bleeding or nlp_result.get("has_severe_bleeding", False)
    final_has_trapped_people = has_trapped_people or nlp_result.get("has_trapped_people", False)
    final_route_blocked = route_blocked_manual or nlp_result.get("route_blocked", False)

    final_needs_medical = (
        nlp_result.get("needs_medical_team", False)
        or estimated_injured > 0
        or final_has_critical_case
        or final_has_unconscious
        or final_has_severe_bleeding
    )

    final_needs_water = nlp_result.get("needs_water", False) or water_shortage >= 5
    final_needs_food = nlp_result.get("needs_food", False) or food_shortage >= 5
    final_needs_medicine = nlp_result.get("needs_medicine", False) or medicine_shortage >= 5
    has_vulnerable_group = nlp_result.get("has_vulnerable_group", False)

    # تیم‌ها
    if final_needs_medical:
        teams.append("تیم امداد و درمان اولیه")

    if final_has_critical_case or final_has_unconscious or final_has_severe_bleeding:
        teams.append("تیم فوریت‌های پزشکی / آمبولانس")

    if final_has_trapped_people:
        teams.append("تیم جست‌وجو و نجات")

    if final_needs_water or final_needs_food or final_needs_medicine:
        teams.append("تیم پشتیبانی و توزیع اقلام")

    if has_vulnerable_group:
        teams.append("تیم حمایت از گروه‌های آسیب‌پذیر")

    if nlp_result.get("needs_psychological_help", False):
        teams.append("تیم حمایت روانی")

    # اقلام
    if final_needs_water:
        items.append("آب آشامیدنی")

    if final_needs_food:
        items.append("بسته غذایی اضطراری")

    if final_needs_medicine:
        items.append("دارو و اقلام پزشکی پایه")

    if estimated_injured > 0 or final_needs_medical:
        items.append("کیت کمک‌های اولیه")

    if final_has_severe_bleeding:
        items.append("پانسمان، باند و اقلام کنترل خونریزی")

    if final_has_trapped_people:
        items.append("تجهیزات نجات و آواربرداری سبک")

    if affected_people >= 50:
        items.append("بسته پشتیبانی جمعی برای اسکان/توزیع")

    # وسیله/روش دسترسی
    if final_route_blocked:
        transport.append("خودروی امدادی ویژه مسیر دشوار")
        transport.append("بررسی مسیر جایگزین / اعزام تیم محلی")
    else:
        transport.append("خودروی امدادی استاندارد")

    if final_has_critical_case or final_has_unconscious:
        transport.append("آمبولانس")

    # اقدامات فوری
    if priority_level == "بحرانی":
        actions.append("اعزام فوری در بالاترین اولویت")
        actions.append("اطلاع به مرکز فرماندهی بحران")
    elif priority_level == "بالا":
        actions.append("اعزام سریع تیم‌های منتخب")
        actions.append("پایش مستمر وضعیت منطقه")
    elif priority_level == "متوسط":
        actions.append("ثبت در صف پاسخ عملیاتی کوتاه‌مدت")
    else:
        actions.append("ثبت و پایش گزارش")

    if final_has_trapped_people:
        actions.append("هماهنگی فوری با تیم نجات")

    if final_has_unconscious or final_has_severe_bleeding:
        actions.append("اولویت انتقال مصدومان بدحال")

    if has_vulnerable_group:
        actions.append("توجه ویژه به کودکان، سالمندان و بیماران")

    # حذف موارد تکراری
    teams = list(dict.fromkeys(teams))
    items = list(dict.fromkeys(items))
    transport = list(dict.fromkeys(transport))
    actions = list(dict.fromkeys(actions))

    return {
        "teams": teams,
        "items": items,
        "transport": transport,
        "actions": actions
    }
