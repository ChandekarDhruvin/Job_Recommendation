import requests
import pdfplumber
from io import BytesIO
from docx import Document
import model

def download_resume(file_url):
    """Download and extract text from resume"""
    response = requests.get(file_url)
    if response.status_code == 200:
        file_content = BytesIO(response.content)
        if file_url.endswith(".pdf"):
            return extract_text_from_pdf(file_content)
        elif file_url.endswith(".docx"):
            return extract_text_from_docx(file_content)
    return None

def extract_text_from_pdf(file_content):
    """Extract text from PDF"""
    text = ""
    with pdfplumber.open(file_content) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def extract_text_from_docx(file_content):
    """Extract text from DOCX"""
    doc = Document(file_content)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_resume_details(resume_text):
    """Extract skills, location, and experience from resume text"""
    doc = model.nlp_resume(resume_text)
    return {
        "skills": list(set(ent.text for ent in doc.ents if ent.label_ == "SKILL")),
        "location": list(set(ent.text for ent in doc.ents if ent.label_ == "LOCATION")),
        "experience": list(set(ent.text for ent in doc.ents if ent.label_ == "EXPERIENCE"))
    }