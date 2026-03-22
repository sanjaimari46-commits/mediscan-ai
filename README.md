# 🏥 MediScan AI — Smart Medical Report Analyzer

An AI-powered web application that analyzes blood test reports and provides instant health insights in simple language.

## 🚀 Features
- 📄 Upload blood test PDF reports
- 🤖 AI-powered analysis using Groq AI (LLaMA 3.3)
- ✅ Normal/Abnormal value detection with explanations
- 💊 Personalized health advice
- 🏥 Doctor consultation recommendations

## 🛠️ Tech Stack
- **Backend:** Python, Flask
- **AI:** Groq AI (LLaMA 3.3-70b)
- **PDF Processing:** PyMuPDF, pdfplumber
- **Frontend:** HTML, CSS, JavaScript

## ⚙️ Setup
1. Clone the repo
2. Install dependencies:
```bash
   pip install flask pymupdf pdfplumber pytesseract pillow requests
```
3. Add your Groq API key in `app.py`
4. Run:
```bash
   python app.py
```
5. Open `http://localhost:5000`

## 📌 Note
Currently supports text-based PDF reports.
OCR support for scanned PDFs coming soon.
