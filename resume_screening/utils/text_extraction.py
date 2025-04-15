import pdfplumber
from docx import Document
from pathlib import Path

# extracting from pdf
def extract_from_pdf(file_path):
    text = ''
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

# extracting from docx
def extract_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs]).strip()

# extracting from txt
def extract_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()
    
# extracting by file type    
def extract_text(file_path):
    try:
        file_type = Path(file_path).suffix.lower()  
        
        if file_type == ".pdf":
            return extract_from_pdf(file_path)
        elif file_type == ".docx":
            return extract_from_docx(file_path)
        elif file_type == ".txt":
            return extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None
    