import sys
import streamlit as st
import pandas as pd
import warnings
import services
import os
import matplotlib.pyplot as plt

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

# Main Title - large and bold
st.markdown('<p class="main-header" style="font-size:2.5rem; font-weight:bold; color:#1E88E5;">💸 CashFlowIQ - Manufacturing Company Dashboard</p>', unsafe_allow_html=True)

# טעינת נתונים
@st.cache_data
def load_data():
    df = pd.read_csv("data/sample_data.csv")
    return df

data = load_data()

# Navigation tabs - right after the title
main_tab, inventory_tab, expenses_tab, contract_tab, query_tab = st.tabs(["💰 Cash Flow", "📦 Inventory", "📊 Expenses", "📄 Contract Analysis", "🔍 Natural Language Queries"])

with main_tab:
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
        min_date = pd.to_datetime(data_converted['date']).min().date()
        max_date = pd.to_datetime(data_converted['date']).max().date()
        date_range = st.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
    
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
    
    # הצגת טבלת תזרים המזומנים
    st.dataframe(cashflow_display, use_container_width=True, height=400)
    
    # הצגת גרפים שימושיים - חלוקה לשלושה גרפים
    st.subheader(f"Cash Flow Visualizations ({currency_label})")
    
    tab1, tab2, tab3 = st.tabs(["Monthly Cash Flow", "Balance Over Time", "Income vs Expenses"])
    
    with tab1:
        # סיכום חודשי של הכנסות והוצאות
        data_for_cashflow['month'] = data_for_cashflow['date'].dt.strftime('%Y-%m')
        monthly_inflows = data_for_cashflow[data_for_cashflow['amount'] > 0].groupby('month')['amount'].sum()
        monthly_outflows = data_for_cashflow[data_for_cashflow['amount'] < 0].groupby('month')['amount'].sum().abs()
        monthly_cashflow = pd.DataFrame({
            'Inflows': monthly_inflows,
            'Outflows': monthly_outflows
        }).fillna(0)
        fig, ax = plt.subplots(figsize=(8, 3))
        monthly_cashflow.plot(kind='bar', ax=ax, rot=0)
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount')
        ax.set_title('Monthly Cash Flow')
        ax.tick_params(axis='x', labelrotation=0)
        st.pyplot(fig)
    
    with tab2:
        # גרף יתרה מצטברת לאורך זמן
        balance_over_time = pd.DataFrame({
            'Date': daily_cashflow['date'],
            'Balance': daily_cashflow['closing_balance']
        }).set_index('Date')
        
        st.line_chart(balance_over_time, use_container_width=True)
    
    with tab3:
        # ניתוח הכנסות והוצאות לפי קטגוריה
        income_by_type = data_for_cashflow[data_for_cashflow['amount'] > 0].groupby('type')['amount'].sum().reset_index()
        expense_by_type = data_for_cashflow[data_for_cashflow['amount'] < 0].groupby('type')['amount'].sum().abs().reset_index()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Income Sources")
            fig1, ax1 = plt.subplots(figsize=(8, 3))
            income_by_type.plot(kind='bar', x='type', y='amount', ax=ax1, legend=False, rot=0)
            ax1.set_xlabel('Type')
            ax1.set_ylabel('Amount')
            ax1.set_title('Income Sources')
            ax1.tick_params(axis='x', labelrotation=0)
            st.pyplot(fig1)
        with col2:
            st.subheader("Expense Categories")
            fig2, ax2 = plt.subplots(figsize=(8, 3))
            expense_by_type.plot(kind='bar', x='type', y='amount', ax=ax2, legend=False, rot=0)
            ax2.set_xlabel('Type')
            ax2.set_ylabel('Amount')
            ax2.set_title('Expense Categories')
            ax2.tick_params(axis='x', labelrotation=0)
            st.pyplot(fig2)
    
    # --- Cash Flow Forecast ---
    st.markdown("---")
    st.subheader(f"Cash Flow Forecast ({currency_label})")
    forecast_col1, forecast_col2, forecast_col3 = st.columns(3)
    with forecast_col1:
        forecast_min_date = pd.to_datetime(data_converted['date']).min().date()
        forecast_max_date = pd.to_datetime(data_converted['date']).max().date()
        forecast_date_range = st.date_input("Forecast Date Range", [forecast_min_date, forecast_max_date], min_value=forecast_min_date, max_value=forecast_max_date, key="forecast_date_range")
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
        forecast_df = services.forecast_cashflow(forecast_data, periods=6)  # ברירת מחדל 6 חודשים
        if not forecast_df.empty:
            last_balance = forecast_data_for_cashflow['amount'].cumsum().iloc[-1] if not forecast_data_for_cashflow.empty else 100000
            forecast_display = pd.DataFrame()
            forecast_display['date'] = forecast_df['date']
            forecast_display['date_str'] = forecast_display['date'].dt.strftime('%d/%m/%Y')
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
            forecast_table = pd.DataFrame({
                'Date': forecast_display['date_str'],
                'Opening Balance': forecast_display['opening_balance'].map('${:,.2f}'.format),
                'Cash Inflows': forecast_display['cash_inflows'].map('${:,.2f}'.format),
                'Cash Outflows': forecast_display['cash_outflows'].map('${:,.2f}'.format),
                'Closing Balance': forecast_display['closing_balance'].map('${:,.2f}'.format),
                'Forecast Value': forecast_display['forecast'].map('${:,.2f}'.format)
            })
            st.dataframe(forecast_table, use_container_width=True)
            st.subheader("Forecast Visualization")
            forecast_chart_data = pd.DataFrame({
                'Date': forecast_display['date'],
                'Forecast': forecast_display['forecast'],
                'Balance': forecast_display['closing_balance']
            }).set_index('Date')
            chart_tab1, chart_tab2, chart_tab3 = st.tabs(["Monthly Cash Flow", "Balance Over Time", "Income vs Expenses"])
            with chart_tab1:
                # Monthly Cash Flow Forecast
                forecast_chart_data_month = forecast_chart_data.resample('M').sum()
                fig, ax = plt.subplots(figsize=(3, 1.5))
                forecast_chart_data_month[['Forecast']].plot(kind='bar', ax=ax, rot=0)
                ax.set_xlabel('Month', fontsize=8)
                ax.set_ylabel('Forecast', fontsize=8)
                ax.set_title('Monthly Cash Flow Forecast', fontsize=10)
                ax.tick_params(axis='x', labelrotation=45, labelsize=6)
                ax.tick_params(axis='y', labelsize=6)
                st.pyplot(fig)
            with chart_tab2:
                fig, ax = plt.subplots(figsize=(3, 1.5))
                forecast_chart_data[['Balance']].plot(ax=ax)
                ax.set_xlabel('Date', fontsize=8)
                ax.set_ylabel('Balance', fontsize=8)
                ax.set_title('Projected Balance Over Time', fontsize=10)
                ax.tick_params(axis='x', labelsize=6)
                ax.tick_params(axis='y', labelsize=6)
                st.pyplot(fig)
            with chart_tab3:
                # הכנסות/הוצאות לפי סוג
                income_types = forecast_display[forecast_display['forecast'] > 0]['forecast']
                expense_types = forecast_display[forecast_display['forecast'] < 0]['forecast'].abs()
                fig, ax = plt.subplots(figsize=(3, 1.5))
                income_types.plot(kind='bar', color='green', ax=ax, position=0, width=0.4, label='Income')
                expense_types.plot(kind='bar', color='red', ax=ax, position=1, width=0.4, label='Expense')
                ax.set_xlabel('Period', fontsize=8)
                ax.set_ylabel('Amount', fontsize=8)
                ax.set_title('Income vs Expenses (Forecast)', fontsize=10)
                ax.tick_params(axis='x', labelsize=6)
                ax.tick_params(axis='y', labelsize=6)
                ax.legend(fontsize=6)
                st.pyplot(fig)
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
    st.download_button(
        label="Download CSV Data",
        data=csv,
        file_name='cashflow_data.csv',
        mime='text/csv',
    )

