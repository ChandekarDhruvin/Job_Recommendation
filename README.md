# 🏆 Job Matching System

## 🚀 Overview
The Job Matching System is an AI-powered platform that processes resumes, extracts relevant details, generates embeddings, and matches candidates with the most suitable job postings using MongoDB and Pinecone.

## ✨ Features
✅ Resume extraction from PDFs and DOCX files.  
✅ Named Entity Recognition (NER) to extract skills, location, and experience.  
✅ Embedding generation for job postings and resumes.  
✅ Job matching using **Pinecone-based similarity search**.  
✅ **MongoDB integration** for storing resumes, jobs, and matches.  
✅ RESTful API for **resume processing & job matching**.  
✅ **OCR support** for extracting text from scanned resumes.  
✅ **Real-time job alerts** for candidates.  

## 🛠️ Technologies Used
- **FastAPI** - API development.
- **MongoDB** - Database storage.
- **Pinecone** - Vector database for similarity search.
- **SentenceTransformers** - Embedding generation.
- **spaCy** - NER-based resume processing.
- **pdfplumber & python-docx** - Resume text extraction.
- **PyTorch** - Cosine similarity computation.
- **Requests** - Resume file download handling.
- **Tesseract OCR** - Optical Character Recognition for scanned resumes.

---

## 📂 Project Structure
```
📂 Job Matching System
├── 📜 `data_extraction.py` - Extracts text from resumes (PDF, DOCX, OCR for scanned documents) & performs NER.
├── 🛢 `DB.py` - Manages MongoDB connections & collections.
├── 🧠 `embedding.py` - Generates embeddings for resumes & job descriptions.
├── 🔍 `job_watcher.py` - Monitors job postings for real-time recommendations.
├── 🚀 `main.py` - Runs the FastAPI server for processing resumes & matching jobs.
├── 🤖 `model.py` - Loads NLP & embedding models (`SentenceTransformer`).
├── 🎯 `recommendation.py` - Finds best job matches using MongoDB & Pinecone.
├── 📑 `resume_processing.py` - Handles resume parsing & job matching logic.
├── 📝 `ocr_resume.py` - Extracts text from scanned resumes using **Tesseract OCR**.
├── 🔄 `ocr_process_resume.py` - Handles OCR-based resume text extraction workflow.
├── 📊 `ocr_resume_extraction.py` - Improves OCR accuracy & text processing for resumes.
```

---

## 📦 Installation & Setup
### 🛠 Prerequisites
Ensure you have the following installed:
✅ Python 3.8+  
✅ MongoDB  
✅ Pinecone API access  
✅ Tesseract OCR (for scanned resumes)  

### 📝 Step 1: Clone the Repository
```sh
git clone https://github.com/ChandekarDhruvin/Job_Recommendation.git
cd job-matching-system
```

### 📌 Step 2: Install Dependencies
```sh
pip install -r requirements.txt
```

### 🔑 Step 3: Set Up Environment Variables
Create a `.env` file and add the following:
```
MONGO_URI=<your-mongodb-uri>
PINECONE_API_KEY=<your-pinecone-api-key>
OCR_PATH=<path-to-tesseract-ocr>
```

### 🚀 Step 4: Run the FastAPI Server
```sh
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

---

## 📡 API Endpoints
### 📝 Process Resume
**Endpoint:** `GET /process_resume`  
**Parameters:**  
- `resume_id` (string) - Resume document ID
- `user_id` (string) - User ID

**Response:**
```json
{
  "resume_id": "123",
  "user_id": "456",
  "top_10_matches": [
    { "job_id": "job123", "score": 87.5 },
    { "job_id": "job456", "score": 82.3 }
  ]
}
```

---

## 🔍 How It Works
1. **Resume Upload & Extraction:**
   - Downloads the resume from a given URL.
   - Extracts text from PDF/DOCX.
   - Uses OCR for scanned resumes.
   - Uses an NLP model to extract skills, experience, and location.

2. **Embedding Generation:**
   - Converts job descriptions and resumes into embeddings using SentenceTransformer.

3. **Job Matching:**
   - Finds the **top 10 best-matching jobs** using cosine similarity.
   - Stores the results in MongoDB.

4. **API Response:**
   - Returns the top job matches instantly.
   - Saves the full job match results asynchronously.

---

## 🔮 Future Enhancements
- 📌 Support for more file formats (TXT, RTF).  
- 📌 Implement **real-time job posting recommendations**.  
- 📌 Improve NLP model for **better skill extraction**.  
- 📌 Enhance OCR processing for **multi-page scanned documents**.  

---

## 👨‍💻 Contributors
- **Chandekar Dhruvin** - AI/ML Engineer
- **Tirth Sutariya** - AI/ML Engineer
- **Wappnet Systems Pvt Ltd**
