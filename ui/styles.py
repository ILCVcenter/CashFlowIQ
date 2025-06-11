"""
ui/styles.py - כל הסגנונות והעיצובים של האפליקציה
"""

def get_main_css():
    """CSS עיקרי של האפליקציה"""
    return """
    <style>
        .main-header {color:#1E88E5; font-size:2.5rem; font-weight:bold;}
        .sub-header {color:#0D47A1; font-size:1.5rem; font-weight:600;}
        .info-text {color:#37474F; font-size:1rem;}
        .warning-box {background-color:#FFF3E0; padding:10px; border-radius:5px; border-left:5px solid #FF9800;}
        .success-box {background-color:#E8F5E9; padding:10px; border-radius:5px; border-left:5px solid #4CAF50;}
    </style>
    """

def get_dark_theme_css():
    """CSS לנושא כהה"""
    return '''
    <link href="https://fonts.googleapis.com/css?family=Inter:wght@400;700&display=swap" rel="stylesheet">
    <style>
    body, .stApp {
        background-color: #181943 !important;
        color: #F5F6FA !important;
        font-family: 'Inter', sans-serif;
    }
    .card {
        background: #23255d;
        border-radius: 18px;
        padding: 24px 24px 18px 24px;
        margin-bottom: 18px;
        box-shadow: 0 2px 8px #0002;
    }
    .kpi {
        font-size: 3rem;
        font-weight: bold;
        color: #00CFFF;
        margin-bottom: 0;
    }
    .kpi-label {
        color: #F5F6FA;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    .progress-bar {
        background: #23255d;
        border-radius: 8px;
        height: 16px;
        margin-top: 8px;
        width: 100%;
        position: relative;
    }
    .progress-bar-inner {
        background: #00CFFF;
        height: 100%;
        border-radius: 8px;
        position: absolute;
        left: 0; top: 0;
    }
    h1, h2, h3, h4 {
        color: #F5F6FA;
        font-weight: bold;
    }
    </style>
    '''

def get_tabs_css():
    """CSS לעיצוב טאבים"""
    return '''
    <style>
    .stTabs [data-baseweb="tab-list"] {
        background: #23255d !important;
        border-radius: 12px 12px 0 0;
        padding: 0 8px;
        border-bottom: 2px solid #23255d;
    }
    .stTabs [data-baseweb="tab"] {
        color: #AAB2D5 !important;
        font-weight: 600;
        font-size: 1.1rem;
        background: transparent !important;
        border: none !important;
        margin-right: 8px;
        margin-left: 8px;
        padding: 10px 18px 8px 18px;
        border-radius: 12px 12px 0 0;
        transition: background 0.2s;
    }
    .stTabs [aria-selected="true"] {
        color: #00CFFF !important;
        border-bottom: 3px solid #00CFFF !important;
        background: #23255d !important;
    }
    .stTabs [aria-selected="false"]:hover {
        background: #23255d55 !important;
        color: #F5F6FA !important;
    }
    /* CSS לטאבים גדולים */
    .stTabs [data-baseweb="tab"] {
        font-size: 2.2rem !important;
        font-weight: bold !important;
        padding: 0.7em 2.2em !important;
        color: #00CFFF !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        border-bottom: 4px solid #00CFFF !important;
        background: #23255d !important;
        color: #fff !important;
    }
    </style>
    '''

def get_tables_css():
    """CSS לעיצוב טבלאות"""
    return '''<style>
    thead tr th {background: #23255d !important; color: #fff !important; font-weight: bold !important;}
    tbody tr td {background: #23255d !important; color: #fff !important;}
    tbody tr:nth-child(even) td {background: #202244 !important;}
    tbody tr:hover td {background: #2e315e !important;}
    .stDataFrame th, .stDataFrame td {color: #fff !important; font-size: 1rem;}
    .stDataFrame th {font-weight: bold !important;}
    .stAlert > div {background-color: #23255d !important; color: #fff !important; border: none !important;}
    .stAlert p {color: #fff !important;}
    div[data-testid="stText"] p {color: #fff !important;}
    div[data-testid="stMarkdown"] p {color: #fff !important;}
    .stSubheader {color: #fff !important;}
    .stSelectbox label, div[data-baseweb="select"] {color: #fff !important;}
    .stMultiSelect label, div[data-baseweb="select"] {color: #fff !important;}
    .stDateInput label, div[data-baseweb="input"] {color: #fff !important;}
    </style>'''

def get_button_css():
    """CSS לעיצוב כפתורים"""
    return """
    <style>
    .stDownloadButton button {
        background-color: #00CFFF !important;
        color: #181943 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        border: none !important;
    }
    .stDownloadButton button:hover {
        background-color: #009FCC !important;
        color: white !important;
    }
    div[data-testid="stButton"] button {
        background-color: #23255d !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #181943 !important;
        border: 1px solid #00CFFF !important;
    }
    </style>
    """

def apply_all_styles(st):
    """החלת כל הסגנונות על האפליקציה"""
    st.markdown(get_main_css(), unsafe_allow_html=True)
    st.markdown(get_dark_theme_css(), unsafe_allow_html=True)
    st.markdown(get_tabs_css(), unsafe_allow_html=True)
    st.markdown(get_tables_css(), unsafe_allow_html=True) 