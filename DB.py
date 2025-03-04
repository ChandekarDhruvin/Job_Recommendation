import os

# ✅ Initialize FastAPI
from pymongo import MongoClient

# ✅ Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["jobPortalDB"]
job_collection = db["jobposts"]
embedding_collection = db["job_posting_embedding"]
resumes_collection = db["resumes"]
matches_collection = db["matches"]
