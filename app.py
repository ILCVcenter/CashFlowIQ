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

st.title("💸 CashFlowIQ - Manufacturing Company Dashboard")

# טעינת נתונים
@st.cache_data
def load_data():
    df = pd.read_csv("data/sample_data.csv")
    return df

data = load_data()

# מבנה טאבים
main_tab, inventory_tab, expenses_tab, contract_tab = st.tabs(["💰 Cash Flow", "📦 Inventory", "📊 Expenses", "📄 Contract Analysis"])

with main_tab:
    st.subheader("Company Transactions Table")
    st.dataframe(data, use_container_width=True)
    st.subheader("Cash Flow Over Time")
    st.line_chart(data.groupby("date")["amount"].sum())
    st.subheader("Income vs Expenses by Category")
    cat_sum = data.groupby(["category"])["amount"].sum().reset_index()
    st.bar_chart(cat_sum, x="category", y="amount")

with inventory_tab:
    st.subheader("Inventory Levels by Component")
    inventory = data.dropna(subset=["component", "inventory_level"])
    if not inventory.empty:
        st.bar_chart(inventory.set_index("component")["inventory_level"])
    else:
        st.info("No inventory data available.")

with expenses_tab:
    st.subheader("Expenses Breakdown by Type")
    expenses = data[data["category"] == "Expense"]
    if not expenses.empty:
        exp_type = expenses.groupby("type")["amount"].sum().abs().reset_index()
        st.bar_chart(exp_type, x="type", y="amount")
    else:
        st.info("No expense data available.")

with contract_tab:
    st.subheader("Contract Analysis (PDF)")
    model = st.selectbox("בחר מודל GPT", ["gpt-3.5-turbo", "gpt-4"], index=1)
    
    # משפר את הטיפול בשגיאות העלאת קובצים
    try:
        uploaded_file = st.file_uploader("Upload Contract PDF", type=["pdf"], accept_multiple_files=False)
        if uploaded_file is not None:
            with st.spinner("Extracting text from PDF..."):
                try:
                    text = services.extract_text_from_pdf(uploaded_file)
                    if text.strip():
                        st.text_area("Contract Text", text, height=200)
                        if st.button("Analyze Contract with GPT"):
                            with st.spinner("Analyzing contract with GPT..."):
                                try:
                                    result = services.analyze_contract(text, None, model)
                                    st.success("Contract Analysis Result:")
                                    st.json(result)
                                except Exception as e:
                                    st.error(f"Error analyzing contract: {str(e)}")
                                    st.info("Try again or check your network connection.")
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

st.caption("© 2024 CashFlowIQ | Responsive Web & Mobile Dashboard")
