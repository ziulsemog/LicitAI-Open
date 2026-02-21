import fitz  # PyMuPDF
import easyocr
import io
import httpx

def extract_text_from_url(url: str) -> str:
    if not url:
        return ""
    try:
        response = httpx.get(url, timeout=30.0)
        response.raise_for_status()
        pdf_bytes = response.content
        return extract_text_from_pdf_bytes(pdf_bytes)
    except Exception as e:
        print(f"Error fetching PDF from {url}: {e}")
        return ""

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    text = ""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text("text") + "\n"
        
        # Fallback to OCR if text is empty or very short
        if len(text.strip()) < 50:
            print("Text extraction yielded little to no text. Falling back to OCR.")
            text = extract_text_with_ocr(pdf_bytes)
    except Exception as e:
        print(f"Error during PDF extraction: {e}")
        text = extract_text_with_ocr(pdf_bytes)
        
    return text

def extract_text_with_ocr(pdf_bytes: bytes) -> str:
    try:
        # Convert first pages to images using PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        # Ensure we only instantiate Reader once ideally, but here for simplicity
        reader = easyocr.Reader(['pt'])
        text = ""
        # OCR only first 3 pages to save time/compute
        for i in range(min(3, len(doc))): 
            page = doc[i]
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            results = reader.readtext(img_bytes, detail=0)
            text += " ".join(results) + "\n"
        return text
    except Exception as e:
        print(f"Error during OCR: {e}")
        return ""
