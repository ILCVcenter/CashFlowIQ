"""
pages/cash_flow.py - עמוד ניתוח תזרים מזומנים
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import services
from ui.components import convert_df_to_csv
from ui.styles import get_button_css
from data.data_loader import (
    filter_data_by_date_range, 
    filter_data_by_categories, 
    filter_data_by_types,
    process_uploaded_csv,
    save_data_to_source
)

def render_cash_flow_page(data):
    """רינדור עמוד תזרים המזומנים"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Currency Conversion at the top
    st.subheader("Currency Conversion")
    col1, col2 = st.columns(2)
    with col1:
        base_currency = st.selectbox("Base Currency", ["USD", "EUR", "ILS", "GBP"], index=0, key="base_currency")
    with col2:
        target_currency = st.selectbox("Target Currency", ["USD", "EUR", "ILS", "GBP"], index=1, key="target_currency")
    
    # Get exchange rate
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
    
    st.markdown("---")
    
    # אפשרויות סינון
    st.subheader("Cash Flow Statement")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # הגבלת טווח התאריכים
        min_date = pd.to_datetime('2024-01-01').date()
        max_date = pd.to_datetime('today').date()
        
        default_start = min_date
        default_end = max_date
        
        data_min_date = pd.to_datetime(data_converted['date']).min().date()
        if data_min_date > min_date:
            min_date = data_min_date
            default_start = data_min_date
            
        date_range = st.date_input("Date Range", [default_start, default_end], 
                                 min_value=min_date, max_value=max_date)
    
    with col2:
        category_options = data_converted['category'].unique()
        category_filter = st.multiselect("Category Filter", category_options, default=[])
    
    with col3:
        type_options = data_converted['type'].unique()
        type_filter = st.multiselect("Type Filter", type_options, default=[])
    
    # סינון הנתונים
    data_for_cashflow = data_converted.copy()
    data_for_cashflow = filter_data_by_date_range(data_for_cashflow, date_range)
    data_for_cashflow = filter_data_by_categories(data_for_cashflow, category_filter)
    data_for_cashflow = filter_data_by_types(data_for_cashflow, type_filter)
    
    if data_for_cashflow.empty:
        st.warning("אין נתונים בטווח התאריכים שנבחר.")
        return
    
    # הצגת תזרים מזומנים
    display_cashflow_statement(data_for_cashflow, currency_label)
    
    # תחזית
    st.markdown("---")
    display_cashflow_forecast(data_converted, currency_label)
    
    # Export וייבוא נתונים
    st.markdown("---")
    handle_data_export_import(data_converted)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_cashflow_statement(data_for_cashflow, currency_label):
    """הצגת דוח תזרים מזומנים"""
    # מיון לפי תאריך
    data_for_cashflow = data_for_cashflow.sort_values('date')
    
    # יצירת נתוני תזרים מזומנים לפי יום
    daily_cashflow = data_for_cashflow.groupby(data_for_cashflow['date'].dt.date).agg({
        'amount': 'sum',
        'description': lambda x: ", ".join(set(x)) if len(set(x)) <= 3 else ", ".join(list(set(x))[:3]) + "..."
    }).reset_index()
    daily_cashflow['date_str'] = daily_cashflow['date'].apply(lambda x: x.strftime('%d/%m/%Y'))
    
    # חישוב יתרות
    initial_balance = 100000
    daily_cashflow['cash_inflows'] = daily_cashflow['amount'].apply(lambda x: max(0, x))
    daily_cashflow['cash_outflows'] = daily_cashflow['amount'].apply(lambda x: min(0, x)).abs()
    
    running_balance = initial_balance
    opening_balances = []
    closing_balances = []
    
    for i, row in daily_cashflow.iterrows():
        opening_balances.append(running_balance)
        closing_balance = running_balance + row['amount']
        closing_balances.append(closing_balance)
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
    
    # הצגת טבלה וגרפים
    table_col, graph_col = st.columns([2, 1])
    with table_col:
        st.dataframe(cashflow_display, use_container_width=True, height=400)
    with graph_col:
        display_cashflow_charts(data_for_cashflow, daily_cashflow)

