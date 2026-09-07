import os
from io import BytesIO
import PyPDF2
import docx2txt

def extract_text_from_file(filename: str, content: bytes) -> str:
    ext = os.path.splitext(filename)[1].lower()
    text = ""
    
    if ext == ".pdf":
        try:
            reader = PyPDF2.PdfReader(BytesIO(content))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            raise ValueError(f"Error reading PDF: {e}")
            
    elif ext in [".docx", ".doc"]:
        try:
            text = docx2txt.process(BytesIO(content))
        except Exception as e:
            raise ValueError(f"Error reading DOCX: {e}")
            
    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")
        
    return text.strip()
