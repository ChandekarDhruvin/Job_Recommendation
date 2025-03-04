

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pymongo import MongoClient
import os
import DB
import model
import resume_processing
import uvicorn
from pinecone import Pinecone

# Initialize FastAPI
app = FastAPI()

#  MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MongoDB URI is missing! Set MONGO_URI in environment variables.")

client = MongoClient(MONGO_URI)
db = DB.client

#  Collections
resumes_collection = DB.resumes_collection
job_postings_collection = DB.job_collection
matches_collection = DB.matches_collection  # Stores matches

# Initialize Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY)

#  Pinecone Index Name
INDEX_NAME = "job-posting-embeddings2"
index = pc.Index(name=INDEX_NAME)

#  Load NLP & Embedding Models
nlp = model.nlp_resume
embedder = model.embedder


def store_resume_matches(resume_id, user_id, full_results):
    """Background task: Stores all job matches in MongoDB asynchronously"""
    try:
        matches_collection.insert_one({
            "resume_id": resume_id,
            "user_id": user_id,
            "matches": full_results
        })
    except Exception as e:
        print(f" Error storing matches: {e}")


@app.get("/process_resume")
def api_process_resume(resume_id: str, user_id: str, background_tasks: BackgroundTasks):
    """API endpoint to process resume and return job matches"""
    try:
        # 🔹 Get all job matches
        all_matches = resume_processing.process_resume(resume_id, user_id)

        # Ensure all_matches is in the correct format
        if isinstance(all_matches, dict):
            if "matches" in all_matches and isinstance(all_matches["matches"], list):
                job_list = all_matches["matches"]  # Extract list from dictionary
            else:
                raise HTTPException(status_code=500, detail="Invalid 'matches' key in response.")
        elif isinstance(all_matches, list):  # If already a list
            job_list = all_matches
        else:
            raise HTTPException(status_code=500, detail=f"Unexpected response format: {type(all_matches)}")

        if not job_list:
            return {
                "resume_id": resume_id,
                "user_id": user_id,
                "message": "No job matches found."
            }

        # 🔹 Return only the top 10 job matches instantly
        top_10_matches = [
            {"job_id": match["job_id"], "score": match["score"]}
            for match in job_list[:10]
        ]

        # 🔹 Store all matches in the background
        background_tasks.add_task(store_resume_matches, resume_id, user_id, job_list)

        return {
            "resume_id": resume_id,
            "user_id": user_id,
            "top_10_matches": top_10_matches
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