def display_cashflow_charts(data_for_cashflow, daily_cashflow):
    """הצגת גרפים של תזרים מזומנים"""
    st.markdown('<div style="margin-bottom:16px;"></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Monthly Cash Flow", "Balance Over Time", "Income vs Expenses"])
    
    with tab1:
        display_monthly_cashflow_chart(data_for_cashflow)
    with tab2:
        display_balance_over_time_chart(daily_cashflow)
    with tab3:
        display_income_vs_expenses_chart(data_for_cashflow)

def display_monthly_cashflow_chart(data_for_cashflow):
    """גרף תזרים חודשי"""
    data_for_cashflow['month'] = data_for_cashflow['date'].dt.strftime('%Y-%m')
    monthly_inflows = data_for_cashflow[data_for_cashflow['amount'] > 0].groupby('month')['amount'].sum()
    monthly_outflows = data_for_cashflow[data_for_cashflow['amount'] < 0].groupby('month')['amount'].sum().abs()
    monthly_cashflow = pd.DataFrame({'Inflows': monthly_inflows, 'Outflows': monthly_outflows}).fillna(0)
    
    try:
        fig, ax = plt.subplots(figsize=(2.5, 1.8), facecolor='#181943')
        ax.set_facecolor('#181943')
        monthly_cashflow.plot(kind='bar', ax=ax, rot=30, color=['#00CFFF', '#9966FF'])
        
        if len(monthly_cashflow.index) > 10:
            step = max(1, len(monthly_cashflow.index) // 10)
            xlabels = ax.get_xticklabels()
            for i, label in enumerate(xlabels):
                if i % step != 0:
                    label.set_visible(False)
        
        ax.set_xlabel('Month', fontsize=7, color='white')
        ax.set_ylabel('Amount', fontsize=7, color='white')
        ax.set_title('Monthly Cash Flow', fontsize=8, color='white', pad=15)
        ax.tick_params(axis='x', labelrotation=45, labelsize=6, colors='white')
        ax.tick_params(axis='y', labelsize=6, colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.grid(axis='y', linestyle='--', alpha=0.2, color='white')
        ax.legend(fontsize=6, facecolor='#23255d', edgecolor='#23255d', labelcolor='white')
        
        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.warning(f"לא ניתן להציג את הגרף: {str(e)}")

def display_balance_over_time_chart(daily_cashflow):
    """גרף יתרה לאורך זמן"""
    balance_over_time = pd.DataFrame({
        'Date': daily_cashflow['date'], 
        'Balance': daily_cashflow['closing_balance']
    }).set_index('Date')
    
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

def display_income_vs_expenses_chart(data_for_cashflow):
    """גרף הכנסות מול הוצאות"""
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

def display_cashflow_forecast(data_converted, currency_label):
    """הצגת תחזית תזרים מזומנים"""
    st.subheader(f"Cash Flow Forecast ({currency_label})")
    
    forecast_col1, forecast_col2, forecast_col3 = st.columns(3)
    with forecast_col1:
        forecast_min_date = pd.to_datetime('today').date()
        forecast_max_date = pd.to_datetime('2027-12-31').date()
        
        forecast_default_start = forecast_min_date
        forecast_default_end = min(forecast_max_date, (forecast_min_date + pd.DateOffset(months=6)).date())
        
        forecast_date_range = st.date_input("Forecast Date Range", 
                                          [forecast_default_start, forecast_default_end], 
                                          min_value=forecast_min_date, 
                                          max_value=forecast_max_date,
                                          key="forecast_date_range")
    with forecast_col2:
        forecast_category_options = data_converted['category'].unique()
        forecast_category_filter = st.multiselect("Forecast Category Filter", 
                                                forecast_category_options, default=[])
    with forecast_col3:
        forecast_type_options = data_converted['type'].unique()
        forecast_type_filter = st.multiselect("Forecast Type Filter", 
                                            forecast_type_options, default=[])
    
    # סינון נתונים לתחזית
    forecast_data_for_cashflow = data_converted.copy()
    forecast_data_for_cashflow['date'] = pd.to_datetime(forecast_data_for_cashflow['date'])
    forecast_data_for_cashflow = filter_data_by_date_range(forecast_data_for_cashflow, forecast_date_range)
    forecast_data_for_cashflow = filter_data_by_categories(forecast_data_for_cashflow, forecast_category_filter)
    forecast_data_for_cashflow = filter_data_by_types(forecast_data_for_cashflow, forecast_type_filter)
    
    # חישוב תחזית
    try:
        forecast_data = forecast_data_for_cashflow[['date', 'amount']].copy()
        forecast_data['date'] = pd.to_datetime(forecast_data['date'])
        
        if forecast_data.empty:
            st.warning("אין נתוני תזרים בטווח התאריכים שנבחר לתחזית.")
            forecast_data = data_converted[['date', 'amount']].copy()
            forecast_data['date'] = pd.to_datetime(forecast_data['date'])
        
        forecast_df = services.forecast_cashflow(forecast_data, periods=6)
        
        if not forecast_df.empty:
            display_forecast_results(forecast_df, forecast_data_for_cashflow)
        else:
            st.info("No forecast data available.")
            
    except Exception as e:
        st.error(f"Forecast error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def display_forecast_results(forecast_df, forecast_data_for_cashflow):
    """הצגת תוצאות התחזית"""
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
    
    if forecast_display.empty or forecast_display['date'].isnull().all() or forecast_display['forecast'].isnull().all():
        st.warning("אין נתוני תחזית בטווח התאריכים שנבחר.")
        return
    
    # טבלת תחזית
    forecast_table = pd.DataFrame({
        'Date': forecast_display['date_str'],
        'Opening Balance': forecast_display['opening_balance'].map('${:,.2f}'.format),
        'Cash Inflows': forecast_display['cash_inflows'].map('${:,.2f}'.format),
        'Cash Outflows': forecast_display['cash_outflows'].map('${:,.2f}'.format),
        'Closing Balance': forecast_display['closing_balance'].map('${:,.2f}'.format),
        'Notes': forecast_display.get('description', ['']*len(forecast_display))
    })
    
    st.subheader("Forecast Visualization")
    
    forecast_table_col, forecast_graph_col = st.columns([2, 1])
    with forecast_table_col:
        st.dataframe(forecast_table, use_container_width=True, height=400)
    with forecast_graph_col:
        display_forecast_charts(forecast_display)

def display_forecast_charts(forecast_display):
    """הצגת גרפי תחזית"""
    st.markdown('<div style="margin-bottom:16px;"></div>', unsafe_allow_html=True)
    
    forecast_chart_data = pd.DataFrame({
        'Date': forecast_display['date'],
        'Forecast': forecast_display['forecast'],
        'Balance': forecast_display['closing_balance']
    }).set_index('Date')
    
    chart_tab1, chart_tab2, chart_tab3 = st.tabs(["Monthly Cash Flow", "Balance Over Time", "Income vs Expenses"])
    
    with chart_tab1:
        display_monthly_forecast_chart(forecast_chart_data)
    with chart_tab2:
        display_balance_forecast_chart(forecast_chart_data)
    with chart_tab3:
        display_income_expense_forecast_chart(forecast_display)

def display_monthly_forecast_chart(forecast_chart_data):
    """גרף תחזית חודשית"""
    try:
        if not forecast_chart_data.empty and not forecast_chart_data['Forecast'].isnull().all():
            forecast_chart_data_month = forecast_chart_data.resample('ME').sum()
            
            if not forecast_chart_data_month.empty:
                fig, ax = plt.subplots(figsize=(3, 2.3), facecolor='#181943')
                ax.set_facecolor('#181943')
                forecast_chart_data_month[['Forecast']].plot(kind='bar', ax=ax, rot=30, color='#00CFFF')
                
                if len(forecast_chart_data_month.index) > 0:
                    xlabels = [item.strftime('%Y-%m-%d') for item in forecast_chart_data_month.index.to_list()]
                    ax.set_xticklabels(xlabels)
                
                ax.set_xlabel('Month', fontsize=8, color='white')
                ax.set_ylabel('Forecast', fontsize=8, color='white')
                ax.set_title('Monthly Cash Flow Forecast', fontsize=10, color='white', pad=15)
                ax.tick_params(axis='x', labelrotation=30, labelsize=6, colors='white')
                ax.tick_params(axis='y', labelsize=6, colors='white')
                ax.spines['bottom'].set_color('white')
                ax.spines['top'].set_color('white')
                ax.spines['left'].set_color('white')
                ax.spines['right'].set_color('white')
                ax.grid(axis='y', linestyle='--', alpha=0.2, color='white')
                
                for i, val in enumerate(forecast_chart_data_month['Forecast']):
                    if not pd.isna(val):
                        ax.text(i, val + (0.1 * val if val > 0 else -0.1 * abs(val)), 
                               f'${int(val)}', ha='center', va='bottom' if val > 0 else 'top', 
                               fontsize=6, color='white')
                
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("אין נתונים מספיקים להצגת גרף תחזית חודשי.")
        else:
            st.warning("אין נתוני תחזית זמינים להצגת גרף.")
    except Exception as e:
        st.warning(f"לא ניתן להציג את גרף התחזית החודשי: {str(e)}")

def display_balance_forecast_chart(forecast_chart_data):
    """גרף תחזית יתרה"""
    try:
        if not forecast_chart_data.empty and not forecast_chart_data['Balance'].isnull().all():
            fig, ax = plt.subplots(figsize=(3, 2.3), facecolor='#181943')
            ax.set_facecolor('#181943')
            forecast_chart_data[['Balance']].plot(ax=ax, color='#00CFFF', linewidth=2)
            
            date_formatter = plt.matplotlib.dates.DateFormatter('%Y-%m-%d')
            ax.xaxis.set_major_formatter(date_formatter)
            
            ax.set_xlabel('Date', fontsize=8, color='white')
            ax.set_ylabel('Balance', fontsize=8, color='white')
            ax.set_title('Projected Balance Over Time', fontsize=10, color='white', pad=15)
            ax.tick_params(axis='x', labelsize=6, colors='white')
            ax.tick_params(axis='y', labelsize=6, colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.grid(axis='y', linestyle='--', alpha=0.2, color='white')
            
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("אין נתוני מאזן זמינים להצגת גרף.")
    except Exception as e:
        st.warning(f"לא ניתן להציג את גרף המאזן: {str(e)}")

def display_income_expense_forecast_chart(forecast_display):
    """גרף תחזית הכנסות מול הוצאות"""
    try:
        if not forecast_display.empty and not forecast_display['forecast'].isnull().all():
            income_types = forecast_display[forecast_display['forecast'] > 0]['forecast']
            expense_types = forecast_display[forecast_display['forecast'] < 0]['forecast'].abs()
            
            if not income_types.empty or not expense_types.empty:
                fig, ax = plt.subplots(figsize=(3, 2.3), facecolor='#181943')
                ax.set_facecolor('#181943')
                
                if not income_types.empty:
                    income_types.plot(kind='bar', color='#00CFFF', ax=ax, position=0, width=0.4, label='Income')
                if not expense_types.empty:
                    expense_types.plot(kind='bar', color='#9966FF', ax=ax, position=1, width=0.4, label='Expense')
                
                ax.set_xlabel('Period', fontsize=8, color='white')
                ax.set_ylabel('Amount', fontsize=8, color='white')
                ax.set_title('Income vs Expenses (Forecast)', fontsize=10, color='white', pad=15)
                
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
                
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("אין נתוני הכנסות/הוצאות זמינים להצגת גרף.")
        else:
            st.warning("אין נתוני תחזית זמינים להצגת גרף.")
    except Exception as e:
        st.warning(f"לא ניתן להציג את גרף ההכנסות והוצאות: {str(e)}")

def handle_data_export_import(data_converted):
    """טיפול בייצוא וייבוא נתונים"""
    csv = convert_df_to_csv(data_converted)
    
    # עיצוב כפתור ההורדה
    st.markdown(get_button_css(), unsafe_allow_html=True)
    
    # כפתור הורדה
    st.download_button(
        label="Download CSV Data",
        data=csv,
        file_name='cashflow_data.csv',
        mime='text/csv',
    )
    
    # העלאת קובץ CSV חדש
    uploaded_file = st.file_uploader("העלה קובץ CSV להוספת נתונים", type=["csv"])
    if uploaded_file is not None:
        merged_data = process_uploaded_csv(uploaded_file, data_converted)
        
        if merged_data is not data_converted:  # אם הנתונים השתנו
            # אפשרות להוריד את הקובץ המשולב
            csv_merged = merged_data.to_csv(index=False).encode('utf-8')
            download_col1, download_col2 = st.columns(2)
            
            with download_col1:
                st.download_button(
                    label="הורד את כל הנתונים (CSV)",
                    data=csv_merged,
                    file_name='merged_cashflow_data.csv',
                    mime='text/csv',
                )
            
            with download_col2:
                save_to_source = st.button("שמור נתונים לקובץ המקור ורענן")
                if save_to_source:
                    if save_data_to_source(merged_data):
                        st.rerun() 