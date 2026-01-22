# AI-Powered Amount Detection in Medical Documents

## Project Overview
This project implements a backend service that extracts financial amounts from medical bills or receipts (typed or scanned). The service handles OCR errors, numeric normalization, and context classification to produce structured JSON output with provenance for each amount.

It supports:
- Text input (`text` field)  
- Image input (`file` field) via OCR  
- Automatic normalization and labeling of `total_bill`, `paid`, and `due` amounts  
- Guardrails for noisy documents  

---

## Features
- **OCR/Text Extraction**: Handles scanned, crumpled, or partially visible bills.  
- **Numeric Normalization**: Corrects common OCR errors (`l` → `1`, `O` → `0`) and maps to integers.  
- **Context Classification**: Labels amounts using surrounding text (`total_bill`, `paid`, `due`).  
- **JSON Output**: Provides structured output with provenance and confidence scores.  
- **Error Handling**: Returns informative messages for noisy or invalid documents.  

---

## Tech Stack
- Python 3.11  
- FastAPI  
- Pydantic for request validation  
- Pillow (PIL) for image processing  
- Pytesseract for OCR  
- ngrok (optional) for public API demo  

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mishalvs/AI-Powered-Amount-Detection.git
cd AI-Powered-Amount-Detection
Create a virtual environment:

python -m venv venv
Activate the virtual environment:

Windows (PowerShell):

& ".\venv\Scripts\Activate.ps1"
Windows (cmd):

venv\Scripts\activate.bat
Linux / macOS:

source venv/bin/activate
Install dependencies:

pip install -r requirements.txt
Ensure Tesseract OCR is installed:

Download from: https://github.com/tesseract-ocr/tesseract

Set the path in utils.py:

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
Running the API
Start the FastAPI server:

uvicorn main:app --reload
API will be available at:

http://127.0.0.1:8000
Swagger UI for testing:

http://127.0.0.1:8000/docs
API Endpoints
Health Check
GET /health
Response:

{"status":"ok"}
Extract Amounts
POST /extract-amounts
Accepts multipart/form-data with optional fields:

text (string) — raw bill text

file (binary) — bill image (jpg/png)

Sample Request using PowerShell:

Invoke-WebRequest `
  -Uri http://127.0.0.1:8000/extract-amounts `
  -Method POST `
  -Form @{ text = "Total: INR 1200 | Paid: 1000 | Due: 200" }
Sample Response:

{
  "step_1_ocr": {
    "raw_tokens": ["1200", "1000", "200"],
    "currency_hint": "INR",
    "confidence": 0.7
  },
  "step_2_normalization": {
    "normalized_amounts": [1200, 1000, 200],
    "normalization_confidence": 0.82
  },
  "step_3_classification": {
    "amounts": [
      {"type": "total_bill", "value": 1200, "source": "text: 'Total: INR 1200'"},
      {"type": "paid", "value": 1000, "source": "text: 'Paid: 1000'"},
      {"type": "due", "value": 200, "source": "text: 'Due: 200'"}
    ],
    "confidence": 0.8
  },
  "final_output": {
    "currency": "INR",
    "amounts": [
      {"type": "total_bill", "value": 1200, "source": "text: 'Total: INR 1200'"},
      {"type": "paid", "value": 1000, "source": "text: 'Paid: 1000'"},
      {"type": "due", "value": 200, "source": "text: 'Due: 200'"}
    ],
    "status": "ok"
  }
}
Notes
Always keep the terminal running if testing locally with ngrok.

Use clean, high-contrast images for better OCR results.

Guardrails will return:

{"status":"no_amounts_found","reason":"document too noisy"}
