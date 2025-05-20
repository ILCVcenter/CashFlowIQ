import sys
import PyPDF2
import openai
import os
import json

# חילוץ טקסט מ-PDF

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# ניתוח חוזה עם GPT

def analyze_contract(text, openai_api_key=None, model="gpt-4"):
    if openai_api_key:
        openai.api_key = openai_api_key
    
    system_prompt = (
        "אתה עוזר פיננסי. נתח את החוזה והוצא סעיפים חשובים, סכומים, תאריכים, סיכונים והתחייבויות. החזר תמיד JSON."
    )
    user_prompt = (
        "Extract the following financial terms from the contract text: "
        "1. Payment amounts\n2. Payment dates\n3. Payment terms\n4. Penalties\n5. Contract period\n"
        "Return the result as a JSON object with these fields.\n\n" + text[:3000]
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
        # ניקוי פלט שלפעמים מכיל תווים מיותרים
        if result.startswith("```json"):
            result = result.replace("```json", "").replace("```", "").strip()
        return result
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return json.dumps({
            "error": "Failed to parse response",
            "raw_response": str(e)
        })
