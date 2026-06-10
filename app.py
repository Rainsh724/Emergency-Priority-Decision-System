import streamlit as st
from modules.nlp import analyze_report_text
from modules.epi import calculate_epi, get_priority_level
from modules.matcher import recommend_resources
import os
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="EPDS - سامانه اولویت‌بندی اضطراری",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 EPDS")
st.sidebar.title("منو")
page = st.sidebar.radio("انتخاب صفحه", ["ثبت گزارش جدید", "مشاهده همه گزارش‌ها"])
st.subheader("سامانه هوشمند اولویت‌بندی و تخصیص منابع اضطراری")

if page == "ثبت گزارش جدید":

    st.markdown("---")

    st.header("ثبت گزارش عمومی بحران")

    st.info(
        "این فرم برای گزارش اولیه توسط شهروند، داوطلب یا اپراتور طراحی شده است "
        "و از کاربر تشخیص تخصصی پزشکی نمی‌خواهد."
    )

    # اطلاعات پایه
    st.subheader("۱. اطلاعات پایه گزارش")

    col1, col2 = st.columns(2)

    with col1:
        area_name = st.text_input("نام منطقه / محل حادثه")
        reporter_name = st.text_input("نام")
        reporter_lname = st.text_input("نام‌خانوادگی")
        reporter_phone = st.text_input("شماره تماس")

    with col2:
        reporter_type = st.selectbox(
            "نوع گزارش‌دهنده",
            [
                "شهروند عادی",
                "داوطلب",
                "امدادگر",
                "پزشک / پرستار",
                "اپراتور مرکز بحران"
            ]
        )

    affected_people_option = st.selectbox(
        "تعداد تقریبی افراد درگیر",
        [
            "نامشخص",
            "کمتر از ۱۰ نفر",
            "۱۰ تا ۵۰ نفر",
            "۵۰ تا ۲۰۰ نفر",
            "بیشتر از ۲۰۰ نفر"
        ]
    )

    # تبدیل گزینه متنی به عدد تقریبی برای EPI
    if affected_people_option == "کمتر از ۱۰ نفر":
        affected_people = 10
    elif affected_people_option == "۱۰ تا ۵۰ نفر":
        affected_people = 50
    elif affected_people_option == "۵۰ تا ۲۰۰ نفر":
        affected_people = 200
    elif affected_people_option == "بیشتر از ۲۰۰ نفر":
        affected_people = 300
    else:
        affected_people = 0

    st.markdown("---")

    # وضعیت انسانی
    st.subheader("۲. وضعیت انسانی قابل مشاهده")

    col1, col2 = st.columns(2)

    with col1:
        estimated_injured = st.number_input(
            "تعداد تقریبی زخمی‌ها",
            min_value=0,
            value=0,
            step=1
        )

        has_critical_case = st.checkbox("آیا فرد بدحال یا در خطر جدی وجود دارد؟")

    with col2:
        has_unconscious = st.checkbox("آیا فرد بیهوش یا غیرهوشیار وجود دارد؟")
        has_severe_bleeding = st.checkbox("آیا خونریزی شدید مشاهده شده است؟")
        has_trapped_people = st.checkbox("آیا فردی گیر افتاده / زیر آوار مانده است؟")

    st.markdown("---")

    # کمبودها
    st.subheader("۳. کمبودهای ضروری")

    col1, col2, col3 = st.columns(3)

    with col1:
        water_shortage = st.slider("شدت کمبود آب", 0, 10, 0)

    with col2:
        food_shortage = st.slider("شدت کمبود غذا", 0, 10, 0)

    with col3:
        medicine_shortage = st.slider("شدت کمبود دارو", 0, 10, 0)

    st.markdown("---")

    # دسترسی
    st.subheader("۴. وضعیت دسترسی")

    route_blocked_manual = st.checkbox("آیا مسیر دسترسی بسته یا بسیار دشوار است؟")

    st.markdown("---")

    # متن آزاد
    st.subheader("۵. متن آزاد گزارش")

    report_text = st.text_area(
        "توضیح وضعیت را با زبان ساده بنویسید:",
        height=150,
        placeholder="مثلاً: راه بسته شده، چند کودک و سالمند در محل هستند، آب آشامیدنی تمام شده و یک نفر بیهوش شده است..."
    )

    st.markdown("---")

    if st.button("محاسبه اولویت بحران"):
        if area_name.strip() == "":
            st.error("لطفاً نام منطقه یا محل حادثه را وارد کنید.")
        else:
            # تحلیل متن با NLP
            nlp_result = analyze_report_text(report_text)

            # محاسبه EPI
            epi_score = calculate_epi(
                affected_people=affected_people,
                estimated_injured=estimated_injured,
                has_critical_case=has_critical_case,
                has_unconscious=has_unconscious,
                has_severe_bleeding=has_severe_bleeding,
                has_trapped_people=has_trapped_people,
                water_shortage=water_shortage,
                food_shortage=food_shortage,
                medicine_shortage=medicine_shortage,
                route_blocked_manual=route_blocked_manual,
                nlp_result=nlp_result
            )

            priority_level = get_priority_level(epi_score)

            recommendations = recommend_resources(
                epi_score=epi_score,
                priority_level=priority_level,
                affected_people=affected_people,
                estimated_injured=estimated_injured,
                has_critical_case=has_critical_case,
                has_unconscious=has_unconscious,
                has_severe_bleeding=has_severe_bleeding,
                has_trapped_people=has_trapped_people,
                water_shortage=water_shortage,
                food_shortage=food_shortage,
                medicine_shortage=medicine_shortage,
                route_blocked_manual=route_blocked_manual,
                nlp_result=nlp_result
            )

            st.header("نتیجه تحلیل گزارش")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("منطقه", area_name)

            with col2:
                st.metric("امتیاز EPI", epi_score)

            with col3:
                st.metric("سطح اولویت", priority_level)

            if priority_level == "بحرانی":
                st.error("سطح بحران: بحرانی")
            elif priority_level == "بالا":
                st.warning("سطح بحران: بالا")
            elif priority_level == "متوسط":
                st.info("سطح بحران: متوسط")
            else:
                st.success("سطح بحران: پایین")

            st.markdown("---")

            st.subheader("خروجی تحلیل NLP")
            st.json(nlp_result)

            st.markdown("---")

            st.subheader("پیشنهاد تخصیص منابع")

            col1, col2 = st.columns(2)

            with col1:
                st.write("### تیم‌های پیشنهادی")
                for team in recommendations["teams"]:
                    st.write("-", team)

                st.write("### اقلام پیشنهادی")
                for item in recommendations["items"]:
                    st.write("-", item)

            with col2:
                st.write("### روش/وسیله دسترسی پیشنهادی")
                for t in recommendations["transport"]:
                    st.write("-", t)

                st.write("### اقدامات پیشنهادی")
                for action in recommendations["actions"]:
                    st.write("-", action)

            st.markdown("---")

            # ---------- ذخیره در CSV (با اطمینان از وجود پوشه data) ----------
            os.makedirs("data", exist_ok=True)   # <--- این خط رو اضافه کردم
            report_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "region": area_name,
                "reporter_phone": reporter_phone,
                "reporter_name": reporter_name,
                "reporter_lastname": reporter_lname,
                "epi_score": epi_score,
                "priority": priority_level,
                "affected_people": affected_people,
                "estimated_injured": estimated_injured,
                "has_critical": has_critical_case,
                "has_unconscious": has_unconscious,
                "has_bleeding": has_severe_bleeding,
                "has_trapped": has_trapped_people,
                "water_shortage": water_shortage,
                "food_shortage": food_shortage,
                "medicine_shortage": medicine_shortage,
                "route_blocked": route_blocked_manual,
                "free_text": report_text
            }

            df_existing = pd.DataFrame()
            csv_path = "data/reports.csv"
            if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
                df_existing = pd.read_csv(csv_path)

            df_new = pd.DataFrame([report_data])
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_csv(csv_path, index=False, encoding="utf-8-sig")

            st.subheader("خلاصه گزارش ثبت‌شده")

            st.write("**نوع گزارش‌دهنده:**", reporter_type)
            st.write("**تعداد تقریبی افراد درگیر:**", affected_people_option)
            st.write("**تعداد تقریبی زخمی‌ها:**", estimated_injured)

            st.write("**فرد بدحال وجود دارد؟**", "بله" if has_critical_case else "خیر")
            st.write("**فرد بیهوش وجود دارد؟**", "بله" if has_unconscious else "خیر")
            st.write("**خونریزی شدید وجود دارد؟**", "بله" if has_severe_bleeding else "خیر")
            st.write("**گیر افتادگی وجود دارد؟**", "بله" if has_trapped_people else "خیر")
            st.write("**مسیر بسته است؟**", "بله" if route_blocked_manual else "خیر")

            st.write("**کمبود آب:**", water_shortage)
            st.write("**کمبود غذا:**", food_shortage)
            st.write("**کمبود دارو:**", medicine_shortage)

elif page == "مشاهده همه گزارش‌ها":
    st.header("لیست همه گزارش‌ها")
    csv_path = "data/reports.csv"
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
        df = pd.read_csv(csv_path)
        df = df.sort_values("epi_score", ascending=False)
        st.dataframe(df)
        st.write(f"تعداد کل گزارش‌ها: {len(df)}")
        st.bar_chart(df.set_index("region")["epi_score"])
    else:
        st.info("هنوز گزارشی ثبت نشده است. لطفاً ابتدا یک گزارش ثبت کنید.")