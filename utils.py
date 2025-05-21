"""
utils.py - פונקציות עזר לשימוש ב-CashFlowIQ
"""

import pandas as pd
import os
import openai
import re
import duckdb

def get_openai_key():
    try:
        with open("Key", "r") as f:
            return f.read().strip()
    except:
        return os.environ.get("OPENAI_API_KEY")

def nl_to_sql(question, table_schema, sample_data, openai_api_key=None):
    """
    המרת שאלה בשפה טבעית לשאילתת SQL
    """
    if not openai_api_key:
        openai_api_key = get_openai_key()
    if openai_api_key:
        openai.api_key = openai_api_key
    system_prompt = """אתה עוזר SQL מקצועי. 
    תפקידך להמיר שאלות בשפה טבעית לשאילתות SQL תקפות שמתאימות לסכמה הנתונה.
    החזר רק את שאילתת ה-SQL ללא הסברים או דברים נוספים."""
    user_prompt = f"""סכמת הטבלה:
    {table_schema}
    
    דוגמת נתונים:
    {sample_data}
    
    שאלה: {question}
    
    תרגם לשאילתת SQL:"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        sql_query = response.choices[0].message.content.strip()
        sql_query = re.sub(r'^```sql', '', sql_query)
        sql_query = re.sub(r'```$', '', sql_query)
        return sql_query.strip()
    except Exception as e:
        return f"שגיאה בהמרת שאילתה: {str(e)}"

def execute_sql(df, sql_query):
    """
    הרצת שאילתת SQL על DataFrame באמצעות DuckDB
    """
    try:
        conn = duckdb.connect(database=':memory:')
        conn.register('data', df)
        result = conn.execute(sql_query).fetchdf()
        return result
    except Exception as e:
        raise Exception(f"שגיאה בהרצת SQL: {str(e)}")
