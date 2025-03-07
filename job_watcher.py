
#=======================================================THIS SCRIPT WILL CREATE THE EMBEDDING OF JOB POSTS IN REAL TIME IF ANY NEW JOB FOUND================================================#

from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from bson import ObjectId
import os
import DB
from pinecone import Pinecone, ServerlessSpec

#  Initialize FastAPI
app = FastAPI()

#  Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["jobPortalDB"]
job_collection = db["jobposts"]

#  Initialize Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY)

#  Define Pinecone Index
INDEX_NAME = "job-posting-embeddings2"

#  Create index if not exists
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,  # Update based on embedding model size
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(name=INDEX_NAME)

#  Load Sentence Embedding Model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

#  Function to process and store job embeddings
def process_and_store_embedding(job_data):
    job_id = str(job_data["_id"])

    try:
        #  Check if embedding already exists in Pinecone
        fetch_response = index.fetch([job_id])
        existing_embedding = fetch_response.vectors  # Fetch embeddings

        if job_id in existing_embedding:
            print(f"🔄 Job {job_id} embedding already exists. Skipping...")
            return

        #  Extract required fields
        description = job_data.get("description", "")
        skills = job_data.get("skills", "")
        location = job_data.get("location", "")
        experience = job_data.get("experience", "")

        #  Create combined text
        combined_text = f"{description} Required Skills: {skills}. Location: {location}. Experience: {experience}."

        #  Generate Embedding
        embedding = embedder.encode(combined_text).tolist()

        #  Save embedding to Pinecone
        index.upsert(vectors=[(job_id, embedding)])
        print(f" Stored job embedding in Pinecone: {job_id}")

    except Exception as e:
        print(f" Error processing job {job_id}: {e}")

#  Store previous embeddings (Run once at startup)
def store_previous_embeddings():
    print(" Storing previous job embeddings in Pinecone...")

    try:
        for job_data in job_collection.find():
            process_and_store_embedding(job_data)

        print(" Finished storing previous embeddings.")

    except Exception as e:
        print(f" Error storing previous embeddings: {e}")

#  Run previous embedding storage at startup
store_previous_embeddings()

#  Monitor new job postings
print("👀 Watching for new job postings...")

with job_collection.watch() as stream:
    for change in stream:
        if change["operationType"] == "insert":
            job_data = change["fullDocument"]
            process_and_store_embedding(job_data)