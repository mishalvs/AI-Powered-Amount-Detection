import re
from PIL import Image, ImageOps
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Text Extraction
def extract_text_from_image(file_path: str) -> str:
    image = Image.open(file_path)
    gray = ImageOps.grayscale(image)
    bw = gray.point(lambda x: 0 if x < 160 else 255, '1')
    return pytesseract.image_to_string(bw)

def extract_text_from_input(text=None, file=None):
    if text:
        return text
    if file:
        return extract_text_from_image(file)
    return None
    
# Number Normalization
def normalize_number(token: str):
    token = token.replace("l", "1").replace("O", "0")
    token = token.replace(",", "").replace("..", ".")
    token = re.sub(r"[^\d]", "", token)
    return int(token) if token.isdigit() else None

def extract_numeric_tokens(text: str):
    pattern = r"\b[\d,\.lO]+\b|\b[\d,]+%\b"
    return re.findall(pattern, text)

def get_normalized_amounts(text: str):
    raw_tokens = extract_numeric_tokens(text)
    normalized = []
    for token in raw_tokens:
        if "%" in token:
            continue
        value = normalize_number(token)
        if value is not None:
            normalized.append(value)
    return raw_tokens, normalized

# Context Classification
def classify_amounts(text: str):
    original_text = text
    text_lower = text.lower().replace("t0tal", "total").replace("pald", "paid").replace("tota1", "total")
    
    mapping = [("total", "total_bill"), ("paid", "paid"), ("due", "due")]
    amounts = []

    for key, label in mapping:
        pattern = rf"{key}[:\s]*(?:[A-Za-z₹$]*\s*)?([0-9lO,\.]+)"
        match = re.search(pattern, text_lower)
        if match:
            value = normalize_number(match.group(1))
            if value is not None:
                source_pattern = rf"{key}[:\s]*(?:[A-Za-z₹$]*\s*)?[0-9lO,\.]+"
                source_match = re.search(source_pattern, original_text, re.IGNORECASE)
                source_text = source_match.group(0) if source_match else match.group(0)
                amounts.append({
                    "type": label,
                    "value": value,
                    "source": f"text: '{source_text.strip()}'"
                })

    if not amounts:
        return {"status": "no_amounts_found", "reason": "document too noisy"}
    return {"amounts": amounts, "status": "ok"}

# Full Pipeline
def extract_amounts_pipeline(text=None, file=None, currency="INR"):
    extracted_text = extract_text_from_input(text=text, file=file)
    if not extracted_text:
        return {"status": "no_amounts_found", "reason": "document too noisy"}

    raw_tokens, normalized = get_normalized_amounts(extracted_text)
    if not raw_tokens:
        return {"status": "no_amounts_found", "reason": "document too noisy"}

    step_1 = {"raw_tokens": raw_tokens, "currency_hint": currency, "confidence": 0.70}
    step_2 = {"normalized_amounts": normalized, "normalization_confidence": 0.82}

    classification = classify_amounts(extracted_text)
    if classification.get("status") != "ok":
        return classification
    step_3 = {"amounts": classification["amounts"], "confidence": 0.80}

    final_output = {"currency": currency, "amounts": classification["amounts"], "status": "ok"}

    return {
        "step_1_ocr": step_1,
        "step_2_normalization": step_2,
        "step_3_classification": step_3,
        "final_output": final_output
    }
