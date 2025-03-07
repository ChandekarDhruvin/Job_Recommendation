#==========================================THIS WILL MANAGE THE IMAGE DATA WHERE WE USE OCR TO EXTRACT THE DATA======================================================#

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pymongo import MongoClient
import os
import DB
import model
import resume_processing
import uvicorn
from pinecone import Pinecone
import traceback
import pytesseract
from pdf2image import convert_from_path
from bson import ObjectId
import data_extraction
import requests
import tempfile
import docx
import ocr_process_resume as ocr_process_resume

import pytesseract
# os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"
# Set the correct tessdata prefix
# os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/5/tessdata"

# # Set the Tesseract executable path
# pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize FastAPI
app = FastAPI()

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MongoDB URI is missing! Set MONGO_URI in environment variables.")

client = MongoClient(MONGO_URI)
db = DB.client

# Collections
resumes_collection = DB.resumes_collection
job_postings_collection = DB.job_collection
matches_collection = DB.matches_collection  # Stores matches

# Initialize Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise ValueError("Pinecone API Key is missing! Set PINECONE_API_KEY in environment variables.")

pc = Pinecone(api_key=PINECONE_API_KEY)
INDEX_NAME = "job-posting-embeddings2"

# Ensure Pinecone index is initialized
try:
    index = pc.Index(name=INDEX_NAME)
except Exception as e:
    raise ValueError(f"Failed to initialize Pinecone index: {e}")

# Load NLP & Embedding Models
nlp = model.nlp_resume
embedder = model.embedder


def store_resume_matches(resume_id, user_id, full_results):
    """Stores job matches asynchronously in MongoDB"""
    try:
        if not full_results:
            print(f"[INFO] No matches found for resume {resume_id}.")
            return

        matches_collection.insert_one({
            "resume_id": resume_id,
            "user_id": user_id,
            "matches": full_results
        })
        print(f"[INFO] Stored {len(full_results)} matches for resume {resume_id}.")
    except Exception as e:
        print(f"[ERROR] Failed to store matches: {e}")


def extract_text_with_ocr(pdf_path):
    """Extracts text from a resume PDF using OCR"""
    try:
        images = convert_from_path(pdf_path)
        extracted_text = " ".join([pytesseract.image_to_string(img) for img in images])
        return extracted_text.strip()
    except Exception as e:
        print(f"[ERROR] OCR Extraction Failed: {e}")
        return None


def download_file(file_url):
    """Download file from a remote source and save locally."""
    try:
        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_url)[-1])
            for chunk in response.iter_content(1024):
                temp_file.write(chunk)
            temp_file.close()
            return temp_file.name  # Return local file path
        else:
            print(f"[ERROR] Failed to download file: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] File download error: {e}")
    return None


def extract_text(file_path):
    """Extract text from PDF, DOCX, or image files."""
    try:
        extracted_text = ""
        if file_path.lower().endswith(".pdf"):
            extracted_text = extract_text_with_ocr(file_path)
        elif file_path.lower().endswith(".docx"):
            doc = docx.Document(file_path)
            extracted_text = "\n".join([para.text for para in doc.paragraphs])
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            extracted_text = pytesseract.image_to_string(file_path)
        else:
            print(f"[ERROR] Unsupported file type: {file_path}")
            return None

        return extracted_text.strip() if extracted_text else None
    except Exception as e:
        print(f"[ERROR] Text extraction failed: {e}")
        return None




@app.get("/process_resume")
def api_process_resume(resume_id: str, user_id: str, background_tasks: BackgroundTasks):
    try:
        if not resume_id or not user_id:
            raise HTTPException(status_code=400, detail="Resume ID and User ID are required.")

        # Retrieve resume document
        resume_doc = resumes_collection.find_one({"_id": ObjectId(resume_id)})
        if not resume_doc or "current_file_url" not in resume_doc:
            raise HTTPException(status_code=404, detail="Resume file URL not found.")

        # Download the resume file
        local_file_path = download_file(resume_doc["current_file_url"])
        if not local_file_path:
            raise HTTPException(status_code=500, detail="Failed to download resume file.")

        # Extract text using OCR
        extracted_text = extract_text(local_file_path)

        # Debugging: Log extracted text
        print(f"[DEBUG] Extracted text (first 500 chars): {extracted_text[:500]}")

        if not extracted_text or len(extracted_text.strip()) < 10:
            raise HTTPException(status_code=500, detail="OCR failed to extract meaningful text from resume.")

        # Process the resume with extracted text
        all_matches = ocr_process_resume.process_resume(resume_id, user_id,extracted_text)

        if not all_matches or "matches" not in all_matches:
            return {
                "resume_id": resume_id,
                "user_id": user_id,
                "message": "No job matches found."
            }

        # Get top 10 job matches
        top_10_matches = [{"job_id": match["job_id"], "score": match["score"]} for match in all_matches["matches"][:10]]

        # Store matches asynchronously
        background_tasks.add_task(store_resume_matches, resume_id, user_id, all_matches["matches"])

        return {
            "resume_id": resume_id,
            "user_id": user_id,
            "top_10_matches": top_10_matches
        }

    except HTTPException as he:
        raise he  # Pass HTTP exceptions directly
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
