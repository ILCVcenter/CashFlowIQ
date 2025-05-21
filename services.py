"""
services.py - מודול שירותים עיקריים ל-CashFlowIQ

פונקציות:
- extract_text_from_pdf: חילוץ טקסט מקובץ PDF
- analyze_contract: ניתוח חוזה באמצעות GPT
- ask_contract_question: מענה לשאלות על החוזה
- get_exchange_rate: שליפת שערי חליפין בזמן אמת
- forecast_cashflow: חיזוי תזרים מזומנים

כל פונקציה מתועדת ומופרדת באחריותה.
"""

import sys
import PyPDF2
import openai
import os
import json
import re
from dotenv import load_dotenv
import requests
import pandas as pd
import numpy as np
from datetime import timedelta

# חילוץ טקסט מ-PDF

def extract_text_from_pdf(pdf_file):
    """
    חילוץ טקסט מקובץ PDF שהועלה ע"י המשתמש.
    :param pdf_file: קובץ PDF (streamlit uploader)
    :return: טקסט מלא מהקובץ
    """
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# ניתוח חוזה עם GPT

def extract_json_from_text(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return None

def get_openai_key_from_file():
    try:
        with open("Key", "r") as f:
            return f.read().strip()
    except Exception:
        return None

def analyze_contract(text, openai_api_key=None, model="gpt-4"):
    """
    ניתוח חוזה באמצעות GPT, החזרת JSON מובנה עם סעיפים פיננסיים עיקריים.
    :param text: טקסט החוזה
    :param context: הקשר נוסף (אופציונלי)
    :param model: דגם GPT לשימוש
    :return: JSON כתוצאה מניתוח החוזה
    """
    if not openai_api_key:
        openai_api_key = get_openai_key_from_file()
    if openai_api_key:
        openai.api_key = openai_api_key
    
    system_prompt = (
        "You are a financial contract analysis assistant. Extract the following financial terms from the contract and return ONLY valid JSON, no explanations. "
        "Each field should be a list of objects with the specified keys."
    )
    user_prompt = (
        "Extract the following financial terms from the contract text and return them as a JSON object with these fields:\n"
        "- Payment Amounts: a list of objects, each with 'Product', 'Description', and 'Value' fields.\n"
        "- Payment Dates: a list of objects, each with 'Type', 'Description', and 'Date' fields.\n"
        "- Payment Terms: a list of objects, each with 'Type', 'Description', and 'Details' fields.\n"
        "- Penalties: a list of objects, each with 'Type', 'Description', and 'Value' fields.\n"
        "- Contract Period: a list of objects, each with 'Type', 'Description', and 'Value' fields.\n"
        "Return only valid JSON, with each field as a list of objects as described above. Do not add any text or explanation.\n\n" + text[:3000]
    )
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )
        result = response.choices[0].message.content.strip()
        json_str = extract_json_from_text(result)
        if json_str:
            return json_str
        return result
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return json.dumps({
            "error": "Failed to parse response",
            "raw_response": str(e)
        })

def ask_contract_question(contract_text, question, openai_api_key=None, model="gpt-4"):
    """
    מענה לשאלה חופשית על החוזה באמצעות GPT.
    :param contract_text: טקסט החוזה
    :param question: שאלה מהמשתמש
    :param context: הקשר נוסף (אופציונלי)
    :param model: דגם GPT לשימוש
    :return: תשובת GPT
    """
    if not openai_api_key:
        openai_api_key = get_openai_key_from_file()
    if openai_api_key:
        openai.api_key = openai_api_key
    system_prompt = (
        "אתה עוזר חוזים חכם. ענה בקצרה, ברור ומדויק על כל שאלה שתישאל לגבי החוזה המצורף."
    )
    user_prompt = f"חוזה:\n{contract_text[:3000]}\n\nשאלה: {question}"
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"שגיאה בשליחת שאלה ל-AI: {str(e)}"

