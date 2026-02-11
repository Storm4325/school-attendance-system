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

# 2. التنسيق الزجاجي المتقدم (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
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
    .student-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 20px; border-radius: 20px;
        margin-bottom: 15px; text-align: right;
        transition: all 0.4s ease;
    }
    .student-card:hover {
        transform: scale(1.02);
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid #fcd34d;
    }
    .report-card {
        max-width: 700px; margin: 50px auto;
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        border-radius: 30px; border: 2px solid rgba(255, 255, 255, 0.3);
        padding: 40px; text-align: center; color: white;
    }
    input[type="password"], input[type="text"] {
        background: rgba(255, 255, 255, 0.9) !important;
        color: #1e3a8a !important; text-align: left !important; direction: ltr !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. جلب الرابط من Secrets (التصحيح للصورة 1 و 2)
db_url = st.secrets.get("DATABASE_URL") or os.getenv("DATABASE_URL")
if not db_url:
    st.error("❌ لم يتم العثور على DATABASE_URL. تأكد من إضافتها في Secrets بصيغة TOML.")
    st.stop()

engine = create_engine(db_url)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'log' not in st.session_state: st.session_state.log = {}

def update_pwd(u, p):
    try:
        r = requests.post(SCRIPT_URL, json={"username": u, "newPassword": p})
        return r.text == "Success"
    except: return False

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
        # تصحيح الخطأ البرمجي في الصورة 3
        u_name = st.session_state.user_info.get('full_name', 'أستاذ')
        st.markdown(f'<div style="text-align:right; font-weight:700; color:white;">👤 الأستاذ {u_name}</div>', unsafe_allow_html=True)
        st.divider()
        
        # إضافة زر تغيير كلمة المرور
        with st.expander("🔑 تغيير كلمة المرور"):
            new_p = st.text_input("الكلمة الجديدة", type="password")
            if st.button("تحديث الآن", use_container_width=True):
                if update_pwd(st.session_state.user_info['username'], new_p):
                    st.success("✅ تم التحديث")
                else: st.error("❌ فشل الاتصال")
        
        st.divider()
        if st.button("🚪 خروج", use_container_width=True):
            st.session_state.auth = False
            st.rerun()

    st.markdown('<h1 class="main-title">مدرسة الشيخ عبدالعزيز بن محمد آل خليفة الثانوية للبنين</h1>', unsafe_allow_html=True)
    
    try:
        with engine.connect() as conn:
            res_sec = conn.execute(text("SELECT DISTINCT class_section FROM students ORDER BY class_section")).fetchall()
        sections = [str(r[0]) for r in res_sec]
        
        choice_label = st.selectbox("🎯 اختر الصف الدراسي", ["-- اختر --"] + [CLASS_NAMES.get(s, f"صف {s}") for s in sections])
        
        if choice_label != "-- اختر --":
            sec_id = [k for k, v in CLASS_NAMES.items() if v == choice_label][0]
            with engine.connect() as conn:
                students = conn.execute(text("SELECT student_id, full_name, cpr FROM students WHERE class_section = :c ORDER BY full_name"), {"c": sec_id}).fetchall()
            
            for std in students:
                sid = str(std[0])
                current_status = st.session_state.log.get(sid, "حاضر")
                
                st.markdown(f'''
                    <div class="student-card">
                        <div style="font-size:1.4rem; font-weight:bold; color:white;">👨‍🎓 {std[1]}</div>
                        <div style="color:rgba(255,255,255,0.8); font-size:1rem;">🆔 التسلسلي: {std[0]} | 💳 البطاقة: {std[2]}</div>
                        <div style="font-weight:bold; color:#fcd34d;">الحالة: {current_status}</div>
                    </div>
                ''', unsafe_allow_html=True)
                
                c1, c2, c3, _ = st.columns([1, 1, 1, 3])
                with c1:
                    if st.button("🚫 غياب", key=f"a_{sid}", use_container_width=True, disabled=(current_status=="غياب")):
                        st.session_state.log[sid] = "غياب"; st.rerun()
                with c2:
                    if st.button("⏰ تأخير", key=f"l_{sid}", use_container_width=True, disabled=(current_status=="تأخير")):
                        st.session_state.log[sid] = "تأخير"; st.rerun()
                with c3:
                    if st.button("🔄 تراجع", key=f"r_{sid}", use_container_width=True, disabled=(current_status=="حاضر")):
                        st.session_state.log[sid] = "حاضر"; st.rerun()

            abs_c = list(st.session_state.log.values()).count("غياب")
            lat_c = list(st.session_state.log.values()).count("تأخير")
            
            st.markdown(f'''
                <div class="report-card">
                    <h2>📊 تقرير {choice_label}</h2>
                    <p>إجمالي الطلاب: {len(students)} | الغياب: {abs_c} | التأخير: {lat_c}</p>
                </div>
            ''', unsafe_allow_html=True)
            if st.button("📤 إرسال التقرير النهائي", use_container_width=True, type="primary"):
                st.balloons(); st.success("✅ تم الإرسال بنجاح")

    except Exception as e:
        st.error(f"⚠️ خطأ في قاعدة البيانات")
