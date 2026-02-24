import fitz 
import os

def pdf_extract(file_path: str) -> str:
    """
    Extracts all text content from a PDF file located at the given path 
    using PyMuPDF (fitz).
    """
    
    # --- The Key Change: Ensure the path is absolute for reliability ---
    safe_file_path = os.path.abspath(file_path)
    
    # 1. Rule-Based Pre-Check
    if not os.path.exists(safe_file_path):
        return f"ERROR: File not found at path: {safe_file_path}"
    if not safe_file_path.lower().endswith('.pdf'):
        return f"ERROR: File must be a PDF type, received: {safe_file_path}"
        
    all_text = []
    
    try:
        # 2. Open the PDF document using the safe path
        doc = fitz.open(safe_file_path)
        
        # ... (rest of the code remains the same: iteration, extraction, closing)
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text = page.get_text()
            all_text.append(text)
            
        doc.close()
        
        # 5. Concatenate all text with a newline separator
        return "\n".join(all_text)
        
    except fitz.FileDataError:
        return f"ERROR: The file at {safe_file_path} is not a valid or corrupt PDF."
        
    except Exception as e:
        return f"ERROR: An unexpected error occurred during PDF processing: {type(e).__name__} - {e}"