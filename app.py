import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from modules.nlp import analyze_report_text
from modules.epi import calculate_epi, get_priority_level
from modules.matcher import recommend_resources
from modules.database import init_db, save_report, get_all_reports

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="EPDS - سامانه اولویت‌بندی اضطراری",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

.hero{

position:relative;

overflow:hidden;

padding:28px 35px;

margin-bottom:30px;

border-radius:22px;

direction:rtl;

text-align:right;

background:linear-gradient(135deg,#161b22,#1b2433,#202b3f);

border:1px solid rgba(80,130,255,.25);

box-shadow:
0 0 30px rgba(0,80,255,.08),
0 15px 35px rgba(0,0,0,.35);

animation:fadeUp .8s ease;

}

.hero::before{

content:"";

position:absolute;

top:-120px;

left:-120px;

width:260px;

height:260px;

background:#3b82f630;

filter:blur(70px);

animation:float1 7s ease-in-out infinite;

}

.hero::after{

content:"";

position:absolute;

bottom:-100px;

right:-100px;

width:220px;

height:220px;

background:#06b6d430;

filter:blur(70px);

animation:float2 8s ease-in-out infinite;

}

.title{

font-size:38px;

font-weight:800;

color:white;

position:relative;

z-index:2;

}

.subtitle{

margin-top:10px;

font-size:17px;

color:#b8c7dc;

line-height:1.9;

position:relative;

z-index:2;

}

.badges{

display:flex;

gap:12px;

flex-wrap:wrap;

margin-top:25px;

position:relative;

z-index:2;

}

.badge{

padding:9px 16px;

border-radius:30px;

background:rgba(255,255,255,.05);

border:1px solid rgba(255,255,255,.08);

color:#eaf2ff;

font-size:14px;

transition:.25s;

backdrop-filter:blur(10px);

}

.badge:hover{

transform:translateY(-4px);

box-shadow:0 0 15px rgba(59,130,246,.45);

border-color:#3b82f6;

}

.logo{

position:absolute;

left:35px;

top:50%;

transform:translateY(-50%);

font-size:74px;

animation:pulse 3s infinite;

z-index:2;

}

.line{

margin-top:18px;

height:3px;

border-radius:20px;

background:linear-gradient(90deg,#3b82f6,#06b6d4,#7c3aed);

background-size:200%;

animation:move 6s linear infinite;

position:relative;

z-index:2;

}

@keyframes fadeUp{

from{

opacity:0;

transform:translateY(-25px);

}

to{

opacity:1;

transform:translateY(0);

}

}

@keyframes pulse{

0%,100%{

transform:translateY(-50%) scale(1);

filter:drop-shadow(0 0 8px #3b82f6);

}

50%{

transform:translateY(-50%) scale(1.08);

filter:drop-shadow(0 0 18px #06b6d4);

}

}

@keyframes move{

0%{background-position:0%;}

100%{background-position:200%;}

}

@keyframes float1{

50%{transform:translate(35px,25px);}

}

@keyframes float2{

50%{transform:translate(-30px,-20px);}

}

</style>
""", unsafe_allow_html=True)

st.markdown("""

<div class="hero">

<div class="title">

🚨 EPDS

</div>

<div class="subtitle">

Emergency Priority & Dispatch Support System

<br>

سامانه هوشمند اولویت‌بندی، تحلیل و تخصیص منابع در شرایط بحران

</div>

<div class="line"></div>

<div class="badges">

<div class="badge">🤖 AI Analysis</div>

<div class="badge">📊 EPI Engine</div>

<div class="badge">🚑 Smart Dispatch</div>

<div class="badge">📂 SQLite</div>

</div>

<div class="logo">

🚨

</div>

</div>

""", unsafe_allow_html=True)

# -----------------------------
# CSS Styling - Command Center Dark Theme
# -----------------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── ROOT & RESET ── */
*, *::before, *::after { box-sizing: border-box; }

 html, body, [class*="css"] {
     font-family: 'Vazirmatn', sans-serif;
     direction: rtl;
 }

/* ── GLOBAL BACKGROUND ── */
.stApp {
    background-color: #0d1117;
    color: #c9d1d9;
}

.main .block-container {
    padding: 2rem 2.5rem;
    max-width: 1400px;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
    border-right: 1px solid #21262d;
}

[data-testid="stSidebar"] .stRadio label {
    color: #8b949e !important;
    font-size: 0.9rem;
    padding: 0.5rem 0;
    transition: color 0.2s;
}

[data-testid="stSidebar"] .stRadio label:hover {
    color: #f0a500 !important;
}

/* ── SIDEBAR BRAND ── */
.sidebar-brand {
    text-align: center;
    padding: 1.5rem 1rem 2rem;
    border-bottom: 1px solid #21262d;
    margin-bottom: 1.5rem;
}

.sidebar-brand .brand-icon {
    font-size: 2.5rem;
    display: block;
    margin-bottom: 0.5rem;
    animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
    0%, 100% { filter: drop-shadow(0 0 6px rgba(240,165,0,0.4)); }
    50% { filter: drop-shadow(0 0 14px rgba(240,165,0,0.8)); }
}

.sidebar-brand h2 {
    color: #f0a500;
    font-size: 1.3rem;
    font-weight: 800;
    letter-spacing: 3px;
    margin: 0;
}

.sidebar-brand p {
    color: #484f58;
    font-size: 0.72rem;
    letter-spacing: 1.5px;
    margin: 0.3rem 0 0;
    text-transform: uppercase;
}

/* ── HEADINGS ── */
h1, h2, h3, h4 {
    color: #e6edf3;
    font-weight: 700;
}

/* ── PAGE HEADER COMPONENT ── */
.page-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem 2rem;
    background: linear-gradient(135deg, #161b22 0%, #1c2230 100%);
    border: 1px solid #21262d;
    border-radius: 12px;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}

.page-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: linear-gradient(180deg, #f0a500, #e05c00);
}

.page-header .ph-icon {
    font-size: 2.2rem;
    flex-shrink: 0;
}

.page-header h1 {
    font-size: 1.6rem;
    font-weight: 800;
    margin: 0;
    color: #e6edf3;
}

.page-header p {
    color: #6e7681;
    font-size: 0.85rem;
    margin: 0.2rem 0 0;
}

/* ── SECTION HEADER ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 2rem 0 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid #21262d;
}

.section-header h3 {
    font-size: 1rem;
    font-weight: 600;
    color: #8b949e;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

.section-header .sh-dot {
    width: 8px; height: 8px;
    background: #f0a500;
    border-radius: 50%;
    flex-shrink: 0;
}

/* ── CARDS ── */
.glass-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}

.glass-card:hover {
    border-color: #30363d;
}

/* ── KPI METRIC BOXES ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}

.kpi-box {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
}

.kpi-box:hover {
    transform: translateY(-2px);
    border-color: #30363d;
}

.kpi-box::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
}

.kpi-box.amber::after  { background: #f0a500; }
.kpi-box.red::after    { background: #f85149; }
.kpi-box.blue::after   { background: #388bfd; }
.kpi-box.green::after  { background: #3fb950; }

.kpi-box .kpi-label {
    font-size: 0.72rem;
    color: #6e7681;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.4rem;
}

.kpi-box .kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #e6edf3;
    line-height: 1;
}

.kpi-box .kpi-icon {
    position: absolute;
    top: 1rem; left: 1rem;
    font-size: 1.5rem;
    opacity: 0.15;
}

/* ── STATUS BADGE ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}

.status-badge.critical { background: rgba(248,81,73,0.15); color: #f85149; border: 1px solid rgba(248,81,73,0.3); }
.status-badge.high     { background: rgba(240,165,0,0.15); color: #f0a500; border: 1px solid rgba(240,165,0,0.3); }
.status-badge.medium   { background: rgba(56,139,253,0.15); color: #388bfd; border: 1px solid rgba(56,139,253,0.3); }
.status-badge.low      { background: rgba(63,185,80,0.15); color: #3fb950; border: 1px solid rgba(63,185,80,0.3); }

/* ── PRIORITY BREAKDOWN BOXES ── */
.priority-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
    margin: 1rem 0;
}

.prio-box {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}

.prio-box .prio-icon { font-size: 1.4rem; display: block; }
.prio-box .prio-count {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    display: block;
    margin: 0.2rem 0;
}
.prio-box .prio-label { font-size: 0.75rem; color: #6e7681; }

.prio-box.c-red   { border-top: 3px solid #f85149; } .prio-box.c-red .prio-count   { color: #f85149; }
.prio-box.c-amber { border-top: 3px solid #f0a500; } .prio-box.c-amber .prio-count { color: #f0a500; }
.prio-box.c-blue  { border-top: 3px solid #388bfd; } .prio-box.c-blue .prio-count  { color: #388bfd; }
.prio-box.c-green { border-top: 3px solid #3fb950; } .prio-box.c-green .prio-count { color: #3fb950; }

/* ── FORM INPUTS ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
[data-baseweb="select"] {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
    font-family: 'Vazirmatn', sans-serif !important;
    transition: border-color 0.2s !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #f0a500 !important;
    box-shadow: 0 0 0 3px rgba(240,165,0,0.1) !important;
}

/* ── SLIDER ── */
.stSlider > div > div > div[data-testid="stSlider"] div[role="slider"] {
    background-color: #f0a500 !important;
}

/* ── CHECKBOX ── */
.stCheckbox label span {
    color: #c9d1d9 !important;
    font-size: 0.9rem;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #f0a500 0%, #e05c00 100%) !important;
    color: #0d1117 !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.65rem 1.5rem !important;
    letter-spacing: 0.5px;
    transition: opacity 0.2s, transform 0.2s !important;
    box-shadow: 0 4px 15px rgba(240,165,0,0.2) !important;
}

.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(240,165,0,0.35) !important;
}

/* ── ALERT BOXES ── */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: 10px !important;
    border: none !important;
}

.stSuccess > div { background: rgba(63,185,80,0.1) !important; border: 1px solid rgba(63,185,80,0.3) !important; color: #3fb950 !important; }
.stError   > div { background: rgba(248,81,73,0.1) !important; border: 1px solid rgba(248,81,73,0.3) !important; color: #f85149 !important; }
.stWarning > div { background: rgba(240,165,0,0.1) !important; border: 1px solid rgba(240,165,0,0.3) !important; color: #f0a500 !important; }
.stInfo    > div { background: rgba(56,139,253,0.1) !important; border: 1px solid rgba(56,139,253,0.3) !important; color: #388bfd !important; }

/* ── METRICS ── */
[data-testid="metric-container"] {
    background: #161b22 !important;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 1rem 1.2rem !important;
}

[data-testid="metric-container"] label {
    color: #6e7681 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.8rem !important;
    color: #e6edf3 !important;
}

/* ── DATAFRAME ── */
.stDataFrame {
    border: 1px solid #21262d !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

[data-testid="stDataFrame"] table {
    background: #161b22 !important;
}

[data-testid="stDataFrame"] th {
    background: #0d1117 !important;
    color: #8b949e !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-bottom: 1px solid #21262d !important;
}

[data-testid="stDataFrame"] td {
    color: #c9d1d9 !important;
    font-size: 0.85rem !important;
    border-bottom: 1px solid #161b22 !important;
}

/* ── REPORT ALERT CARDS ── */
.report-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.2rem;
    border-radius: 10px;
    margin-bottom: 0.6rem;
    border: 1px solid transparent;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: default;
    transition: transform 0.15s;
}

.report-card:hover { transform: translateX(-3px); }

.report-card.card-red    { background: rgba(248,81,73,0.08);  border-color: rgba(248,81,73,0.25);  color: #f85149; }
.report-card.card-amber  { background: rgba(240,165,0,0.08);  border-color: rgba(240,165,0,0.25);  color: #f0a500; }
.report-card.card-blue   { background: rgba(56,139,253,0.08); border-color: rgba(56,139,253,0.25); color: #388bfd; }
.report-card.card-green  { background: rgba(63,185,80,0.08);  border-color: rgba(63,185,80,0.25);  color: #3fb950; }

.report-card .rc-region { font-weight: 700; font-size: 1rem; }
.report-card .rc-meta   { color: #6e7681; font-size: 0.78rem; margin-top: 0.1rem; }
.report-card .rc-epi    { margin-right: auto; font-family: 'JetBrains Mono', monospace; font-size: 1.2rem; font-weight: 700; }

/* ── RECOMMENDATION LISTS ── */
.rec-section {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 1.2rem;
    margin-bottom: 0.75rem;
}

.rec-section h4 {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #6e7681;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #21262d;
}

.rec-item {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.4rem 0;
    color: #c9d1d9;
    font-size: 0.88rem;
    border-bottom: 1px solid #0d1117;
}

.rec-item:last-child { border-bottom: none; }

.rec-item::before {
    content: '›';
    color: #f0a500;
    font-weight: 700;
    flex-shrink: 0;
}

/* ── EPI SCORE RESULT ── */
.epi-result-banner {
    background: linear-gradient(135deg, #161b22 0%, #1c2230 100%);
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    margin: 1.5rem 0;
    position: relative;
    overflow: hidden;
}

.epi-result-banner::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at center top, rgba(240,165,0,0.06) 0%, transparent 70%);
}

.epi-result-banner .epi-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 4rem;
    font-weight: 700;
    color: #f0a500;
    line-height: 1;
    text-shadow: 0 0 40px rgba(240,165,0,0.3);
}

.epi-result-banner .epi-label {
    font-size: 0.8rem;
    color: #6e7681;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 0.4rem;
}

/* ── DIVIDERS ── */
hr { border: none; border-top: 1px solid #21262d; margin: 1.5rem 0; }

/* ── PLOTLY/CHART BACKGROUNDS ── */
.js-plotly-plot { background: transparent !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #484f58; }

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
    .kpi-grid, .priority-row { grid-template-columns: repeat(2, 1fr); }
    .epi-result-banner .epi-number { font-size: 2.5rem; }
}


div[data-baseweb="slider"]{
    direction:ltr !important;
}

div[data-baseweb="slider"] *{
    direction:ltr !important;
    text-align:left !important;
}

/* عدد کنار اسلایدر */
div[data-baseweb="slider"] + div{
    direction:ltr !important;
}            

</style>
""", unsafe_allow_html=True)


# -----------------------------
# Helpers
# -----------------------------
def convert_people(option):
    mapping = {
        "نامشخص": 0,
        "کمتر از ۱۰ نفر": 10,
        "۱۰ تا ۵۰ نفر": 50,
        "۵۰ تا ۲۰۰ نفر": 200,
        "بیشتر از ۲۰۰ نفر": 300
    }
    return mapping.get(option, 0)


def section_header(icon, title):
    st.markdown(f"""
    <div class="section-header">
        <div class="sh-dot"></div>
        <h3>{icon} &nbsp; {title}</h3>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------
# UI - Form Page
# -----------------------------
def render_form():

    # ── Section 1: Basic Info ──
    section_header("📋", "اطلاعات اولیه")

    col1, col2 = st.columns(2)
    with col1:
        area = st.text_input("نام منطقه", placeholder="مثلاً: تهران - منطقه ۷")
        name = st.text_input("نام", placeholder="نام گزارش‌دهنده")
        lastname = st.text_input("نام خانوادگی")
    with col2:
        phone = st.text_input("شماره تماس", placeholder="۰۹۱۲...")
        reporter_type = st.selectbox(
            "نوع گزارش‌دهنده",
            ["شهروند", "داوطلب", "امدادگر", "پزشک", "اپراتور"]
        )
        affected_option = st.selectbox(
            "تعداد افراد درگیر",
            ["نامشخص", "کمتر از ۱۰ نفر", "۱۰ تا ۵۰ نفر", "۵۰ تا ۲۰۰ نفر", "بیشتر از ۲۰۰ نفر"]
        )

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── Section 2: Human Status ──
    section_header("🏥", "وضعیت انسانی")

    injured = st.number_input("تعداد زخمی‌ها", 0, 1000, 0, help="تعداد تخمینی افراد زخمی")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        critical   = st.checkbox("❌ فرد بدحال")
    with c2:
        unconscious = st.checkbox("❕ بیهوش")
    with c3:
        bleeding   = st.checkbox("🩸 خونریزی شدید")
    with c4:
        trapped    = st.checkbox("⚠️ افراد گرفتار")

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── Section 3: Shortages ──
    section_header("📦", "کمبودها و دسترسی")

    col1, col2, col3 = st.columns(3)
    with col1:
        water = st.slider("💧 کمبود آب", 0, 10, 0)
    with col2:
        food = st.slider("🍞 کمبود غذا", 0, 10, 0)
    with col3:
        medicine = st.slider("💊 کمبود دارو", 0, 10, 0)

    blocked = st.checkbox("🚧 مسیر دسترسی مسدود است")

    st.markdown("<hr/>", unsafe_allow_html=True)
    

    # ── Section 4: Description ──
    section_header("📝", "شرح گزارش")

    report_text = st.text_area(
        "توضیحات کامل وضعیت",
        height=150,
        placeholder="شرح کاملی از وضعیت فعلی، نوع حادثه، نیازهای فوری و هر اطلاعات مرتبط دیگری را وارد کنید..."
    )

    st.markdown("<br/>", unsafe_allow_html=True)

    if st.button("📊 تحلیل و ثبت گزارش", use_container_width=True):

        if not area:
            st.error("⚠️ نام منطقه الزامی است")
            return
        
        if not phone:
            st.error("⚠️ َشماره تماس الزامی است")
            return

        with st.spinner("در حال تحلیل گزارش..."):
            affected_people = convert_people(affected_option)
            nlp_result = analyze_report_text(report_text)
            epi_score  = calculate_epi(
                affected_people, injured, critical, unconscious,
                bleeding, trapped, water, food, medicine, blocked, nlp_result
            )
            priority = get_priority_level(epi_score)
            recommendations = recommend_resources(
                epi_score, priority, affected_people, injured,
                critical, unconscious, bleeding, trapped,
                water, food, medicine, blocked, nlp_result
            )

        report = {
            "timestamp":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "region":          area,
            "name":            name,
            "lastname":        lastname,
            "phone":           phone,
            "epi_score":       epi_score,
            "priority":        priority,
            "affected_people": affected_people,
            "injured":         injured,
            "critical":        critical,
            "unconscious":     unconscious,
            "bleeding":        bleeding,
            "trapped":         trapped,
            "water":           water,
            "food":            food,
            "medicine":        medicine,
            "blocked":         blocked,
            "text":            report_text
        }
        save_report(report)

        st.success("✅ گزارش با موفقیت ثبت شد")
        show_results(area, epi_score, priority, nlp_result, recommendations)


# -----------------------------
# Results UI
# -----------------------------
def show_results(area, epi_score, priority, nlp_result, recommendations):

    st.markdown("---")
    section_header("📌", "نتیجه تحلیل")

    # Priority badge mapping
    badge_map = {
        "بحرانی": ("critical", "🔴"),
        "بالا":   ("high",     "🟠"),
        "متوسط":  ("medium",   "🟡"),
        "پایین":  ("low",      "🟢"),
    }
    badge_class, badge_icon = badge_map.get(priority, ("low", "⚪"))

    # EPI banner + priority badge
    st.markdown(f"""
    <div class="epi-result-banner">
        <div class="epi-number">{epi_score}</div>
        <div class="epi-label">امتیاز اولویت اضطراری (EPI)</div>
        <br/>
        <span class="status-badge {badge_class}">{badge_icon} {priority}</span>
        &nbsp;
        <span style="color:#6e7681; font-size:0.85rem">منطقه: {area}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # NLP Analysis
    with st.expander("🔬 تحلیل متن (NLP)", expanded=False):
        st.json(nlp_result)

    st.markdown("---")
    section_header("🛠", "توصیه‌های عملیاتی")

    col1, col2 = st.columns(2)

    with col1:
        # Teams
        teams_html = "".join(f'<div class="rec-item">{i}</div>' for i in recommendations.get("teams", []))
        st.markdown(f"""
        <div class="rec-section">
            <h4>👥 تیم‌های پیشنهادی</h4>
            {teams_html}
        </div>
        """, unsafe_allow_html=True)

        # Items
        items_html = "".join(f'<div class="rec-item">{i}</div>' for i in recommendations.get("items", []))
        st.markdown(f"""
        <div class="rec-section">
            <h4>📦 اقلام مورد نیاز</h4>
            {items_html}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Transport
        transport_html = "".join(f'<div class="rec-item">{i}</div>' for i in recommendations.get("transport", []))
        st.markdown(f"""
        <div class="rec-section">
            <h4>🚗 حمل و نقل</h4>
            {transport_html}
        </div>
        """, unsafe_allow_html=True)

        # Actions
        actions_html = "".join(f'<div class="rec-item">{i}</div>' for i in recommendations.get("actions", []))
        st.markdown(f"""
        <div class="rec-section">
            <h4>⚡ اقدامات فوری</h4>
            {actions_html}
        </div>
        """, unsafe_allow_html=True)


# -----------------------------
# Reports Dashboard Page
# -----------------------------
def render_reports():

    st.markdown("""
    <div class="page-header">
        <span class="ph-icon">📁</span>
        <div>
            <h1>داشبورد گزارش‌ها</h1>
            <p>مانیتورینگ زنده و تحلیل کلیه گزارش‌های ثبت‌شده</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df = get_all_reports()

    if df.empty:
        st.markdown("""
        <div style="text-align:center; padding:4rem 2rem; color:#484f58;">
            <div style="font-size:3rem; margin-bottom:1rem;">📭</div>
            <h3 style="color:#6e7681;">هنوز گزارشی ثبت نشده است</h3>
            <p style="font-size:0.9rem;">از منوی ثبت گزارش، اولین رویداد را وارد کنید</p>
        </div>
        """, unsafe_allow_html=True)
        return

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.sort_values("epi_score", ascending=False)

    # ── KPI SECTION ──
    section_header("📊", "آمار کلی سیستم")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("کل گزارش‌ها", len(df))
    col2.metric("میانگین EPI", round(df["epi_score"].mean(), 2))
    col3.metric("بحرانی", len(df[df["priority"] == "بحرانی"]))
    col4.metric("بیشترین EPI", df["epi_score"].max())

    st.markdown("---")

    # ── FILTERS ──
    section_header("🎛", "فیلترها")

    col1, col2 = st.columns(2)
    with col1:
        priority_filter = st.selectbox("سطح بحران", ["همه", "بحرانی", "بالا", "متوسط", "پایین"])
    with col2:
        region_filter = st.selectbox("منطقه", ["همه"] + list(df["region"].dropna().unique()))

    filtered_df = df.copy()
    if priority_filter != "همه":
        filtered_df = filtered_df[filtered_df["priority"] == priority_filter]
    if region_filter != "همه":
        filtered_df = filtered_df[filtered_df["region"] == region_filter]

    st.markdown("---")

    # ── PRIORITY BREAKDOWN ──
    section_header("🔔", "وضعیت بحران‌ها")

    cnt_c = len(filtered_df[filtered_df["priority"] == "بحرانی"])
    cnt_h = len(filtered_df[filtered_df["priority"] == "بالا"])
    cnt_m = len(filtered_df[filtered_df["priority"] == "متوسط"])
    cnt_l = len(filtered_df[filtered_df["priority"] == "پایین"])

    st.markdown(f"""
    <div class="priority-row">
        <div class="prio-box c-red">
            <span class="prio-icon">🔴</span>
            <span class="prio-count">{cnt_c}</span>
            <span class="prio-label">بحرانی</span>
        </div>
        <div class="prio-box c-amber">
            <span class="prio-icon">🟠</span>
            <span class="prio-count">{cnt_h}</span>
            <span class="prio-label">بالا</span>
        </div>
        <div class="prio-box c-blue">
            <span class="prio-icon">🟡</span>
            <span class="prio-count">{cnt_m}</span>
            <span class="prio-label">متوسط</span>
        </div>
        <div class="prio-box c-green">
            <span class="prio-icon">🟢</span>
            <span class="prio-count">{cnt_l}</span>
            <span class="prio-label">پایین</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── CHARTS ──
    section_header("📈", "تحلیل داده‌ها")

    col1, col2 = st.columns(2)

    with col1:
        st.caption("📊 میانگین EPI بر اساس سطح بحران")
        epi_hist = filtered_df.groupby("priority")["epi_score"].mean()
        st.bar_chart(epi_hist, color="#f0a500")

    with col2:
        st.caption("🗺 میانگین EPI مناطق")
        region_avg = filtered_df.groupby("region")["epi_score"].mean()
        st.bar_chart(region_avg, color="#388bfd")

    st.markdown("---")

    # ── TIME SERIES ──
    section_header("📅", "روند زمانی بحران‌ها")

    time_data = filtered_df.dropna(subset=["timestamp"])
    if len(time_data) > 0:
        timeline = time_data.groupby(time_data["timestamp"].dt.date)["epi_score"].mean()
        st.line_chart(timeline, color="#f0a500")
    else:
        st.info("داده زمانی کافی وجود ندارد")

    st.markdown("---")

    # ── INJURY RELATION ──
    section_header("📍", "رابطه شدت بحران و تعداد زخمی‌ها")

    injured_col = "injured" if "injured" in filtered_df.columns else "estimated_injured"
    if injured_col in filtered_df.columns:
        relation_df = filtered_df[[injured_col, "epi_score"]].dropna().sort_values(injured_col)
        st.line_chart(relation_df.set_index(injured_col)["epi_score"], color="#f85149")
    else:
        st.info("داده کافی برای تحلیل رابطه وجود ندارد")

    st.markdown("---")

    # ── REPORT TABLE ──
    section_header("📋", "لیست گزارش‌ها")

    priority_icons = {"بحرانی": "🔴", "بالا": "🟠", "متوسط": "🟡", "پایین": "🟢"}

    display_df = filtered_df.copy()
    display_df.insert(0, "وضعیت", display_df["priority"].map(priority_icons).fillna("⚪"))

    preferred_order = ["وضعیت", "region", "epi_score", "priority", "affected_people", "estimated_injured", "timestamp"]
    existing_cols   = [c for c in preferred_order if c in display_df.columns]
    other_cols      = [c for c in display_df.columns if c not in existing_cols]

    display_df = display_df[existing_cols + other_cols]

    st.dataframe(display_df, use_container_width=True, hide_index=True, height=500)

    st.markdown("---")

    # ── TOP REPORTS ──
    section_header("🚨", "مهم‌ترین گزارش‌ها")

    top_reports = filtered_df.sort_values("epi_score", ascending=False).head(5)

    if top_reports.empty:
        st.info("گزارش قابل نمایش وجود ندارد.")
        return

    card_map = {
        "بحرانی": "card-red",
        "بالا":   "card-amber",
        "متوسط":  "card-blue",
        "پایین":  "card-green",
    }
    icon_map = {"بحرانی": "🔴", "بالا": "🟠", "متوسط": "🟡", "پایین": "🟢"}

    for _, row in top_reports.iterrows():
        priority = row.get("priority", "نامشخص")
        card_cls = card_map.get(priority, "card-green")
        icon     = icon_map.get(priority, "⚪")
        ts       = str(row.get("timestamp", ""))[:16]

        st.markdown(f"""
        <div class="report-card {card_cls}">
            <span style="font-size:1.4rem">{icon}</span>
            <div>
                <div class="rc-region">{row['region']}</div>
                <div class="rc-meta">{ts}</div>
            </div>
            <div class="rc-epi">{row['epi_score']}</div>
            <span class="status-badge {card_cls.replace('card-','').replace('red','critical').replace('amber','high').replace('blue','medium').replace('green','low')}">{priority}</span>
        </div>
        """, unsafe_allow_html=True)


# -----------------------------
# Sidebar + Router
# -----------------------------
def main():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <span class="brand-icon">🛡️</span>
            <h2>EPDS</h2>
            <p>سامانه اولویت‌بندی اضطراری</p>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "ناوبری",
            ["🚨 ثبت گزارش", "📁 داشبورد گزارش‌ها"],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("""
        <div style="padding: 0 0.5rem;">
            <div style="font-size:0.72rem; color:#484f58; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.75rem;">راهنما</div>
            <div style="font-size:0.82rem; color:#6e7681; line-height:1.8;">
                🔴 بحرانی — EPI ≥ ۸۰<br/>
                🟠 بالا — EPI ۶۰–۷۹<br/>
                🟡 متوسط — EPI ۴۰–۵۹<br/>
                🟢 پایین — EPI &lt; ۴۰
            </div>
        </div>
        """, unsafe_allow_html=True)

    if "ثبت گزارش" in page:
        render_form()
    else:
        render_reports()


if __name__ == "__main__":
    init_db()
    main()