def get_exchange_rate(base_currency, target_currency):
    """
    שליפת שער חליפין בזמן אמת ממספר מקורות אפשריים, עם fallback למקרה של כשל.
    :param base_currency: מטבע מקור (למשל 'USD')
    :param target_currency: מטבע יעד (למשל 'ILS')
    :return: שער חליפין עדכני (float) או ערך קבוע במקרה של כשל
    """
    # Fallback rates (fixed values for common currency pairs)
    fallback_rates = {
        "USD_EUR": 0.92,
        "USD_ILS": 3.75,
        "USD_GBP": 0.79,
        "EUR_USD": 1.09,
        "EUR_ILS": 4.08,
        "EUR_GBP": 0.86,
        "ILS_USD": 0.27,
        "ILS_EUR": 0.24,
        "ILS_GBP": 0.21,
        "GBP_USD": 1.26,
        "GBP_EUR": 1.16,
        "GBP_ILS": 4.75
    }
    
    # Return 1.0 for same currency
    if base_currency == target_currency:
        return 1.0
    
    # Try primary API - exchangerate.host
    try:
        url = f"https://api.exchangerate.host/convert?from={base_currency}&to={target_currency}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            result = data.get('result')
            if result:
                print(f"Got rate from exchangerate.host: {result}")
                return result
    except Exception as e:
        print(f"Primary API error: {e}")
    
    # Try alternate API - exchangeratesapi.io with no API key (limited but works)
    try:
        url = f"https://api.exchangeratesapi.io/latest?base={base_currency}&symbols={target_currency}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            rates = data.get('rates', {})
            result = rates.get(target_currency)
            if result:
                print(f"Got rate from exchangeratesapi.io: {result}")
                return result
    except Exception as e:
        print(f"Secondary API error: {e}")
    
    # Try third API - frankfurter.app
    try:
        url = f"https://api.frankfurter.app/latest?from={base_currency}&to={target_currency}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            rates = data.get('rates', {})
            result = rates.get(target_currency)
            if result:
                print(f"Got rate from frankfurter.app: {result}")
                return result
    except Exception as e:
        print(f"Tertiary API error: {e}")
    
    # If all APIs fail, use fallback rates
    pair_key = f"{base_currency}_{target_currency}"
    if pair_key in fallback_rates:
        print(f"Using fallback rate for {pair_key}: {fallback_rates[pair_key]}")
        return fallback_rates[pair_key]
    
    # Last fallback: returning None will show error in UI
    return None

def forecast_cashflow(df, periods=12):
    """
    חיזוי תזרים מזומנים על בסיס נתונים היסטוריים.
    :param df: DataFrame עם נתוני תזרים (עמודות: 'date', 'amount')
    :param periods: מספר תקופות לחיזוי (חודשים קדימה)
    :return: DataFrame עם תחזית (עמודות: 'date', 'forecast')
    """
    # בדיקה שהעמודות קיימות
    if 'date' not in df.columns or 'amount' not in df.columns:
        raise ValueError("DataFrame חייב לכלול עמודות 'date' ו-'amount'")
    
    # המרת תאריכים ומיון
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # חישוב ממוצע נע
    avg_monthly = df.groupby(df['date'].dt.to_period('M'))['amount'].sum()
    last_6_months_avg = avg_monthly.tail(6).mean()
    print(f"[DEBUG] avg_monthly: {avg_monthly}")
    print(f"[DEBUG] last_6_months_avg: {last_6_months_avg}")
    
    # קו מגמה פשוט - לוקח את השינוי הממוצע לחודש
    if len(avg_monthly) > 1:
        trend = (avg_monthly.iloc[-1] - avg_monthly.iloc[0]) / (len(avg_monthly) - 1)
    else:
        trend = 0
    print(f"[DEBUG] trend: {trend}")
    
    # חיזוי - ממוצע אחרון + מגמה
    last_date = df['date'].max()
    forecast_dates = [last_date + pd.DateOffset(months=i+1) for i in range(periods)]
    forecast_values = [last_6_months_avg + trend * (i+1) for i in range(periods)]
    print(f"[DEBUG] forecast_dates: {forecast_dates}")
    print(f"[DEBUG] forecast_values: {forecast_values}")
    
    # יצירת DataFrame עם התחזית
    result = pd.DataFrame({
        'date': forecast_dates,
        'forecast': forecast_values
    })
    print(f"[DEBUG] result DataFrame:\n{result}")
    
    return result

load_dotenv()
