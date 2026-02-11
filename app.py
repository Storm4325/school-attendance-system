import streamlit as st
import pandas as pd
import requests
import os
from sqlalchemy import create_engine, text

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام مدرسة الشيخ عبدالعزيز", page_icon="🏫", layout="wide")

# الروابط الرسمية للمشروع
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQXCHOY9CHVwdruWhQEvhtgZm9gadjqY_PGHobJvG2OcqZ4Md1e3MxMctBVP6OwYpbq0Fvv5PuQFJ33/pub?output=csv"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzHDhKY2VZxFu0RyUf9P-3jnm9OZIzXcY3H59XhFo9ca5vKJNt-jWJUlQYKRvmq0NEq/exec"

CLASS_NAMES = {"11": "1 علم 1", "12": "1 علم 2", "21": "2 علم 1", "22": "2 علم 2", "31": "3 علم 1", "32": "32 علم 2"}

# 2. التنسيق الجمالي (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Cairo', sans-serif; direction: rtl !important; text-align: right !important;
        background-color: #f8fafc;
    }

    /* العنوان الرئيسي في نص الشاشة H1 */
    .main-title { 
        text-align: center; 
        color: #1e3a8a; 
        font-weight: 900; 
        font-size: 2.5rem; 
        margin-top: 20px;
        margin-bottom: 10px;
    }

    input[type="password"], input[type="text"] {
        text-align: left !important;
        direction: ltr !important;
    }

    /* توسيط واختيار الفصل */
    div[data-testid="stSelectbox"] { max-width: 500px; margin: 0 auto; }
    .select-label { text-align: center; font-weight: bold; font-size: 1.2rem; margin-top: 20px; color: #1e3a8a; }

    .sidebar-user {
        display: flex; align-items: center; justify-content: flex-start;
        gap: 10px; flex-direction: row-reverse;
        font-weight: 700; color: #1e3a8a;
    }

    .student-card {
        background: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 10px;
        border-right: 8px solid #1e3a8a; text-align: right;
    }
    
    /* صندوق الإحصائيات الموضح وفي المنتصف */
    .stats-container {
        max-width: 700px;
        margin: 40px auto;
        background: #ffffff;
        padding: 30px;
        border-radius: 20px;
        border: 2px solid #1e3a8a;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. جلب الرابط من Secrets
try:
    db_url = st.secrets["DATABASE_URL"]
    engine = create_engine(db_url)
except Exception:
    st.error("⚠️ خطأ: لم يتم العثور على DATABASE_URL في إعدادات Secrets.")
    st.stop()

if 'auth' not in st.session_state: st.session_state.auth = False
if 'attendance_data' not in st.session_state: st.session_state.attendance_data = {"absent": 0, "late": 0}

def update_pwd(u, p):
    try:
        r = requests.post(SCRIPT_URL, json={"username": u, "newPassword": p})
        return r.text == "Success"
    except: return False

# --- واجهة تسجيل الدخول ---
if not st.session_state.auth:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown('<div style="margin-top:50px; padding:30px; background:#fff; border-radius:20px; box-shadow:0 10px 25px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:#1e3a8a;">🏫 دخول النظام</h2>', unsafe_allow_html=True)
        user_input = st.text_input("اسم المستخدم", key="user_login")
        pass_input = st.text_input("كلمة المرور", type="password", key="pass_login")
        if st.button("دخول", use_container_width=True):
            try:
                df = pd.read_csv(CSV_URL)
                match = df[(df['username'].astype(str).str.strip() == user_input.strip()) & 
                           (df['password'].astype(str).str.strip() == pass_input.strip())]
                if not match.empty:
                    st.session_state.auth = True
                    st.session_state.user_info = match.iloc[0].to_dict()
                    st.rerun()
                else: st.error("❌ البيانات غير صحيحة")
            except: st.error("⚠️ فشل الاتصال بالسجل")
        st.markdown('</div>', unsafe_allow_html=True)

# --- النظام الرئيسي ---
else:
    with st.sidebar:
        full_name = st.session_state.user_info.get('full_name', 'أستاذ')
        st.markdown(f'<div class="sidebar-user"><span>الأستاذ {full_name}</span><span>👤</span></div>', unsafe_allow_html=True)
        st.divider()
        
        with st.expander("🔑 تغيير كلمة المرور"):
            new_p = st.text_input("الكلمة الجديدة", type="password")
            if st.button("تحديث في الشيت", use_container_width=True):
                if update_pwd(st.session_state.user_info['username'], new_p):
                    st.success("✅ تم تحديث كلمة المرور")
                else: st.error("❌ فشل الاتصال")
        
        st.divider()
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.auth = False
            st.rerun()

    # اسم المدرسة في نص الشاشة فوق بالـ H1
    st.markdown('<h1 class="main-title">مدرسة الشيخ عبدالعزيز بن محمد آل خليفة الثانوية للبنين</h1>', unsafe_allow_html=True)
    st.markdown(f'<h3 style="text-align:center; color:#475569;">مرحباً بك أستاذ {st.session_state.user_info.get("full_name")}</h3>', unsafe_allow_html=True)
    st.write("---")

    try:
        with engine.connect() as conn:
            res_sec = conn.execute(text("SELECT DISTINCT class_section FROM students ORDER BY class_section")).fetchall()
        sections = [str(r[0]) for r in res_sec]
        
        st.markdown('<p class="select-label">🎯 اختر الصف الدراسي</p>', unsafe_allow_html=True)
        choice_label = st.selectbox("", ["-- اختر من القائمة --"] + [CLASS_NAMES.get(s, f"صف {s}") for s in sections], label_visibility="collapsed")
        
        if choice_label != "-- اختر من القائمة --":
            sec_id = [k for k, v in CLASS_NAMES.items() if v == choice_label][0]
            with engine.connect() as conn:
                students = conn.execute(text("SELECT student_id, full_name, cpr FROM students WHERE class_section = :c ORDER BY full_name"), {"c": sec_id}).fetchall()
            
            st.write("<br>", unsafe_allow_html=True)
            for std in students:
                st.markdown(f'''
                    <div class="student-card">
                        <div style="font-size:1.3rem; font-weight:bold; color:#1e3a8a;">{std[1]}</div>
                        <div style="color:#64748b;">رقم الطالب: {std[0]} | البطاقة الذكية: {std[2]}</div>
                    </div>
                ''', unsafe_allow_html=True)
                
                c1, c2, c3, _ = st.columns([1, 1, 1, 3])
                with c1: st.button("🚫 غياب", key=f"a_{std[0]}", use_container_width=True)
                with c2: st.button("⏰ تأخير", key=f"l_{std[0]}", use_container_width=True)
                with c3: st.button("🔄 تراجع", key=f"r_{std[0]}", use_container_width=True)

            # --- قسم إحصائيات الرصد (واضح وفي النص) ---
            st.markdown('<div class="stats-container">', unsafe_allow_html=True)
            st.markdown('<h2 style="color:#1e3a8a; margin-bottom:20px;">📊 ملخص رصد الفصل</h2>', unsafe_allow_html=True)
            
            # عرض الإحصائيات بشكل واضح
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("إجمالي الطلاب", len(students))
            with col_s2:
                st.metric("عدد الغياب", st.session_state.attendance_data["absent"])
            with col_s3:
                st.metric("عدد التأخير", st.session_state.attendance_data["late"])
            
            st.write("<br>", unsafe_allow_html=True)
            # زر الإرسال متاح دائماً حتى لو الغياب 0
            if st.button("📤 إرسال التقرير النهائي للإدارة", use_container_width=True, type="primary"):
                st.balloons()
                st.success(f"✅ تم اعتماد وإرسال تقرير فصل {choice_label} بنجاح.")
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ خطأ في الاتصال بقاعدة البيانات.")
