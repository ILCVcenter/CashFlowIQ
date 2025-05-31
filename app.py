import sys
import streamlit as st
import pandas as pd
import warnings
import services
import os
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import numpy as np

st.set_page_config(
    page_title="CashFlowIQ Dashboard",
    layout="wide",  # מאפשר רספונסיביות טובה גם למובייל
    initial_sidebar_state="expanded"
)

# CSS styling
st.markdown("""
<style>
    .main-header {color:#1E88E5; font-size:2.5rem; font-weight:bold;}
    .sub-header {color:#0D47A1; font-size:1.5rem; font-weight:600;}
    .info-text {color:#37474F; font-size:1rem;}
    .warning-box {background-color:#FFF3E0; padding:10px; border-radius:5px; border-left:5px solid #FF9800;}
    .success-box {background-color:#E8F5E9; padding:10px; border-radius:5px; border-left:5px solid #4CAF50;}
</style>
""", unsafe_allow_html=True)

# טעינת הלוגו
logo = Image.open("logo.png")
# הצג את הלוגו והכותרת בצורה צמודה יותר
col1, col2 = st.columns([0.4, 5])
with col1:
    st.image(logo, width=75)
with col2:
    st.markdown('<span style="font-size:2.2rem; font-weight:bold; color:#fff; letter-spacing:1px; margin-top:-20px; padding-top:0; display:block;">CashFlowIQ</span>', unsafe_allow_html=True)

# --- DARK DASHBOARD STYLE ---
st.markdown('''
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
''', unsafe_allow_html=True)

# --- עיצוב טאבים כהה ---
st.markdown('''
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
</style>
''', unsafe_allow_html=True)

# --- עיצוב טבלאות כהות ---
st.markdown('''<style>
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
</style>''', unsafe_allow_html=True)

# --- CSS לטאבים גדולים ---
st.markdown("""
<style>
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
""", unsafe_allow_html=True)

# טעינת נתונים
@st.cache_data(ttl=60)  # מטמון לשעה אחת בלבד לאפשר רענון נתונים
def load_data():
    df = pd.read_csv("data/sample_data.csv")
    return df

data = load_data()

