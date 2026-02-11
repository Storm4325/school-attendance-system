import streamlit as st
import pandas as pd
import requests
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام مدرسة الشيخ عبدالعزيز", page_icon="🏫", layout="wide")

# الروابط الخاصة بك
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQXCHOY9CHVwdruWhQEvhtgZm9gadjqY_PGHobJvG2OcqZ4Md1e3MxMctBVP6OwYpbq0Fvv5PuQFJ33/pub?output=csv"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwhLnded5J9fR4nOK_CJSp_ROwmpSsgH3Y02CgDTF31hjCrrqAY7OpuZ-qXPAoCy3cA/exec"

CLASS_NAMES = {"11": "1 علم 1", "12": "1 علم 2", "21": "2 علم 1", "22": "2 علم 2", "31": "3 علم 1", "32": "3 علم 2"}

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Cairo', sans-serif; direction: rtl !important; text-align: right !important;
        background: linear-gradient(-45deg, #e0e7ff, #f8fafc, #c7d2fe, #ffffff);
        background-size: 400% 400%; animation: gradientBG 15s ease infinite; background-attachment: fixed;
    }
    
    @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }

    /* حل مشكلة التداخل في حقول الإدخال */
    .stTextInput div[data-baseweb="input"] {
        margin-top: 10px !important;
        margin-bottom: 5px !important;
    }

    [data-testid="stTextInput"] input {
        text-align: left !important;
        direction: ltr !important;
    }

    .login-header {
        text-align: center !important;
        color: #1e3a8a;
        font-weight: 900;
        margin-bottom: 20px;
    }

    .sidebar-user {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 10px;
        flex-direction: row-reverse;
        font-weight: 700;
        font-size: 1.2rem;
        color: #1e3a8a;
    }

    .student-card {
        background: rgba(255, 255, 255, 0.4); backdrop-filter: blur(10px);
        padding: 20px; border-radius: 18px; border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 12px; text-align: right; transition: all 0.3s ease;
    }
    .student-card:hover { background: rgba(255, 255, 255, 0.7); transform: scale(1.005); border-right: 10px solid #1e3a8a; }

    .glass-header {
        background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(15px);
        border-radius: 20px; padding: 20px; border: 1px solid rgba(255, 255, 255, 0.3);
        text-align: center !important; margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# استدعاء الرابط من Secrets (لحماية قاعدة البيانات)
db_url = st.secrets.get("DATABASE_URL") or os.getenv("DATABASE_URL")
if db_url:
    engine = create_engine(db_url)

if 'auth' not in st.session_state: st.session_state.auth = False
if 'attendance' not in st.session_state: st.session_state.attendance = {}
if 'submitted' not in st.session_state: st.session_state.submitted = False

def update_pwd(u, p):
    try:
        r = requests.post(SCRIPT_URL, json={"username": u, "newPassword": p})
        return r.text == "Success"
    except: return False

# --- واجهة تسجيل الدخول ---
if not st.session_state.auth:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown('<div style="background: rgba(255,255,255,0.3); padding:35px; border-radius:25px; border: 1px solid rgba(255,255,255,0.4);">', unsafe_allow_html=True)
        st.markdown('<h2 class="login-header">🏫 دخول النظام</h2>', unsafe_allow_html=True)
        u = st.text_input("اسم المستخدم", placeholder="Username")
        p = st.text_input("كلمة المرور", type="password", placeholder="••••••••")
        if st.button("دخول", use_container_width=True):
            df = pd.read_csv(CSV_URL)
            match = df[(df['username'].astype(str) == u) & (df['password'].astype(str) == p)]
            if not match.empty:
                st.session_state.auth = True
                st.session_state.user_info = match.iloc[0].to_dict()
                st.rerun()
            else: st.error("❌ بيانات خاطئة")
        st.markdown('</div>', unsafe_allow_html=True)

# --- النظام الرئيسي ---
else:
    with st.sidebar:
        st.markdown(f'<div class="sidebar-user"><span>الأستاذ {st.session_state.user_info["full_name"]}</span><span style="font-size:1.5rem;">👤</span></div>', unsafe_allow_html=True)
        st.divider()
        with st.expander("🔑 تغيير كلمة المرور"):
            new_p = st.text_input("كلمة المرور الجديدة", type="password")
            confirm_p = st.text_input("تأكيد الكلمة", type="password")
            if st.button("حفظ وتحديث الشيت", use_container_width=True):
                if new_p and new_p == confirm_p:
                    if update_pwd(st.session_state.user_info['username'], new_p):
                        st.success("✅ تم التحديث")
                    else: st.error("⚠️ فشل الاتصال")
                else: st.warning("⚠️ لا يوجد تطابق")
        if st.button("🚪 خروج", use_container_width=True):
            st.session_state.auth = False
            st.rerun()

    st.markdown(f'<div class="glass-header"><h1 style="color:#1e3a8a; margin:0;">🏫 نظام مدرسة الشيخ عبدالعزيز</h1><p>الأستاذ {st.session_state.user_info["full_name"]}</p></div>', unsafe_allow_html=True)

    _, col_choice, _ = st.columns([1, 2, 1])
    with col_choice:
        try:
            with engine.connect() as conn:
                raw_sec = [row[0] for row in conn.execute(text("SELECT DISTINCT class_section FROM students ORDER BY class_section"))]
            display_map = {CLASS_NAMES.get(s, f"صف {s}"): s for s in raw_sec}
            st.markdown('<p style="color:black; font-weight:900; text-align:center;">🎯 اختر الفصل الدراسي:</p>', unsafe_allow_html=True)
            choice_label = st.selectbox("", ["-- اختر --"] + list(display_map.keys()), label_visibility="collapsed")
            choice = display_map.get(choice_label)
        except: choice = None

    if choice:
        st.write("---")
        with engine.connect() as conn:
            res = conn.execute(text("SELECT student_id, full_name, cpr, serial_number FROM students WHERE class_section = :c ORDER BY full_name"), {"c": choice}).fetchall()
        
        for s in res:
            sid, name, cpr, serial = s
            status = st.session_state.attendance.get(sid, None)
            st.markdown(f'<div class="student-card"><div style="color:#1e3a8a; font-weight:900; font-size:1.6rem;">{name}</div><div style="font-weight:bold; color:#475569;">🆔: {sid} | 💳: {cpr} | 🔢: {serial}</div></div>', unsafe_allow_html=True)
            c1, c2, c3, _ = st.columns([1.5, 1.5, 1.5, 5])
            with c1:
                if st.button("🚫 غياب", key=f"a_{sid}", use_container_width=True, disabled=st.session_state.submitted or status == 'absent'):
                    st.session_state.attendance[sid] = 'absent'; st.rerun()
            with c2:
                dis = (status == 'late') if not st.session_state.submitted else (status != 'absent')
                if st.button("⏰ تأخير", key=f"l_{sid}", use_container_width=True, disabled=dis):
                    st.session_state.attendance[sid] = 'late'; st.rerun()
            with c3:
                if st.button("🔄 تراجع", key=f"r_{sid}", use_container_width=True, disabled=st.session_state.submitted):
                    st.session_state.attendance.pop(sid, None); st.rerun()

        if st.session_state.attendance:
            abs_c = list(st.session_state.attendance.values()).count('absent')
            lat_c = list(st.session_state.attendance.values()).count('late')
            st.markdown(f'<div style="background:rgba(30,58,138,0.1); padding:20px; border-radius:20px; border:2px solid #1e3a8a; text-align:center;"><h3>📊 ملخص الرصد</h3><p>الغياب: {abs_c} | التأخير: {lat_c}</p></div>', unsafe_allow_html=True)
            if not st.session_state.submitted:
                if st.button("🚀 اعتماد التقرير النهائي", type="primary", use_container_width=True):
                    st.session_state.submitted = True
                    st.balloons()
                    st.rerun()
