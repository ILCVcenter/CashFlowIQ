"""
app.py - נקודת כניסה ראשית לאפליקציית CashFlowIQ
"""
import streamlit as st
from PIL import Image
import logging

# הגדרת logging - מניעת הצגת הודעות בממשק
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger('services').setLevel(logging.WARNING)
logging.getLogger('pages.cash_flow').setLevel(logging.WARNING)
logging.getLogger('pages.contract_analysis').setLevel(logging.WARNING)
logging.getLogger('pages.query_chat').setLevel(logging.WARNING)

# הגדרות עמוד
st.set_page_config(
    page_title="CashFlowIQ Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ייבוא מודולים פנימיים
from ui.styles import apply_all_styles
from ui.components import display_header
from data.data_loader import load_data
from pages.cash_flow import render_cash_flow_page
from pages.contract_analysis import render_contract_analysis_page
from pages.query_chat import render_query_chat_page

# החלת סגנונות
apply_all_styles(st)

# הצגת כותרת ולוגו
display_header()

# טעינת נתונים
data = load_data()

# יצירת טאבים ראשיים
with st.container():
    main_tab, contract_tab, query_tab = st.tabs([
        "💰 Cash Flow",
        "📄 Contract Analysis", 
        "🔍 Natural Language Queries"
    ])
    
    with main_tab:
        render_cash_flow_page(data)
    
    with contract_tab:
        render_contract_analysis_page()
    
    with query_tab:
        render_query_chat_page(data)

# כותרת תחתונה
st.caption("© 2025 CashFlowIQ | Responsive Web & Mobile Dashboard | Beta Version") 