# הוספת מעטפת ראשית למניעת מסגרת מיותרת
with st.container():
    # Navigation tabs - right after the title
    main_tab, contract_tab, query_tab = st.tabs([
        "💰 Cash Flow",
        "📄 Contract Analysis",
        "🔍 Natural Language Queries"
    ])

    with main_tab:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        # Currency Conversion at the top of Cash Flow tab
        st.subheader("Currency Conversion")
        col1, col2 = st.columns(2)
        with col1:
            base_currency = st.selectbox("Base Currency", ["USD", "EUR", "ILS", "GBP"], index=0, key="base_currency")
        with col2:
            target_currency = st.selectbox("Target Currency", ["USD", "EUR", "ILS", "GBP"], index=1, key="target_currency")
        
        # Get exchange rate with better error handling
        exchange_rate = services.get_exchange_rate(base_currency, target_currency)
        if exchange_rate:
            st.info(f"Current Exchange Rate: 1 {base_currency} = {exchange_rate:.4f} {target_currency}")
        else:
            st.error("Could not fetch exchange rate. Please try again later.")
        
        # Apply conversion to data
        data_converted = data.copy()
        if exchange_rate and base_currency != target_currency:
            data_converted['amount'] = data_converted['amount'] * exchange_rate
            currency_label = target_currency
        else:
            currency_label = base_currency
        
        # Main content below the currency conversion
        st.markdown("---")
        
        # אפשרויות סינון
        st.subheader("Cash Flow Statement")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            # הגבלת טווח התאריכים: מ-01.01.2024 ועד היום
            min_date = pd.to_datetime('2024-01-01').date()
            max_date = pd.to_datetime('today').date()
            
            # התאריך הנבחר בברירת מחדל יהיה מתחילת 2024 ועד היום
            default_start = min_date
            default_end = max_date
            
            # ודא שאנחנו לא חורגים מטווח הנתונים הקיימים
            data_min_date = pd.to_datetime(data_converted['date']).min().date()
            if data_min_date > min_date:
                min_date = data_min_date
                default_start = data_min_date
                
            date_range = st.date_input("Date Range", [default_start, default_end], min_value=min_date, max_value=max_date)
        
        with col2:
            category_options = data_converted['category'].unique()
            category_filter = st.multiselect("Category Filter", category_options, default=[])
        
        with col3:
            type_options = data_converted['type'].unique()
            type_filter = st.multiselect("Type Filter", type_options, default=[])
        
        # הכנת הנתונים לתצוגת תזרים מזומנים
        # המרת תאריכים לפורמט datetime עבור סינון
        data_for_cashflow = data_converted.copy()
        data_for_cashflow['date'] = pd.to_datetime(data_for_cashflow['date'])
        
        # סינון על פי הבחירות
        if len(date_range) == 2:
            start_date, end_date = date_range
            mask = (data_for_cashflow['date'] >= pd.Timestamp(start_date)) & (data_for_cashflow['date'] <= pd.Timestamp(end_date))
            data_for_cashflow = data_for_cashflow[mask]
        
        if category_filter:
            data_for_cashflow = data_for_cashflow[data_for_cashflow['category'].isin(category_filter)]
        
        if type_filter:
            data_for_cashflow = data_for_cashflow[data_for_cashflow['type'].isin(type_filter)]
        
        # בדיקה אם יש נתונים אחרי הסינון
        if data_for_cashflow.empty:
            st.warning("אין נתונים בטווח התאריכים שנבחר.")
            st.stop()
        
        # מיון לפי תאריך
        data_for_cashflow = data_for_cashflow.sort_values('date')
        
        # יצירת נתוני תזרים מזומנים לפי יום
        daily_cashflow = data_for_cashflow.groupby(data_for_cashflow['date'].dt.date).agg({
            'amount': 'sum',
            'description': lambda x: ", ".join(set(x)) if len(set(x)) <= 3 else ", ".join(list(set(x))[:3]) + "..."
        }).reset_index()
        daily_cashflow['date_str'] = daily_cashflow['date'].apply(lambda x: x.strftime('%d/%m/%Y'))
        
        # חישוב יתרות פתיחה וסגירה
        initial_balance = 100000  # יתרת פתיחה התחלתית
        daily_cashflow['cash_inflows'] = daily_cashflow['amount'].apply(lambda x: max(0, x))
        daily_cashflow['cash_outflows'] = daily_cashflow['amount'].apply(lambda x: min(0, x)).abs()
        
        # חישוב יתרות מצטברות
        running_balance = initial_balance
        opening_balances = []
        closing_balances = []
        
        for i, row in daily_cashflow.iterrows():
            # יתרת פתיחה
            opening_balances.append(running_balance)
            # חישוב יתרת סגירה
            closing_balance = running_balance + row['amount']
            closing_balances.append(closing_balance)
            # עדכון היתרה לשורה הבאה
            running_balance = closing_balance
        
        daily_cashflow['opening_balance'] = opening_balances
        daily_cashflow['closing_balance'] = closing_balances
        
        # פורמט לתצוגה
        cashflow_display = pd.DataFrame({
            'Date': daily_cashflow['date_str'],
            'Opening Balance': daily_cashflow['opening_balance'].map('${:,.2f}'.format),
            'Cash Inflows': daily_cashflow['cash_inflows'].map('${:,.2f}'.format),
            'Cash Outflows': daily_cashflow['cash_outflows'].map('${:,.2f}'.format),
            'Closing Balance': daily_cashflow['closing_balance'].map('${:,.2f}'.format),
            'Notes': daily_cashflow['description']
        })
        
        # הצגת טבלת תזרים המזומנים והגרפים זה לצד זה
        table_col, graph_col = st.columns([2, 1])
        with table_col:
            st.dataframe(cashflow_display, use_container_width=True, height=400)
        with graph_col:
            st.markdown('<div style="margin-bottom:16px;"></div>', unsafe_allow_html=True)
            tab1, tab2, tab3 = st.tabs(["Monthly Cash Flow", "Balance Over Time", "Income vs Expenses"])
            with tab1:
                data_for_cashflow['month'] = data_for_cashflow['date'].dt.strftime('%Y-%m')
                monthly_inflows = data_for_cashflow[data_for_cashflow['amount'] > 0].groupby('month')['amount'].sum()
                monthly_outflows = data_for_cashflow[data_for_cashflow['amount'] < 0].groupby('month')['amount'].sum().abs()
                monthly_cashflow = pd.DataFrame({'Inflows': monthly_inflows, 'Outflows': monthly_outflows}).fillna(0)
                
                # תמיד להשתמש ב-try-except בגרפים למניעת שגיאות
                try:
                    fig, ax = plt.subplots(figsize=(2.5, 1.8), facecolor='#181943')
                    ax.set_facecolor('#181943')
                    monthly_cashflow.plot(kind='bar', ax=ax, rot=30, color=['#00CFFF', '#9966FF'])  # שינוי זווית סיבוב לקריאות
                    
                    # טיפול בתאריכים לקריאות טובה יותר
                    if len(monthly_cashflow.index) > 10:
                        # אם יש יותר מדי תאריכים, הצג רק חלק מהם
                        step = max(1, len(monthly_cashflow.index) // 10)
                        xlabels = ax.get_xticklabels()
                        for i, label in enumerate(xlabels):
                            if i % step != 0:
                                label.set_visible(False)
                    
                    ax.set_xlabel('Month', fontsize=7, color='white')
                    ax.set_ylabel('Amount', fontsize=7, color='white')
                    ax.set_title('Monthly Cash Flow', fontsize=8, color='white', pad=15)  # תוספת pad לכותרת
                    ax.tick_params(axis='x', labelrotation=45, labelsize=6, colors='white')  # שינוי זווית סיבוב לקריאות
                    ax.tick_params(axis='y', labelsize=6, colors='white')
                    ax.spines['bottom'].set_color('white')
                    ax.spines['top'].set_color('white')
                    ax.spines['left'].set_color('white')
                    ax.spines['right'].set_color('white')
                    ax.grid(axis='y', linestyle='--', alpha=0.2, color='white')
                    ax.legend(fontsize=6, facecolor='#23255d', edgecolor='#23255d', labelcolor='white')
                    
                    plt.tight_layout()  # שיפור הפריסה האוטומטית
                    st.pyplot(fig)
                except Exception as e:
                    st.warning(f"לא ניתן להציג את הגרף: {str(e)}")
            with tab2:
                balance_over_time = pd.DataFrame({'Date': daily_cashflow['date'], 'Balance': daily_cashflow['closing_balance']}).set_index('Date')
                fig, ax = plt.subplots(figsize=(2.5, 1.8), facecolor='#181943')
                ax.set_facecolor('#181943')
                balance_over_time.plot(ax=ax, color='#00CFFF', linewidth=2)
                ax.set_xlabel('Date', fontsize=7, color='white')
                ax.set_ylabel('Balance', fontsize=7, color='white')
                ax.set_title('Balance Over Time', fontsize=8, color='white')
                ax.tick_params(axis='x', labelsize=6, colors='white')
                ax.tick_params(axis='y', labelsize=6, colors='white')
                ax.spines['bottom'].set_color('white')
                ax.spines['top'].set_color('white')
                ax.spines['left'].set_color('white')
                ax.spines['right'].set_color('white')
                ax.grid(axis='y', linestyle='--', alpha=0.2, color='white')
                st.pyplot(fig)
            with tab3:
                income_by_type = data_for_cashflow[data_for_cashflow['amount'] > 0].groupby('type')['amount'].sum().reset_index()
                expense_by_type = data_for_cashflow[data_for_cashflow['amount'] < 0].groupby('type')['amount'].sum().abs().reset_index()
                fig1, ax1 = plt.subplots(figsize=(2.5, 1.8), facecolor='#181943')
                ax1.set_facecolor('#181943')
                income_by_type.plot(kind='bar', x='type', y='amount', ax=ax1, legend=False, rot=0, color='#00CFFF')
                ax1.set_xlabel('Type', fontsize=7, color='white')
                ax1.set_ylabel('Amount', fontsize=7, color='white')
                ax1.set_title('Income Sources', fontsize=8, color='white')
                ax1.tick_params(axis='x', labelrotation=30, labelsize=6, colors='white')
                ax1.tick_params(axis='y', labelsize=6, colors='white')
                ax1.spines['bottom'].set_color('white')
                ax1.spines['top'].set_color('white')
                ax1.spines['left'].set_color('white')
                ax1.spines['right'].set_color('white')
                ax1.grid(axis='y', linestyle='--', alpha=0.2, color='white')
                st.pyplot(fig1)
                fig2, ax2 = plt.subplots(figsize=(2.5, 1.8), facecolor='#181943')
                ax2.set_facecolor('#181943')
                expense_by_type.plot(kind='bar', x='type', y='amount', ax=ax2, legend=False, rot=0, color='#9966FF')
                ax2.set_xlabel('Type', fontsize=7, color='white')
                ax2.set_ylabel('Amount', fontsize=7, color='white')
                ax2.set_title('Expense Categories', fontsize=8, color='white')
                ax2.tick_params(axis='x', labelrotation=30, labelsize=6, colors='white')
                ax2.tick_params(axis='y', labelsize=6, colors='white')
                ax2.spines['bottom'].set_color('white')
                ax2.spines['top'].set_color('white')
                ax2.spines['left'].set_color('white')
                ax2.spines['right'].set_color('white')
                ax2.grid(axis='y', linestyle='--', alpha=0.2, color='white')
                st.pyplot(fig2)
        
        # --- Cash Flow Forecast ---
        st.markdown("---")
        st.subheader(f"Cash Flow Forecast ({currency_label})")
        forecast_col1, forecast_col2, forecast_col3 = st.columns(3)
        with forecast_col1:
            # הגבלת טווח התאריכים: מהיום ועד 31.12.2027
            forecast_min_date = pd.to_datetime('today').date()
            forecast_max_date = pd.to_datetime('2027-12-31').date()
            
            # התאריך הנבחר בברירת מחדל יהיה מהיום ועד חצי שנה קדימה
            forecast_default_start = forecast_min_date
            forecast_default_end = min(forecast_max_date, (forecast_min_date + pd.DateOffset(months=6)).date())
            
            forecast_date_range = st.date_input("Forecast Date Range", 
                                                [forecast_default_start, forecast_default_end], 
                                                min_value=forecast_min_date, 
                                                max_value=forecast_max_date,
                                                key="forecast_date_range")
        with forecast_col2:
            forecast_category_options = data_converted['category'].unique()
            forecast_category_filter = st.multiselect("Forecast Category Filter", forecast_category_options, default=[])
        with forecast_col3:
            forecast_type_options = data_converted['type'].unique()
            forecast_type_filter = st.multiselect("Forecast Type Filter", forecast_type_options, default=[])
        forecast_data_for_cashflow = data_converted.copy()
        forecast_data_for_cashflow['date'] = pd.to_datetime(forecast_data_for_cashflow['date'])
        if len(forecast_date_range) == 2:
            forecast_start_date, forecast_end_date = forecast_date_range
            mask = (forecast_data_for_cashflow['date'] >= pd.Timestamp(forecast_start_date)) & (forecast_data_for_cashflow['date'] <= pd.Timestamp(forecast_end_date))
            forecast_data_for_cashflow = forecast_data_for_cashflow[mask]
        if forecast_category_filter:
            forecast_data_for_cashflow = forecast_data_for_cashflow[forecast_data_for_cashflow['category'].isin(forecast_category_filter)]
        if forecast_type_filter:
            forecast_data_for_cashflow = forecast_data_for_cashflow[forecast_data_for_cashflow['type'].isin(forecast_type_filter)]
        # חישוב תחזית בזמן אמת
        try:
            forecast_data = forecast_data_for_cashflow[['date', 'amount']].copy()
            
            # וידוא שעמודת התאריך היא מסוג datetime - חשוב כדי שתזוהה נכון
            forecast_data['date'] = pd.to_datetime(forecast_data['date'])
            
            # אם אין נתונים, יצירת תחזית על בסיס כל הנתונים
            if forecast_data.empty:
                st.warning("אין נתוני תזרים בטווח התאריכים שנבחר לתחזית. יוצרת תחזית על בסיס כל הנתונים.")
                forecast_data = data_converted[['date', 'amount']].copy()
                forecast_data['date'] = pd.to_datetime(forecast_data['date'])
            
            forecast_df = services.forecast_cashflow(forecast_data, periods=6)  # ברירת מחדל 6 חודשים
            if not forecast_df.empty:
                last_balance = forecast_data_for_cashflow['amount'].cumsum().iloc[-1] if not forecast_data_for_cashflow.empty else 100000
                forecast_display = pd.DataFrame()
                forecast_display['date'] = forecast_df['date']
                forecast_display['date_str'] = forecast_display['date'].dt.strftime('%Y-%m-%d')
                opening_balances = [last_balance]
                closing_balances = []
                cash_inflows = []
                cash_outflows = []
                for i, value in enumerate(forecast_df['forecast']):
                    if i > 0:
                        opening_balances.append(closing_balances[i-1])
                    inflow = max(0, value)
                    outflow = abs(min(0, value))
                    cash_inflows.append(inflow)
                    cash_outflows.append(outflow)
                    closing_balance = opening_balances[i] + value
                    closing_balances.append(closing_balance)
                forecast_display['opening_balance'] = opening_balances
                forecast_display['cash_inflows'] = cash_inflows
                forecast_display['cash_outflows'] = cash_outflows
                forecast_display['closing_balance'] = closing_balances
                forecast_display['forecast'] = forecast_df['forecast']
                # בדיקה אם יש נתוני תחזית תקינים
                if forecast_display.empty or forecast_display['date'].isnull().all() or forecast_display['forecast'].isnull().all():
                    st.warning("אין נתוני תחזית בטווח התאריכים שנבחר.")
                else:
                    # טבלת תחזית
                    forecast_table = pd.DataFrame({
                        'Date': forecast_display['date_str'],
                        'Opening Balance': forecast_display['opening_balance'].map('${:,.2f}'.format),
                        'Cash Inflows': forecast_display['cash_inflows'].map('${:,.2f}'.format),
                        'Cash Outflows': forecast_display['cash_outflows'].map('${:,.2f}'.format),
                        'Closing Balance': forecast_display['closing_balance'].map('${:,.2f}'.format),
                        'Notes': forecast_display.get('description', ['']*len(forecast_display))
                    })
                    # הצגת טבלת תזרים התחזית והגרפים זה לצד זה
                    st.subheader("Forecast Visualization")
                    forecast_chart_data = pd.DataFrame({
                        'Date': forecast_display['date'],
                        'Forecast': forecast_display['forecast'],
                        'Balance': forecast_display['closing_balance']
                    }).set_index('Date')
                    forecast_table_col, forecast_graph_col = st.columns([2, 1])
                    with forecast_table_col:
                        st.dataframe(forecast_table, use_container_width=True, height=400)
                    with forecast_graph_col:
                        st.markdown('<div style="margin-bottom:16px;"></div>', unsafe_allow_html=True)
                        chart_tab1, chart_tab2, chart_tab3 = st.tabs(["Monthly Cash Flow", "Balance Over Time", "Income vs Expenses"])
                        with chart_tab1:
                            # Monthly Cash Flow Forecast
                            try:
                                # וידוא שיש נתונים
                                if not forecast_chart_data.empty and not forecast_chart_data['Forecast'].isnull().all():
                                    forecast_chart_data_month = forecast_chart_data.resample('ME').sum()
                                    
                                    # בדיקה שיש נתונים אחרי הפעולה
                                    if not forecast_chart_data_month.empty:
                                        fig, ax = plt.subplots(figsize=(3, 2.3), facecolor='#181943')  # גובה גדול יותר
                                        ax.set_facecolor('#181943')
                                        forecast_chart_data_month[['Forecast']].plot(kind='bar', ax=ax, rot=30, color='#00CFFF')
                                        
                                        # עיצוב תבנית תאריך - רק תאריך ללא שעה
                                        date_formatter = plt.matplotlib.dates.DateFormatter('%Y-%m-%d')
                                        if len(forecast_chart_data_month.index) > 0:
                                            xlabels = [item.strftime('%Y-%m-%d') for item in forecast_chart_data_month.index.to_list()]
                                            ax.set_xticklabels(xlabels)
                                        
                                        ax.set_xlabel('Month', fontsize=8, color='white')
                                        ax.set_ylabel('Forecast', fontsize=8, color='white')
                                        ax.set_title('Monthly Cash Flow Forecast', fontsize=10, color='white', pad=15)  # תוספת pad לכותרת
                                        ax.tick_params(axis='x', labelrotation=30, labelsize=6, colors='white')
                                        ax.tick_params(axis='y', labelsize=6, colors='white')
                                        ax.spines['bottom'].set_color('white')
                                        ax.spines['top'].set_color('white')
                                        ax.spines['left'].set_color('white')
                                        ax.spines['right'].set_color('white')
                                        ax.grid(axis='y', linestyle='--', alpha=0.2, color='white')
                                        
                                        # הצגת ערכים מספריים מעל העמודות רק אם יש נתונים
                                        for i, val in enumerate(forecast_chart_data_month['Forecast']):
                                            if not pd.isna(val):  # רק אם הערך אינו NaN
                                                ax.text(i, val + (0.1 * val if val > 0 else -0.1 * abs(val)), 
                                                        f'${int(val)}', ha='center', va='bottom' if val > 0 else 'top', 
                                                        fontsize=6, color='white')
                                        
                                        plt.tight_layout()  # שיפור האוטומטי של הפריסה
                                        st.pyplot(fig)
                                    else:
                                        st.warning("אין נתונים מספיקים להצגת גרף תחזית חודשי.")
                                else:
                                    st.warning("אין נתוני תחזית זמינים להצגת גרף.")
                            except Exception as e:
                                st.warning(f"לא ניתן להציג את גרף התחזית החודשי: {str(e)}")
                        with chart_tab2:
                            try:
                                # וידוא שיש נתונים
                                if not forecast_chart_data.empty and not forecast_chart_data['Balance'].isnull().all():
                                    fig, ax = plt.subplots(figsize=(3, 2.3), facecolor='#181943')
                                    ax.set_facecolor('#181943')
                                    forecast_chart_data[['Balance']].plot(ax=ax, color='#00CFFF', linewidth=2)
                                    
                                    # עיצוב תבנית תאריך - רק תאריך ללא שעה
                                    date_formatter = plt.matplotlib.dates.DateFormatter('%Y-%m-%d')
                                    ax.xaxis.set_major_formatter(date_formatter)
                                    
                                    ax.set_xlabel('Date', fontsize=8, color='white')
                                    ax.set_ylabel('Balance', fontsize=8, color='white')
                                    ax.set_title('Projected Balance Over Time', fontsize=10, color='white', pad=15)  # תוספת pad לכותרת
                                    ax.tick_params(axis='x', labelsize=6, colors='white')
                                    ax.tick_params(axis='y', labelsize=6, colors='white')
                                    ax.spines['bottom'].set_color('white')
                                    ax.spines['top'].set_color('white')
                                    ax.spines['left'].set_color('white')
                                    ax.spines['right'].set_color('white')
                                    ax.grid(axis='y', linestyle='--', alpha=0.2, color='white')
                                    
                                    plt.tight_layout()  # שיפור האוטומטי של הפריסה
                                    st.pyplot(fig)
                                else:
                                    st.warning("אין נתוני מאזן זמינים להצגת גרף.")
                            except Exception as e:
                                st.warning(f"לא ניתן להציג את גרף המאזן: {str(e)}")
                        with chart_tab3:
                            try:
                                # וידוא שיש נתונים
                                if not forecast_display.empty and not forecast_display['forecast'].isnull().all():
                                    # הכנסות/הוצאות לפי סוג
                                    income_types = forecast_display[forecast_display['forecast'] > 0]['forecast']
                                    expense_types = forecast_display[forecast_display['forecast'] < 0]['forecast'].abs()
                                    
                                    if not income_types.empty or not expense_types.empty:
                                        fig, ax = plt.subplots(figsize=(3, 2.3), facecolor='#181943')
                                        ax.set_facecolor('#181943')
                                        
                                        # וידוא שיש נתונים לפני הציור
                                        if not income_types.empty:
                                            income_types.plot(kind='bar', color='#00CFFF', ax=ax, position=0, width=0.4, label='Income')
                                        if not expense_types.empty:
                                            expense_types.plot(kind='bar', color='#9966FF', ax=ax, position=1, width=0.4, label='Expense')
                                        
                                        ax.set_xlabel('Period', fontsize=8, color='white')
                                        ax.set_ylabel('Amount', fontsize=8, color='white')
                                        ax.set_title('Income vs Expenses (Forecast)', fontsize=10, color='white', pad=15)  # תוספת pad לכותרת
                                        
                                        # עיצוב תאריכים
                                        if len(forecast_display['date']) > 0:
                                            xlabels = [item.strftime('%Y-%m-%d') for item in forecast_display['date']]
                                            if len(xlabels) == len(ax.get_xticklabels()):
                                                ax.set_xticklabels(xlabels, rotation=30)
                                        
                                        ax.tick_params(axis='x', labelsize=6, colors='white')
                                        ax.tick_params(axis='y', labelsize=6, colors='white')
                                        ax.spines['bottom'].set_color('white')
                                        ax.spines['top'].set_color('white')
                                        ax.spines['left'].set_color('white')
                                        ax.spines['right'].set_color('white')
                                        ax.grid(axis='y', linestyle='--', alpha=0.2, color='white')
                                        ax.legend(fontsize=6, facecolor='#23255d', edgecolor='#23255d', labelcolor='white')
                                        
                                        plt.tight_layout()  # שיפור האוטומטי של הפריסה
                                        st.pyplot(fig)
                                    else:
                                        st.warning("אין נתוני הכנסות/הוצאות זמינים להצגת גרף.")
                                else:
                                    st.warning("אין נתוני תחזית זמינים להצגת גרף.")
                            except Exception as e:
                                st.warning(f"לא ניתן להציג את גרף ההכנסות והוצאות: {str(e)}")
            else:
                st.info("No forecast data available.")
        except Exception as e:
            st.error(f"Forecast error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
        
        # --- Export Data ---
        def convert_df_to_csv(df):
            return df.to_csv(index=False).encode('utf-8')
        csv = convert_df_to_csv(data_converted)
        
        # עיצוב כפתור ההורדה
        st.markdown("""
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
        </style>
        """, unsafe_allow_html=True)
        
        # כפתור הורדה
        st.download_button(
            label="Download CSV Data",
            data=csv,
            file_name='cashflow_data.csv',
            mime='text/csv',
        )

        # --- העלאת קובץ CSV חדש והוספת נתונים ---
        uploaded_file = st.file_uploader("העלה קובץ CSV להוספת נתונים", type=["csv"])
        if uploaded_file is not None:
            try:
                new_data = pd.read_csv(uploaded_file)
                
                # המרת עמודת התאריך לפורמט אחיד
                if 'date' in new_data.columns:
                    # ניסיון להמיר תאריכים בכל פורמט אפשרי
                    try:
                        new_data['date'] = pd.to_datetime(new_data['date'])
                        # המרה לפורמט YYYY-MM-DD אחיד
                        new_data['date'] = new_data['date'].dt.strftime('%Y-%m-%d')
                        st.success("התאריכים הומרו בהצלחה לפורמט YYYY-MM-DD")
                    except Exception as e:
                        st.warning(f"שגיאה בהמרת התאריכים: {e}. מנסה פורמט אחר...")
                        try:
                            # ניסיון להמיר עם פורמט ספציפי
                            new_data['date'] = pd.to_datetime(new_data['date'], format='%d/%m/%Y')
                            new_data['date'] = new_data['date'].dt.strftime('%Y-%m-%d')
                            st.success("התאריכים הומרו בהצלחה לפורמט YYYY-MM-DD")
                        except:
                            st.error("לא ניתן להמיר את התאריכים. אנא בדוק שהתאריכים בפורמט תקין.")
                
                # מיזוג הנתונים
                data_converted = pd.concat([data_converted, new_data], ignore_index=True)
                
                # הסרת כפילויות (לפי כל העמודות)
                data_converted = data_converted.drop_duplicates()
                
                # הצגת הודעת הצלחה
                st.success(f"הנתונים נוספו בהצלחה! נוספו {len(new_data)} שורות.")
                
                # אפשרות להציג חלק מהנתונים החדשים
                with st.expander("הצג את הנתונים החדשים שנוספו"):
                    st.dataframe(new_data.head(10))
                    
                # אפשרות להוריד את הקובץ המשולב
                csv_merged = data_converted.to_csv(index=False).encode('utf-8')
                download_col1, download_col2 = st.columns(2)
                with download_col1:
                    st.download_button(
                        label="הורד את כל הנתונים (CSV)",
                        data=csv_merged,
                        file_name='merged_cashflow_data.csv',
                        mime='text/csv',
                    )
                with download_col2:
                    # אפשרות לשמור את הנתונים לקובץ המקור
                    save_to_source = st.button("שמור נתונים לקובץ המקור ורענן")
                    if save_to_source:
                        try:
                            data_converted.to_csv("data/sample_data.csv", index=False)
                            st.cache_data.clear()  # מחיקת המטמון כדי לחייב טעינה מחדש
                            st.success("הנתונים נשמרו בהצלחה לקובץ המקור! לחץ על Rerun כדי לראות את השינויים.")
                            st.rerun()  # רענון האפליקציה
                        except Exception as e:
                            st.error(f"שגיאה בשמירת הנתונים: {e}")
            except Exception as e:
                st.error(f"שגיאה בקריאת הקובץ: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    with contract_tab:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Contract Analysis (PDF)")
        model = st.selectbox("Select GPT Model", ["gpt-3.5-turbo", "gpt-4"], index=1)
        contract_text = ""
        contract_analysis = None
        contract_analysis_error = None
        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []
        ai_answer = None
        try:
            uploaded_file = st.file_uploader("Upload Contract PDF", type=["pdf"], accept_multiple_files=False)
            if uploaded_file is not None:
                with st.spinner("Extracting text from PDF..."):
                    try:
                        text = services.extract_text_from_pdf(uploaded_file)
                        contract_text = text
                        if text.strip():
                            st.text_area("Contract Text", text, height=200)
                            # ניתוח אוטומטי של החוזה
                            with st.spinner("Analyzing contract with GPT..."):
                                try:
                                    result = services.analyze_contract(text, None, model)
                                    import json
                                    try:
                                        contract_analysis = json.loads(result)
                                    except Exception:
                                        contract_analysis_error = result
                                except Exception as e:
                                    contract_analysis_error = f"Error analyzing contract: {str(e)}"
                            if contract_analysis:
                                st.success("Contract Analysis Result:")
                                import pandas as pd
                                def render_list_of_dicts_table(lst):
                                    if not lst:
                                        st.info("No data available.")
                                        return
                                    df = pd.DataFrame(lst)
                                    st.table(df)
                                def render_vertical_table(data):
                                    rows = []
                                    for k, v in data.items():
                                        if isinstance(v, (list, tuple)):
                                            v = ', '.join(str(i) for i in v)
                                        elif isinstance(v, dict):
                                            v = ', '.join([f"{ik}: {iv}" for ik, iv in v.items()])
                                        rows.append({"Field": k, "Value": v})
                                    df = pd.DataFrame(rows)
                                    st.table(df)
                                for key, value in contract_analysis.items():
                                    st.markdown(f"**{key}:**")
                                    # הצגת רשימה של אובייקטים כטבלה
                                    if isinstance(value, list) and value and isinstance(value[0], dict):
                                        render_list_of_dicts_table(value)
                                    elif isinstance(value, dict):
                                        render_vertical_table(value)
                                    elif isinstance(value, list):
                                        st.markdown("<ul>" + ''.join([f"<li>{v}</li>" for v in value]) + "</ul>", unsafe_allow_html=True)
                                    else:
                                        st.info(value)
                                # הצגת הערות/אזהרות בצורה טבלאית אם צריך
                                def render_warning_table(val, title):
                                    if isinstance(val, list) and val and isinstance(val[0], dict):
                                        st.warning(f"{title}:")
                                        render_list_of_dicts_table(val)
                                    elif isinstance(val, list):
                                        st.warning(f"{title}:<ul>" + ''.join([f"<li>{v}</li>" for v in val]) + "</ul>", unsafe_allow_html=True)
                                    elif val:
                                        st.warning(f"{title}: {val}")
                                if 'Penalties' in contract_analysis and contract_analysis['Penalties']:
                                    render_warning_table(contract_analysis['Penalties'], "Attention")
                                if 'Risks' in contract_analysis and contract_analysis['Risks']:
                                    render_warning_table(contract_analysis['Risks'], "Risks")
                            elif contract_analysis_error:
                                st.error(contract_analysis_error)
                            st.markdown("---")
                            st.subheader(":speech_balloon: Ask the AI about the contract")
                            for msg in st.session_state['chat_history']:
                                if msg['role'] == 'user':
                                    st.markdown(f"<div style='text-align:left; background:#181943; padding:8px; border-radius:8px; margin-bottom:4px; color:black;'><b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
                                else:
                                    content = msg['content']
                                    # תמיד מיושר לשמאל (LTR)
                                    if content.strip().startswith('1.') or '\n1.' in content:
                                        items = [line.strip() for line in content.split('\n') if line.strip() and (line.strip()[0].isdigit() and line.strip()[1] in ['.',')'])]
                                        if items:
                                            st.markdown("<div style='text-align:left; background:#23255d; padding:8px; border-radius:8px; margin-bottom:8px; color:black;'><b>AI:</b><ul style='text-align:left; color:black;'>" + ''.join([f"<li>{v}</li>" for v in items]) + "</ul></div>", unsafe_allow_html=True)
                                        else:
                                            st.markdown(f"<div style='text-align:left; background:#23255d; padding:8px; border-radius:8px; margin-bottom:8px; color:black;'><b>AI:</b> {content}</div>", unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"<div style='text-align:left; background:#23255d; padding:8px; border-radius:8px; margin-bottom:8px; color:black;'><b>AI:</b> {content}</div>", unsafe_allow_html=True)
                            
                            # סגנון כפתורים
                            st.markdown("""
                            <style>
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
                            """, unsafe_allow_html=True)
                            
                            user_question = st.text_input("Type your question about the contract", key="contract_chat_input")
                            ask_clicked = st.button("Ask AI")
                            clear_clicked = st.button("Clear Chat")
                            if ask_clicked and user_question.strip():
                                with st.spinner("AI is analyzing your question..."):
                                    ai_answer = services.ask_contract_question(contract_text, user_question, None, model)
                                    st.session_state['chat_history'].append({'role': 'user', 'content': user_question})
                                    st.session_state['chat_history'].append({'role': 'ai', 'content': ai_answer})
                                st.rerun()
                            if clear_clicked:
                                st.session_state['chat_history'] = []
                                st.rerun()
                        else:
                            st.warning("Could not extract text from the PDF. The file might be scanned or password-protected.")
                    except Exception as e:
                        st.error(f"Error processing PDF: {str(e)}")
                        st.info("Try uploading a different PDF file. Make sure it's a valid, unencrypted PDF document.")
            else:
                st.info("Upload a PDF contract to begin analysis.")
        except Exception as e:
            st.error(f"Error in file upload: {str(e)}")
            st.info("The file might be too large or have a problematic filename. Try a smaller file with a simple English filename.")
        st.markdown('</div>', unsafe_allow_html=True)

    with query_tab:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Natural Language Queries")
        st.markdown("Ask questions about the data in natural language, and the system will translate them to SQL queries and display the results")
        import utils
        nl_query = st.text_input("Enter your question in natural language", placeholder="For example: How much income was there in February?")
        run_query = st.button("Run Query")
        if run_query and nl_query:
            with st.spinner("Processing query..."):
                try:
                    # שמירה על מבנה נתונים אחיד
                    table_schema = ", ".join(data.columns.tolist())
                    sample_data = data.head(3).to_string(index=False)
                    
                    # קריאה מוגנת לפונקציית תרגום שאילתה
                    sql_query = utils.nl_to_sql(
                        question=nl_query, 
                        table_schema=table_schema, 
                        sample_data=sample_data,
                        openai_api_key=None  # ישתמש בערך ברירת מחדל
                    )
                    
                    # הצגת ה-SQL שנוצר
                    st.code(sql_query, language="sql")
                    
                    # בדיקה אם יש שגיאות בטקסט התשובה
                    if "error" in sql_query.lower() or "שגיאה" in sql_query.lower():
                        st.error(f"AI Error: {sql_query}")
                    else:
                        try:
                            # הרץ את השאילתה על הנתונים
                            results = utils.execute_sql(data, sql_query)
                            
                            # הצג תוצאות והוסף לסשן
                            st.success("Query Results:")
                            st.dataframe(results)
                            
                            # שמירת תוצאות השאילתה ב-session_state
                            st.session_state['query_results'] = results
                            st.session_state['last_query'] = sql_query
                        except Exception as e:
                            st.error(f"Error running query: {str(e)}")
                            st.session_state['query_results'] = None
                            st.session_state['last_query'] = None
                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
                    st.session_state['query_results'] = None
                    st.session_state['last_query'] = None
        # הצגת ויזואליזציה רק אם יש תוצאות בשאילתה האחרונה
        results = st.session_state.get('query_results')
        if results is not None and not results.empty and len(results.columns) >= 2:
            numeric_cols = results.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0 and len(results) > 1:
                st.subheader("Visualization")
                
                # סוגי הגרפים
                chart_options = ["Bar Chart", "Line Chart", "Pie Chart"]
                selected_chart = st.selectbox("Select chart type", chart_options, key="chart_type")
                
                # יצירת גרפים באמצעות matplotlib בלבד
                try:
                    # הכנת הנתונים
                    x_values = results.iloc[:, 0].values
                    y_values = results.iloc[:, 1].values
                    
                    # יצירת הגרף (משתמש רק ב-matplotlib ולא בפונקציות של streamlit)
                    fig, ax = plt.subplots(figsize=(10, 5), facecolor='#181943')
                    ax.set_facecolor('#181943')
                    
                    if selected_chart == "Bar Chart":
                        # יצירת גרף עמודות
                        bars = ax.bar(x_values, y_values, color='#00CFFF')
                        # הוספת ערכים מעל העמודות
                        for i, bar in enumerate(bars):
                            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                                    f'{y_values[i]:.1f}', ha='center', color='white', fontsize=9)
                    
                    elif selected_chart == "Line Chart":
                        # יצירת גרף קווי
                        ax.plot(x_values, y_values, marker='o', linestyle='-', linewidth=2, color='#00CFFF')
                        # הוספת נקודות ערך
                        for i, (x, y) in enumerate(zip(x_values, y_values)):
                            ax.text(x, y + 0.1, f'{y:.1f}', ha='center', color='white', fontsize=9)
                    
                    elif selected_chart == "Pie Chart" and len(results) <= 10:
                        # יצירת גרף עוגה
                        wedges, texts, autotexts = ax.pie(
                            y_values, 
                            labels=None,  # לא מציג תוויות מסביב לעוגה
                            autopct='%1.1f%%',
                            textprops={'color': 'white'},
                            colors=plt.cm.Blues(np.linspace(0.4, 0.7, len(results)))
                        )
                        # הוספת מקרא
                        ax.legend(wedges, x_values, title="Categories", loc="center left", 
                                 bbox_to_anchor=(1, 0, 0.5, 1), frameon=False,
                                 labelcolor='white')
                    
                    # עיצוב כללי לכל סוגי הגרפים
                    ax.set_title(f'{selected_chart} of {results.columns[1]} by {results.columns[0]}', 
                               color='white', fontsize=12, pad=15)
                    ax.tick_params(axis='x', colors='white')
                    ax.tick_params(axis='y', colors='white')
                    ax.spines['bottom'].set_color('white')
                    ax.spines['top'].set_color('white')
                    ax.spines['left'].set_color('white')
                    ax.spines['right'].set_color('white')
                    ax.grid(axis='y', linestyle='--', alpha=0.3, color='gray')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close(fig)  # סגירת הפיגורה לשחרור זיכרון
                    
                except Exception as e:
                    st.warning(f"שגיאה בהצגת הגרף: {str(e)}")
                    
                # תמיד מציג את הנתונים בטבלה משוכללת
                st.write("Data for Visualization:")
                st.dataframe(results, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.caption("© 2025 CashFlowIQ | Responsive Web & Mobile Dashboard | Beta Version")
