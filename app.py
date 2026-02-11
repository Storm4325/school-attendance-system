import streamlit as st
import pandas as pd
import requests
import os
from sqlalchemy import create_engine, text

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام مدرسة الشيخ عبدالعزيز", page_icon="🏫", layout="wide")

# الروابط الرسمية
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQXCHOY9CHVwdruWhQEvhtgZm9gadjqY_PGHobJvG2OcqZ4Md1e3MxMctBVP6OwYpbq0Fvv5PuQFJ33/pub?output=csv"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzHDhKY2VZxFu0RyUf9P-3jnm9OZIzXcY3H59XhFo9ca5vKJNt-jWJUlQYKRvmq0NEq/exec"

CLASS_NAMES = {"11": "1 علم 1", "12": "1 علم 2", "21": "2 علم 1", "22": "2 علم 2", "31": "3 علم 1", "32": "32 علم 2"}

# 2. التنسيق الزجاجي المتقدم مع التفاعل (Advanced CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    /* خلفية متحركة زجاجية */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, #1e3a8a, #3b82f6, #0f172a, #1e40af);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        font-family: 'Cairo', sans-serif;
        direction: rtl !important;
    }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .main-title { 
        text-align: center; color: white !important; font-weight: 900; 
        font-size: 2.8rem; text-shadow: 2px 2px 10px rgba(0,0,0,0.3); margin: 20px 0;
    }

    /* بطاقة الطالب الزجاجية مع تفاعل التكبير */
    .student-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 20px; border-radius: 20px;
        margin-bottom: 15px; 
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        text-align: right; /* محاذاة الأسماء لليمين */
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* تأثير حركي مرن */
    }

    /* تفاعل عند مرور الماوس على اسم الطالب */
    .student-card:hover {
        transform: scale(1.02); /* تكبير بسيط */
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid #fcd34d; /* تغيير لون الحدود للأصفر الذهبي عند التفاعل */
    }

    .student-name {
        font-size: 1.5rem; font-weight: bold; color: white; margin-bottom: 5px;
    }

    .student-info {
        color: rgba(255, 255, 255, 0.8); font-size: 1rem;
    }

    /* صندوق التقرير الزجاجي الموسط */
    .report-card {
        max-width: 700px; margin: 50px auto;
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        border-radius: 30px; border: 2px solid rgba(255, 255, 255, 0.3);
        padding: 40px; text-align: center; color: white;
    }

    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 900 !important; }
    [data-testid="stMetricLabel"] { color: #d1d5db !important; }

    /* تحسين شكل الأزرار */
    .stButton>button {
        border-radius: 12px; border: none; font-weight: bold; transition: all 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. جلب الرابط من Secrets
try:
    db_url = st.secrets["DATABASE_URL"]
    engine = create_engine(db_url)
except:
    st.error("⚠️ خطأ في إعدادات DATABASE_URL")
    st.stop()

if 'auth' not in st.session_state: st.session_state.auth = False
if 'log' not in st.session_state: st.session_state.log = {}

# --- واجهة تسجيل الدخول ---
if not st.session_state.auth:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown('<div style="margin-top:50px; padding:30px; background:rgba(255,255,255,0.2); backdrop-filter:blur(20px); border-radius:25px; border:1px solid rgba(255,255,255,0.3);">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:white;">🏫 دخول النظام</h2>', unsafe_allow_html=True)
        u_in = st.text_input("اسم المستخدم", key="u_l")
        p_in = st.text_input("كلمة المرور", type="password", key="p_l")
        if st.button("دخول", use_container_width=True):
            df = pd.read_csv(CSV_URL)
            match = df[(df['username'].astype(str).str.strip() == u_in.strip()) & (df['password'].astype(str).str.strip() == p_in.strip())]
            if not match.empty:
                st.session_state.auth = True
                st.session_state.user_info = match.iloc[0].to_dict()
                st.rerun()
            else: st.error("❌ البيانات غير صحيحة")
        st.markdown('</div>', unsafe_allow_html=True)

# --- النظام الرئيسي ---
else:
    with st.sidebar:
        st.markdown(f'<div style="text-align:right; font-weight:700; color:white;">👤 الأستاذ {st.session_state.user_info.get('full_name')}</div>', unsafe_allow_html=True)
        st.divider()
        if st.button("🚪 خروج", use_container_width=True):
            st.session_state.auth = False
            st.rerun()

    st.markdown('<h1 class="main-title">مدرسة الشيخ عبدالعزيز بن محمد آل خليفة الثانوية للبنين</h1>', unsafe_allow_html=True)
    st.write("---")

    try:
        with engine.connect() as conn:
            res_sec = conn.execute(text("SELECT DISTINCT class_section FROM students ORDER BY class_section")).fetchall()
        sections = [str(r[0]) for r in res_sec]
        
        st.markdown('<p style="text-align:center; color:white; font-size:1.2rem;">🎯 اختر الصف الدراسي</p>', unsafe_allow_html=True)
        choice_label = st.selectbox("", ["-- اختر --"] + [CLASS_NAMES.get(s, f"صف {s}") for s in sections], label_visibility="collapsed")
        
        if choice_label != "-- اختر --":
            sec_id = [k for k, v in CLASS_NAMES.items() if v == choice_label][0]
            with engine.connect() as conn:
                students = conn.execute(text("SELECT student_id, full_name, cpr FROM students WHERE class_section = :c ORDER BY full_name"), {"c": sec_id}).fetchall()
            
            for std in students:
                sid = str(std[0])
                current_status = st.session_state.log.get(sid, "حاضر")
                
                # بطاقة الطالب التفاعلية مع محاذاة لليمين
                st.markdown(f'''
                    <div class="student-card">
                        <div class="student-name">👨‍🎓 {std[1]}</div>
                        <div class="student-info">
                            🆔 الرقم التسلسلي: {std[0]} <br>
                            💳 بطاقة الهوية (CPR): {std[2]}
                        </div>
                        <div style="margin-top:10px; font-weight:bold; color:#fcd34d;">الحالة المرصودة: {current_status}</div>
                    </div>
                ''', unsafe_allow_html=True)
                
                c1, c2, c3, _ = st.columns([1, 1, 1, 3])
                with c1:
                    if st.button("🚫 غياب", key=f"a_{sid}", use_container_width=True, disabled=(current_status=="غياب")):
                        st.session_state.log[sid] = "غياب"
                        st.rerun()
                with c2:
                    if st.button("⏰ تأخير", key=f"l_{sid}", use_container_width=True, disabled=(current_status=="تأخير")):
                        st.session_state.log[sid] = "تأخير"
                        st.rerun()
                with c3:
                    if st.button("🔄 تراجع", key=f"r_{sid}", use_container_width=True, disabled=(current_status=="حاضر")):
                        st.session_state.log[sid] = "حاضر"
                        st.rerun()

            # --- التقرير النهائي التفاعلي ---
            abs_count = list(st.session_state.log.values()).count("غياب")
            lat_count = list(st.session_state.log.values()).count("تأخير")
            
            st.markdown('<div class="report-card">', unsafe_allow_html=True)
            st.markdown(f'<h2 style="color:white; margin-bottom:20px;">📊 ملخص تقرير {choice_label}</h2>', unsafe_allow_html=True)
            
            r1, r2, r3 = st.columns(3)
            r1.metric("👥 إجمالي الطلاب", len(students))
            r2.metric("🚫 الغياب", abs_count)
            r3.metric("⏰ التأخير", lat_count)
            
            st.write("<br>", unsafe_allow_html=True)
            if st.button("📤 إرسال التقرير النهائي للإدارة", use_container_width=True, type="primary"):
                st.balloons()
                st.success(f"✅ تم الإرسال: {abs_count} غياب و {lat_count} تأخير.")
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception:
        st.error("❌ حدث خطأ في النظام")
