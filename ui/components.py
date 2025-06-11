"""
ui/components.py - רכיבי UI משותפים
"""
import streamlit as st
from PIL import Image
import pandas as pd

def display_header():
    """הצגת כותרת ולוגו של האפליקציה"""
    logo = Image.open("logo.png")
    col1, col2 = st.columns([0.4, 5])
    with col1:
        st.image(logo, width=75)
    with col2:
        st.markdown('<span style="font-size:2.2rem; font-weight:bold; color:#fff; letter-spacing:1px; margin-top:-20px; padding-top:0; display:block;">CashFlowIQ</span>', unsafe_allow_html=True)

def render_list_of_dicts_table(lst):
    """הצגת רשימה של מילונים כטבלה"""
    if not lst:
        st.info("No data available.")
        return
    df = pd.DataFrame(lst)
    st.table(df)

def render_vertical_table(data):
    """הצגת מילון כטבלה אנכית"""
    rows = []
    for k, v in data.items():
        if isinstance(v, (list, tuple)):
            v = ', '.join(str(i) for i in v)
        elif isinstance(v, dict):
            v = ', '.join([f"{ik}: {iv}" for ik, iv in v.items()])
        rows.append({"Field": k, "Value": v})
    df = pd.DataFrame(rows)
    st.table(df)

def render_warning_table(val, title):
    """הצגת אזהרות בצורה טבלאית"""
    if isinstance(val, list) and val and isinstance(val[0], dict):
        st.warning(f"{title}:")
        render_list_of_dicts_table(val)
    elif isinstance(val, list):
        st.warning(f"{title}:<ul>" + ''.join([f"<li>{v}</li>" for v in val]) + "</ul>", unsafe_allow_html=True)
    elif val:
        st.warning(f"{title}: {val}")

def convert_df_to_csv(df):
    """המרת DataFrame ל-CSV להורדה"""
    return df.to_csv(index=False).encode('utf-8')

def display_chat_message(role, content):
    """הצגת הודעת צ'אט מעוצבת"""
    if role == 'user':
        st.markdown(f"<div style='text-align:left; background:#181943; padding:8px; border-radius:8px; margin-bottom:4px; color:black;'><b>You:</b> {content}</div>", unsafe_allow_html=True)
    else:
        # תמיד מיושר לשמאל (LTR)
        if content.strip().startswith('1.') or '\n1.' in content:
            items = [line.strip() for line in content.split('\n') if line.strip() and (line.strip()[0].isdigit() and line.strip()[1] in ['.',')'])]
            if items:
                st.markdown("<div style='text-align:left; background:#23255d; padding:8px; border-radius:8px; margin-bottom:8px; color:black;'><b>AI:</b><ul style='text-align:left; color:black;'>" + ''.join([f"<li>{v}</li>" for v in items]) + "</ul></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:left; background:#23255d; padding:8px; border-radius:8px; margin-bottom:8px; color:black;'><b>AI:</b> {content}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:left; background:#23255d; padding:8px; border-radius:8px; margin-bottom:8px; color:black;'><b>AI:</b> {content}</div>", unsafe_allow_html=True) 