from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import fitz
import pdfplumber
import pytesseract
from PIL import Image
import requests
import json
import io

app = Flask(__name__)
app.secret_key = 'mediscan-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf'}
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def allowed_file(f):
    return '.' in f and f.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(filepath):
    doc = fitz.open(filepath)
    extracted = ""

    for i in range(len(doc)):
        page = doc[i]
        words = page.get_text("words")

        if words:
            page_width = page.rect.width
            col1_end = page_width * 0.35
            col2_end = page_width * 0.55

            rows = {}
            for word in words:
                x, y, x2, y2, word_text = word[0], word[1], word[2], word[3], word[4]
                row_key = round(y / 8) * 8
                if row_key not in rows:
                    rows[row_key] = {"test": [], "result": [], "reference": []}
                if x < col1_end:
                    rows[row_key]["test"].append((x, word_text))
                elif x < col2_end:
                    rows[row_key]["result"].append((x, word_text))
                else:
                    rows[row_key]["reference"].append((x, word_text))

            for row_key in sorted(rows.keys()):
                row = rows[row_key]
                test = " ".join([w[1] for w in sorted(row["test"], key=lambda w: w[0])])
                result = " ".join([w[1] for w in sorted(row["result"], key=lambda w: w[0])])
                reference = " ".join([w[1] for w in sorted(row["reference"], key=lambda w: w[0])])
                if test.strip() or result.strip():
                    extracted += f"{test} | {result} | {reference}\n"
        else:
            return ""  # Image PDF - not supported

    print("Extracted text:\n", extracted[:600])
    return extracted

def analyze_report(text):
    prompt = f"""You are a medical report analyzer. I will give you text extracted from a blood test report row by row.

IMPORTANT INSTRUCTIONS:
- Each row contains words from left to right
- TEST NAME appears first, then RESULT VALUE, then REFERENCE RANGE
- Carefully match each result to its correct test name
- Do NOT mix up values between different tests

Analyze and return ONLY this JSON format, nothing else:
{{
  "summary": "2-3 line simple summary in plain English for a non-medical person",
  "normal": ["TestName: value (normal range: x-y)"],
  "abnormal": ["TestName: value - HIGH/LOW (normal range: x-y, explanation)"],
  "doctor_needed": true or false,
  "advice": "simple practical health advice"
}}

Blood test report text:
{text}

Return ONLY valid JSON. No extra text, no markdown, no backticks."""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": "Bearer YOUR_GROQ_API_KEY",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
    )

    result = response.json()
    print("Groq Response:", result)

    if 'choices' not in result:
        raise Exception("Groq API error: " + str(result))

    content = result['choices'][0]['message']['content'].strip()
    if content.startswith('```'):
        content = content.split('```')[1]
        if content.startswith('json'):
            content = content[4:]

    return json.loads(content)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'report' not in request.files:
        return jsonify({'error': 'No file uploaded'})

    file = request.files['report']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'})

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    extracted = extract_text_from_pdf(filepath)
    if not extracted.strip():
        return jsonify({'error': 'Could not read PDF'})

    result = analyze_report(extracted)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)