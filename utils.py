"""
utils.py - פונקציות עזר לשימוש ב-CashFlowIQ
"""

import pandas as pd
import os
import openai
import re
import duckdb
from dotenv import load_dotenv

# טען תמיד את .env מתוך תיקיית CashFlowIQ
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

def get_openai_key():
    # טען משתני סביבה מקובץ .env
    return os.environ.get("OPENAI_API_KEY")

def nl_to_sql(question, table_schema, sample_data, openai_api_key=None):
    """
    המרת שאלה בשפה טבעית לשאילתת SQL
    """
    if not openai_api_key:
        openai_api_key = get_openai_key()
    if openai_api_key:
        openai.api_key = openai_api_key
    system_prompt = """
You are a professional SQL assistant.
The table name is 'data'. Always use 'data' as the table name in your queries.
The 'date' column is a string in format 'YYYY-MM-DD'. Always cast it to DATE using CAST(date AS DATE) or STRPTIME(date, '%Y-%m-%d') before using it in date/time functions (such as STRFTIME, DATE_TRUNC, etc).
Convert the following natural language question to a valid SQL query for DuckDB.
Return only the SQL query, no explanations.

Example:
Question: Show me the monthly income
SQL: SELECT STRFTIME('%Y-%m', CAST(date AS DATE)) AS month, SUM(amount) AS income FROM data WHERE category = 'Income' GROUP BY month ORDER BY month;
"""
    user_prompt = f"""Table schema:
{table_schema}

Sample data:
{sample_data}

Question: {question}
"""
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
