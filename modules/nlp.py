
def normalize_text(text):
    """
    نرمال‌سازی اولیه متن فارسی
    """

    if text is None:
        return ""

    text = str(text)

    replacements = {
        "ي": "ی",
        "ك": "ک",
        "‌": " ",
        "\n": " ",
        "\t": " "
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = text.strip().lower()

    while "  " in text:
        text = text.replace("  ", " ")

    return text


def contains_any(text, keywords):
    return any(keyword in text for keyword in keywords)


def calculate_urgency_score(text, result):
    urgency_keywords = [
        "فوری",
        "بحرانی",
        "اورژانسی",
        "بدحال",
        "خطر جانی",
        "سریع",
        "الان",
        "بلافاصله",
        "کمک فوری",
        "نیاز فوری"
    ]

    score = 0

    score += sum(
        2 for keyword in urgency_keywords
        if keyword in text
    )

    if result["has_critical_case"]:
        score += 2

    if result["has_unconscious"]:
        score += 2

    if result["has_severe_bleeding"]:
        score += 2

    if result["has_trapped_people"]:
        score += 2

    if result["route_blocked"]:
        score += 1

    return min(score, 10)


def analyze_report_text(text):
    """
    تحلیل Rule-Based گزارش بحران
    """

    text = normalize_text(text)

    positive_water = [
        "آب کافی",
        "آب به اندازه",
        "آب وجود دارد",
        "آب هست",
        "بی آب نیست",
        "کمبود آب نداریم",
        "نیازی به آب نداریم",
        "آب زیاد"
    ]

    positive_food = [
        "غذا کافی",
        "غذا به اندازه",
        "غذا وجود دارد",
        "غذا هست",
        "کمبود غذا نداریم",
        "نیازی به غذا نداریم",
        "غذا زیاد"
    ]

    positive_medicine = [
        "دارو کافی",
        "دارو وجود دارد",
        "دارو هست",
        "کمبود دارو نداریم",
        "نیازی به دارو نداریم",
        "دارو زیاد"
    ]

    water_keywords = [
        "آب",
        "بی آب",
        "بی آب",
        "بدون آب",
        "تشنگی",
        "کمبود آب",
        "آب نداریم"
    ]

    food_keywords = [
        "غذا",
        "گرسنگی",
        "نان",
        "مواد غذایی",
        "کمبود غذا",
        "غذا نداریم"
    ]

    medicine_keywords = [
        "دارو",
        "قرص",
        "آمپول",
        "انسولین",
        "آنتی بیوتیک",
        "مسکن",
        "کمبود دارو",
        "دارو نداریم"
    ]

    medical_keywords = [
        "پزشک",
        "دکتر",
        "پرستار",
        "مجروح",
        "زخمی",
        "اورژانس",
        "آمبولانس",
        "درمان",
        "کمک پزشکی"
    ]

    psych_keywords = [
        "ترس",
        "اضطراب",
        "شوک",
        "روانشناس",
        "وحشت",
        "حمله عصبی"
    ]

    vulnerable_keywords = [
        "کودک",
        "نوزاد",
        "سالمند",
        "پیر",
        "زن باردار",
        "باردار",
        "معلول"
    ]

    route_keywords = [
        "راه بسته",
        "مسیر بسته",
        "جاده بسته",
        "مسدود",
        "ریزش",
        "امکان عبور نیست",
        "عبور ممکن نیست",
        "پل خراب",
        "پل تخریب شده",
        "راه مسدود"
    ]

    critical_keywords = [
        "بدحال",
        "حال وخیم",
        "وخیم",
        "خطر جانی",
        "در حال مرگ",
        "وضعیت بحرانی"
    ]

    unconscious_keywords = [
        "بیهوش",
        "بی هوش",
        "از حال رفته",
        "هوشیار نیست"
    ]

    bleeding_keywords = [
        "خونریزی",
        "خون ریزی",
        "خونریزی شدید",
        "خون زیادی",
        "زخم عمیق"
    ]

    trapped_keywords = [
        "گیر افتاده",
        "زیر آوار",
        "محبوس",
        "محصور",
        "زیر خرابه"
    ]

    needs_water = (
        contains_any(text, water_keywords)
        and not contains_any(text, positive_water)
    )

    needs_food = (
        contains_any(text, food_keywords)
        and not contains_any(text, positive_food)
    )

    needs_medicine = (
        contains_any(text, medicine_keywords)
        and not contains_any(text, positive_medicine)
    )

    result = {
        "needs_water": needs_water,
        "needs_food": needs_food,
        "needs_medicine": needs_medicine,
        "needs_medical_team": contains_any(text, medical_keywords),
        "needs_psychological_help": contains_any(text, psych_keywords),
        "has_vulnerable_group": contains_any(text, vulnerable_keywords),
        "route_blocked": contains_any(text, route_keywords),
        "has_critical_case": contains_any(text, critical_keywords),
        "has_unconscious": contains_any(text, unconscious_keywords),
        "has_severe_bleeding": contains_any(text, bleeding_keywords),
        "has_trapped_people": contains_any(text, trapped_keywords),
        "urgency_score": 0
    }

    result["urgency_score"] = calculate_urgency_score(
        text,
        result
    )

    return result
