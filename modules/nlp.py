def analyze_report_text(text):
    """
    تحلیل ساده متن فارسی گزارش بحران بر اساس کلمات کلیدی.
    خروجی این تابع یک دیکشنری از نیازها، نشانه‌های بحران و فوریت است.
    """

    if text is None:
        text = ""

    text = text.strip().lower()

    result = {
        "needs_water": False,
        "needs_food": False,
        "needs_medicine": False,
        "needs_medical_team": False,
        "needs_psychological_help": False,
        "has_vulnerable_group": False,
        "route_blocked": False,
        "has_critical_case": False,
        "has_unconscious": False,
        "has_severe_bleeding": False,
        "has_trapped_people": False,
        "urgency_score": 0
    }

    # کلیدواژه‌های آب
    water_keywords = [
        "آب", "بی آب", "بی‌آب", "بدون آب", "آب آشامیدنی",
        "تشنگی", "کمبود آب", "آب نداریم"
    ]

    # کلیدواژه‌های غذا
    food_keywords = [
        "غذا", "نان", "گرسنگی", "مواد غذایی", "کنسرو",
        "کمبود غذا", "غذا نداریم"
    ]

    # کلیدواژه‌های دارو
    medicine_keywords = [
        "دارو", "قرص", "آمپول", "انسولین", "آنتی بیوتیک",
        "آنتی‌بیوتیک", "مسکن", "کمبود دارو", "دارو نداریم"
    ]

    # کلیدواژه‌های نیاز پزشکی
    medical_keywords = [
        "پزشک", "دکتر", "پرستار", "مجروح", "زخمی",
        "اورژانس", "آمبولانس", "درمان", "کمک پزشکی"
    ]

    # کمک روانی
    psych_keywords = [
        "ترس", "اضطراب", "شوک", "روانشناس", "وحشت",
        "حمله عصبی", "گریه شدید"
    ]

    # گروه‌های آسیب‌پذیر
    vulnerable_keywords = [
        "کودک", "نوزاد", "سالمند", "پیر", "بیمار",
        "زن باردار", "باردار", "معلول", "معلولیت"
    ]

    # مسیر بسته
    route_keywords = [
        "راه بسته", "مسیر بسته", "جاده بسته", "مسدود",
        "ریزش", "امکان عبور نیست", "عبور ممکن نیست",
        "پل خراب", "پل تخریب شده"
    ]

    # مورد بدحال / بحرانی
    critical_keywords = [
        "بدحال", "حال وخیم", "وخیم", "خطر جانی",
        "در حال مرگ", "وضعیت بحرانی", "نیاز فوری"
    ]

    # بیهوشی
    unconscious_keywords = [
        "بیهوش", "بی هوش", "از حال رفته", "هوشیار نیست",
        "از هوش رفته"
    ]

    # خونریزی شدید
    bleeding_keywords = [
        "خونریزی", "خون ریزی", "خونریزی شدید",
        "خون زیادی", "زخم عمیق"
    ]

    # گیر افتادگی
    trapped_keywords = [
        "گیر افتاده", "زیر آوار", "محبوس", "محصور",
        "زیر خرابه", "امکان خروج ندارد"
    ]

    # کلمات فوریت
    urgency_keywords = [
        "فوری", "بحرانی", "اورژانسی", "بدحال",
        "خطر جانی", "سریع", "الان", "بلافاصله",
        "کمک فوری", "نیاز فوری"
    ]

    def contains_any(keywords):
        for word in keywords:
            if word in text:
                return True
        return False

    result["needs_water"] = contains_any(water_keywords)
    result["needs_food"] = contains_any(food_keywords)
    result["needs_medicine"] = contains_any(medicine_keywords)
    result["needs_medical_team"] = contains_any(medical_keywords)
    result["needs_psychological_help"] = contains_any(psych_keywords)
    result["has_vulnerable_group"] = contains_any(vulnerable_keywords)
    result["route_blocked"] = contains_any(route_keywords)
    result["has_critical_case"] = contains_any(critical_keywords)
    result["has_unconscious"] = contains_any(unconscious_keywords)
    result["has_severe_bleeding"] = contains_any(bleeding_keywords)
    result["has_trapped_people"] = contains_any(trapped_keywords)

    # محاسبه امتیاز فوریت از متن
    urgency_score = 0

    for word in urgency_keywords:
        if word in text:
            urgency_score += 2

    # برخی نشانه‌ها ذاتاً فوریت را بالا می‌برند
    if result["has_critical_case"]:
        urgency_score += 2

    if result["has_unconscious"]:
        urgency_score += 2

    if result["has_severe_bleeding"]:
        urgency_score += 2

    if result["has_trapped_people"]:
        urgency_score += 2

    if result["route_blocked"]:
        urgency_score += 1

    # سقف امتیاز فوریت
    if urgency_score > 10:
        urgency_score = 10

    result["urgency_score"] = urgency_score

    return result
