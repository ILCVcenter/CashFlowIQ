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
    /* Hide any tab underlines or borders - multiple selectors for safety */
    .stTabs > div > div,
    .stTabs > div > div > div,
    .stTabs [role="tablist"],
    .stTabs div[data-baseweb="tab-border"] {
        border-bottom: none !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Main tabs container */
    .stTabs [data-baseweb="tab-list"] {
        background: #23255d !important;
        border-radius: 12px 12px 0 0;
        padding: 0 8px;
        border-bottom: none !important;
        border: none !important;
        gap: 4px;
        margin-bottom: 0px !important;
    }
    
    /* Remove any tab panel borders */
    .stTabs [data-baseweb="tab-panel"] {
        border: none !important;
        border-top: none !important;
        margin-top: 0px !important;
        padding-top: 20px;
    }
    
    /* Force remove any possible divider lines */
    .stTabs::after,
    .stTabs::before,
    .stTabs > div::after,
    .stTabs > div::before {
        display: none !important;
        content: none !important;
        border: none !important;
        background: none !important;
    }
    
    /* Remove any hr elements that might appear */
    .stTabs hr {
        display: none !important;
    }
    
    /* Individual tabs */
    .stTabs [data-baseweb="tab"] {
        color: #AAB2D5 !important;
        font-weight: 600;
        font-size: 0.9rem !important;
        background: #181943 !important;
        border: 1px solid #2a2d5a !important;
        margin-right: 4px;
        margin-left: 4px;
        padding: 8px 16px !important;
        border-radius: 8px 8px 0 0;
        transition: all 0.2s ease;
        min-width: 120px;
        text-align: center;
    }
    
    /* Active tab */
    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        background: #00CFFF !important;
        border: 1px solid #00CFFF !important;
        border-bottom: 3px solid #00CFFF !important;
        font-weight: bold !important;
    }
    
    /* Hover state */
    .stTabs [aria-selected="false"]:hover {
        background: #2a2d5a !important;
        color: #F5F6FA !important;
        border: 1px solid #00CFFF !important;
        cursor: pointer;
    }
    
    /* Tab panel content */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 20px;
    }
    
    /* Nested tabs (for charts) */
    div[data-testid="stHorizontalBlock"] .stTabs [data-baseweb="tab"] {
        font-size: 0.75rem !important;
        padding: 4px 8px !important;
        min-width: 120px !important;
        max-width: 120px !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }
    
    /* Horizontal scroll for nested tabs */
    div[data-testid="stHorizontalBlock"] .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto !important;
        overflow-y: hidden !important;
        white-space: nowrap !important;
        scroll-behavior: smooth !important;
        padding-bottom: 5px !important;
    }
    
    /* Scrollbar styling for nested tabs */
    div[data-testid="stHorizontalBlock"] .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        height: 4px !important;
    }
    
    div[data-testid="stHorizontalBlock"] .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-track {
        background: #181943 !important;
    }
    
    div[data-testid="stHorizontalBlock"] .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
        background: #00CFFF !important;
        border-radius: 2px !important;
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

def get_scroll_fix_js():
    """JavaScript to prevent auto-scroll on filter changes"""
    return '''
    <script>
    let lastScrollY = 0;
    let isFilterUpdate = false;
    
    // Save scroll position before any changes
    function saveScrollPosition() {
        lastScrollY = window.scrollY;
    }
    
    // Restore scroll position
    function restoreScrollPosition() {
        if (isFilterUpdate && lastScrollY > 0) {
            window.scrollTo({top: lastScrollY, behavior: 'auto'});
            isFilterUpdate = false;
        }
    }
    
    // Monitor for filter input changes
    function monitorFilters() {
        const filters = document.querySelectorAll('input, select, [data-baseweb="select"]');
        filters.forEach(filter => {
            filter.addEventListener('change', () => {
                saveScrollPosition();
                isFilterUpdate = true;
                setTimeout(restoreScrollPosition, 200);
            });
            filter.addEventListener('input', () => {
                saveScrollPosition();
                isFilterUpdate = true;
                setTimeout(restoreScrollPosition, 200);
            });
        });
    }
    
    // Initial setup and monitor for new elements
    const setupObserver = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                setTimeout(monitorFilters, 100);
            }
        });
    });
    
    // Start observing when page loads
    if (document.querySelector('.stApp')) {
        monitorFilters();
        setupObserver.observe(document.querySelector('.stApp'), {
            childList: true,
            subtree: true
        });
    }
    
    // Additional backup - prevent scroll on tab content changes
    window.addEventListener('hashchange', function() {
        if (lastScrollY > 0) {
            setTimeout(() => window.scrollTo({top: lastScrollY, behavior: 'auto'}), 50);
        }
    });
    </script>
    '''

def apply_all_styles(st):
    """Apply all styles to the application"""
    st.markdown(get_main_css(), unsafe_allow_html=True)
    st.markdown(get_dark_theme_css(), unsafe_allow_html=True)
    st.markdown(get_tabs_css(), unsafe_allow_html=True)
    st.markdown(get_tables_css(), unsafe_allow_html=True)
    st.markdown(get_scroll_fix_js(), unsafe_allow_html=True) 