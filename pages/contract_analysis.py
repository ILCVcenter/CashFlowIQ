"""
pages/contract_analysis.py - עמוד ניתוח חוזים
"""
import streamlit as st
import json
import services
from ui.components import (
    render_list_of_dicts_table,
    render_vertical_table,
    render_warning_table,
    display_chat_message
)
from ui.styles import get_button_css

def render_contract_analysis_page():
    """רינדור עמוד ניתוח חוזים"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Contract Analysis (PDF)")
    
    model = st.selectbox("Select GPT Model", ["gpt-3.5-turbo", "gpt-4"], index=1)
    
    contract_text = ""
    contract_analysis = None
    contract_analysis_error = None
    
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    
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
                                try:
                                    contract_analysis = json.loads(result)
                                except Exception:
                                    contract_analysis_error = result
                            except Exception as e:
                                contract_analysis_error = f"Error analyzing contract: {str(e)}"
                        
                        # הצגת תוצאות הניתוח
                        if contract_analysis:
                            display_contract_analysis(contract_analysis)
                        elif contract_analysis_error:
                            st.error(contract_analysis_error)
                        
                        # צ'אט עם AI על החוזה
                        st.markdown("---")
                        display_contract_chat(contract_text, model)
                        
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

def display_contract_analysis(contract_analysis):
    """הצגת תוצאות ניתוח החוזה"""
    st.success("Contract Analysis Result:")
    
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
    
    # הצגת הערות/אזהרות בצורה טבלאית
    if 'Penalties' in contract_analysis and contract_analysis['Penalties']:
        render_warning_table(contract_analysis['Penalties'], "Attention")
    
    if 'Risks' in contract_analysis and contract_analysis['Risks']:
        render_warning_table(contract_analysis['Risks'], "Risks")

def display_contract_chat(contract_text, model):
    """הצגת צ'אט עם AI על החוזה"""
    st.subheader(":speech_balloon: Ask the AI about the contract")
    
    # הצגת היסטוריית הצ'אט
    for msg in st.session_state['chat_history']:
        display_chat_message(msg['role'], msg['content'])
    
    # סגנון כפתורים
    st.markdown(get_button_css(), unsafe_allow_html=True)
    
    # קלט משתמש
    user_question = st.text_input("Type your question about the contract", key="contract_chat_input")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        ask_clicked = st.button("Ask AI")
    with col2:
        clear_clicked = st.button("Clear Chat")
    
    # טיפול בלחיצות
    if ask_clicked and user_question.strip():
        with st.spinner("AI is analyzing your question..."):
            ai_answer = services.ask_contract_question(contract_text, user_question, None, model)
            st.session_state['chat_history'].append({'role': 'user', 'content': user_question})
            st.session_state['chat_history'].append({'role': 'ai', 'content': ai_answer})
        st.rerun()
    
    if clear_clicked:
        st.session_state['chat_history'] = []
        st.rerun() 