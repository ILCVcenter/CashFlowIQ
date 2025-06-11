"""
pages/query_chat.py - עמוד שאילתות בשפה טבעית
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import utils

def render_query_chat_page(data):
    """רינדור עמוד שאילתות בשפה טבעית"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Natural Language Queries")
    st.markdown("Ask questions about the data in natural language, and the system will translate them to SQL queries and display the results")
    
    nl_query = st.text_input("Enter your question in natural language", 
                           placeholder="For example: How much income was there in February?")
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
        display_query_visualization(results)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_query_visualization(results):
    """הצגת ויזואליזציה של תוצאות השאילתה"""
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
            
            # יצירת הגרף
            fig, ax = plt.subplots(figsize=(10, 5), facecolor='#181943')
            ax.set_facecolor('#181943')
            
            if selected_chart == "Bar Chart":
                create_bar_chart(ax, x_values, y_values)
            elif selected_chart == "Line Chart":
                create_line_chart(ax, x_values, y_values)
            elif selected_chart == "Pie Chart" and len(results) <= 10:
                create_pie_chart(ax, x_values, y_values)
            
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

def create_bar_chart(ax, x_values, y_values):
    """יצירת גרף עמודות"""
    bars = ax.bar(x_values, y_values, color='#00CFFF')
    # הוספת ערכים מעל העמודות
    for i, bar in enumerate(bars):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                f'{y_values[i]:.1f}', ha='center', color='white', fontsize=9)

def create_line_chart(ax, x_values, y_values):
    """יצירת גרף קווי"""
    ax.plot(x_values, y_values, marker='o', linestyle='-', linewidth=2, color='#00CFFF')
    # הוספת נקודות ערך
    for i, (x, y) in enumerate(zip(x_values, y_values)):
        ax.text(x, y + 0.1, f'{y:.1f}', ha='center', color='white', fontsize=9)

def create_pie_chart(ax, x_values, y_values):
    """יצירת גרף עוגה"""
    wedges, texts, autotexts = ax.pie(
        y_values, 
        labels=None,  # לא מציג תוויות מסביב לעוגה
        autopct='%1.1f%%',
        textprops={'color': 'white'},
        colors=plt.cm.Blues(np.linspace(0.4, 0.7, len(y_values)))
    )
    # הוספת מקרא
    ax.legend(wedges, x_values, title="Categories", loc="center left", 
             bbox_to_anchor=(1, 0, 0.5, 1), frameon=False,
             labelcolor='white') 