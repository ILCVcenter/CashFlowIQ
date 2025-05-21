import sys
import streamlit as st
import pandas as pd
import warnings
import services
import os

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
    st.subheader("Company Transactions Table")
    st.dataframe(data_converted, use_container_width=True)
    st.subheader(f"Cash Flow Over Time ({currency_label})")
    st.line_chart(data_converted.groupby("date")["amount"].sum(), use_container_width=True)
    st.subheader(f"Income vs Expenses by Category ({currency_label})")
    cat_sum = data_converted.groupby(["category"])["amount"].sum().reset_index()
    st.bar_chart(cat_sum, x="category", y="amount", use_container_width=True)

    # --- Cash Flow Forecast ---
    st.markdown("---")
    st.subheader(f"Cash Flow Forecast ({currency_label})")
    monthly = data_converted.copy()
    monthly['month'] = pd.to_datetime(monthly['date']).dt.to_period('M')
    st.markdown(f"**Historical Monthly Cash Flow ({currency_label})**")
    st.bar_chart(monthly.groupby('month')['amount'].sum(), use_container_width=True)
    periods = st.slider("Select forecast periods (months)", min_value=3, max_value=24, value=6)
    if st.button("Run Forecast"):
        with st.spinner("Calculating forecast..."):
            try:
                forecast_data = data_converted[['date', 'amount']].copy()
                forecast_df = services.forecast_cashflow(forecast_data, periods=periods)
                if not forecast_df.empty:
                    st.success(f"Forecast generated for {periods} months")
                    st.line_chart(forecast_df.set_index('date')['forecast'], use_container_width=True)
                    st.dataframe(forecast_df, use_container_width=True)
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
    if st.button("Run Query") and nl_query:
        with st.spinner("Processing query..."):
            table_schema = ", ".join(data.columns.tolist())
            sample_data = data.head(3).to_string(index=False)
            sql_query = utils.nl_to_sql(nl_query, table_schema, sample_data)
            st.code(sql_query, language="sql")
            try:
                results = utils.execute_sql(data, sql_query)
                st.success("Query Results:")
                st.dataframe(results)
                if not results.empty and len(results.columns) >= 2:
                    numeric_cols = results.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 0 and len(results) > 1:
                        st.subheader("Visualization")
                        chart_type = st.selectbox("Select chart type", ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart"])
                        if chart_type == "Bar Chart":
                            st.bar_chart(results)
                        elif chart_type == "Line Chart":
                            st.line_chart(results)
                        elif chart_type == "Scatter Plot":
                            st.scatter_chart(results)
                        elif chart_type == "Pie Chart" and len(results) <= 10:
                            import matplotlib.pyplot as plt
                            fig, ax = plt.subplots()
                            ax.pie(results.iloc[:, 1], labels=results.iloc[:, 0], autopct='%1.1f%%')
                            st.pyplot(fig)
            except Exception as e:
                st.error(f"Error running query: {str(e)}")

st.caption("© 2025 CashFlowIQ | Responsive Web & Mobile Dashboard | Beta Version")
