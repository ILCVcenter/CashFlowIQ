import sys
import PyPDF2
import openai
import os
import json
import re
from dotenv import load_dotenv

# חילוץ טקסט מ-PDF

def extract_text_from_pdf(pdf_file):
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
    מקבל טקסט חוזה ושאלה חופשית, מחזיר תשובה חופשית מה-AI.
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

load_dotenv()
