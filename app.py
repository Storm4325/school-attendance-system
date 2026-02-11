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

# 2. التنسيق الجمالي (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Cairo', sans-serif; direction: rtl !important; text-align: right !important;
        background-color: #f1f5f9;
    }
    .main-title { text-align: center; color: #1e3a8a; font-weight: 900; font-size: 2.5rem; margin: 20px 0; }
    input[type="password"], input[type="text"] { text-align: left !important; direction: ltr !important; }
    .student-card {
        background: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 10px;
        border-right: 8px solid #1e3a8a; text-align: right;
    }
    .report-card {
        max-width: 700px; margin: 50px auto; background: #ebf8ff;
        padding: 40px; border-radius: 25px; border: 3px solid #3182ce;
        text-align: center; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    .status-tag { padding: 2px 10px; border-radius: 5px; font-size: 0.9rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. جلب الرابط من Secrets
try:
    db_url = st.secrets["DATABASE_URL"]
    engine = create_engine(db_url)
except:
    st.error("⚠️ خطأ في إعدادات DATABASE_URL")
    st.stop()

# إدارة الجلسة والذكاء الصناعي للرصد
if 'auth' not in st.session_state: st.session_state.auth = False
if 'log' not in st.session_state: st.session_state.log = {} # لتخزين حالة كل طالب (غياب/تأخير)

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
        st.markdown(f'<div style="text-align:right; font-weight:700; color:#1e3a8a;">👤 الأستاذ {st.session_state.user_info.get("full_name")}</div>', unsafe_allow_html=True)
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
        
        choice_label = st.selectbox("🎯 اختر الصف الدراسي", ["-- اختر --"] + [CLASS_NAMES.get(s, f"صف {s}") for s in sections])
        
        if choice_label != "-- اختر --":
            sec_id = [k for k, v in CLASS_NAMES.items() if v == choice_label][0]
            with engine.connect() as conn:
                students = conn.execute(text("SELECT student_id, full_name, cpr FROM students WHERE class_section = :c ORDER BY full_name"), {"c": sec_id}).fetchall()
            
            for std in students:
                sid = str(std[0])
                current_status = st.session_state.log.get(sid, "حاضر")
                
                # بطاقة الطالب مع الإيموجيات المطلوبة
                st.markdown(f'''
                    <div class="student-card">
                        <div style="font-size:1.2rem; font-weight:bold; color:#1e3a8a;">👨‍🎓 {std[1]}</div>
                        <div style="color:#64748b; font-size:0.9rem;">
                            🆔 الرقم التسلسلي: {std[0]} | 💳 البطاقة الذكية (CPR): {std[2]}
                        </div>
                        <div style="margin-top:5px;">الحالة الحالية: <b>{current_status}</b></div>
                    </div>
                ''', unsafe_allow_html=True)
                
                c1, c2, c3, _ = st.columns([1, 1, 1, 3])
                
                # منطق الأزرار الذكي
                with c1:
                    # زر غياب: متاح دائماً إلا إذا كان الطالب غائباً أصلاً
                    if st.button("🚫 غياب", key=f"a_{sid}", use_container_width=True, disabled=(current_status=="غياب")):
                        st.session_state.log[sid] = "غياب"
                        st.rerun()
                
                with c2:
                    # زر تأخير: متاح للحاضر، وأيضاً للغائب (لتحويله لتأخير)
                    if st.button("⏰ تأخير", key=f"l_{sid}", use_container_width=True, disabled=(current_status=="تأخير")):
                        st.session_state.log[sid] = "تأخير"
                        st.rerun()
                
                with c3:
                    # زر تراجع: لإرجاع الطالب لحالة "حاضر"
                    if st.button("🔄 تراجع", key=f"r_{sid}", use_container_width=True, disabled=(current_status=="حاضر")):
                        st.session_state.log[sid] = "حاضر"
                        st.rerun()

            # --- التقرير الحقيقي والذكي ---
            absent_count = list(st.session_state.log.values()).count("غياب")
            late_count = list(st.session_state.log.values()).count("تأخير")
            
            st.markdown('<div class="report-card">', unsafe_allow_html=True)
            st.markdown(f'<h2 style="color:#2c5282;">📋 تقرير رصد {choice_label} النهائي</h2>', unsafe_allow_html=True)
            
            r1, r2, r3 = st.columns(3)
            r1.metric("👥 إجمالي الفصل", len(students))
            r2.metric("🚫 إجمالي الغياب", absent_count)
            r3.metric("⏰ إجمالي التأخير", late_count)
            
            st.write("<br>", unsafe_allow_html=True)
            if st.button("📤 إرسال التقرير النهائي للإدارة", use_container_width=True, type="primary"):
                st.balloons()
                st.success(f"✅ تم إرسال التقرير: {absent_count} غياب و {late_count} تأخير.")
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ خطأ في النظام")