with inventory_tab:
    st.subheader("Inventory Levels by Component")
    inventory = data_converted.dropna(subset=["component", "inventory_level"])
    if not inventory.empty:
        st.bar_chart(inventory.set_index("component")["inventory_level"], use_container_width=True)
    else:
        st.info("No inventory data available.")

with expenses_tab:
    st.subheader("Expenses Breakdown by Type")
    expenses = data_converted[data_converted["category"] == "Expense"]
    if not expenses.empty:
        exp_type = expenses.groupby("type")["amount"].sum().abs().reset_index()
        st.bar_chart(exp_type, x="type", y="amount", use_container_width=True)
    else:
        st.info("No expense data available.")

with contract_tab:
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
                                st.markdown(f"<div style='text-align:left; background:#e6f0ff; padding:8px; border-radius:8px; margin-bottom:4px;'><b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
                            else:
                                content = msg['content']
                                # תמיד מיושר לשמאל (LTR)
                                if content.strip().startswith('1.') or '\n1.' in content:
                                    items = [line.strip() for line in content.split('\n') if line.strip() and (line.strip()[0].isdigit() and line.strip()[1] in ['.',')'])]
                                    if items:
                                        st.markdown("<div style='text-align:left; background:#f6ffe6; padding:8px; border-radius:8px; margin-bottom:8px;'><b>AI:</b><ul style='text-align:left'>" + ''.join([f"<li>{v}</li>" for v in items]) + "</ul></div>", unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"<div style='text-align:left; background:#f6ffe6; padding:8px; border-radius:8px; margin-bottom:8px;'><b>AI:</b> {content}</div>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<div style='text-align:left; background:#f6ffe6; padding:8px; border-radius:8px; margin-bottom:8px;'><b>AI:</b> {content}</div>", unsafe_allow_html=True)
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

with query_tab:
    st.subheader("Natural Language Queries")
    st.markdown("Ask questions about the data in natural language, and the system will translate them to SQL queries and display the results")
    import utils
    nl_query = st.text_input("Enter your question in natural language", placeholder="For example: How much income was there in February?")
    run_query = st.button("Run Query")
    if run_query and nl_query:
        with st.spinner("Processing query..."):
            table_schema = ", ".join(data.columns.tolist())
            sample_data = data.head(3).to_string(index=False)
            sql_query = utils.nl_to_sql(nl_query, table_schema, sample_data)
            st.code(sql_query, language="sql")
            if "error" in sql_query.lower() or "שגיאה" in sql_query.lower():
                st.error(f"AI Error: {sql_query}")
            else:
                try:
                    results = utils.execute_sql(data, sql_query)
                    st.success("Query Results:")
                    st.dataframe(results)
                    # שמירת תוצאות השאילתה ב-session_state
                    st.session_state['query_results'] = results
                    st.session_state['last_query'] = sql_query
                except Exception as e:
                    st.error(f"Error running query: {str(e)}")
                    st.session_state['query_results'] = None
                    st.session_state['last_query'] = None
    # הצגת ויזואליזציה רק אם יש תוצאות בשאילתה האחרונה
    results = st.session_state.get('query_results')
    if results is not None and not results.empty and len(results.columns) >= 2:
        numeric_cols = results.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0 and len(results) > 1:
            st.subheader("Visualization")
            chart_type = st.selectbox("Select chart type", ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart"], key="chart_type")
            if chart_type == "Bar Chart":
                st.bar_chart(results)
            elif chart_type == "Line Chart":
                st.line_chart(results)
            elif chart_type == "Scatter Plot":
                st.scatter_chart(results)
            elif chart_type == "Pie Chart" and len(results) <= 10:
                fig, ax = plt.subplots(figsize=(6, 3))
                ax.pie(results.iloc[:, 1], labels=results.iloc[:, 0], autopct='%1.1f%%')
                st.pyplot(fig)

st.caption("© 2025 CashFlowIQ | Responsive Web & Mobile Dashboard | Beta Version")
