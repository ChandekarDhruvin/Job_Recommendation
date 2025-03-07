
import DB 
import torch
from bson import ObjectId

#===================================USING MONGODB===========================================#


# def find_best_matching_jobs(resume_embedding):
#     """Find the top 10 best matching jobs using cosine similarity"""
#     job_posts = DB.embedding_collection.find({})
#     best_match = []
#     for job in job_posts:
#         job_id = job["job_id"]
#         job_embedding = torch.tensor(job["embedding"])
#         similarity_score = torch.nn.functional.cosine_similarity(resume_embedding, job_embedding, dim=0).item()
#         percentage_score = ((similarity_score + 1) / 2) * 100
#         best_match.append({"job_id": job_id, "score": round(percentage_score, 2)})
    

#     return sorted(best_match, key=lambda x: x["score"], reverse=True)[:10]


#===================================USING PINECONE===========================================#

import os
import torch
from pinecone import Pinecone

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY)

#  Pinecone Index Name
INDEX_NAME = "job-posting-embeddings2"
index = pc.Index(name=INDEX_NAME)


def find_best_matching_jobs(resume_embedding):
    """Find the top 10 best matching jobs using cosine similarity with Pinecone"""
    if isinstance(resume_embedding, torch.Tensor):
        resume_embedding = resume_embedding.tolist()  # Convert tensor to list
    
    # Query Pinecone for the top 50 closest job embeddings
    results = index.query(vector=resume_embedding, top_k=50, include_values=True, include_metadata=True)

    best_match = []
    
    # Compute cosine similarity manually using PyTorch
    for match in results["matches"]:
        job_id = match["id"]
        job_embedding = torch.tensor(match["values"])  # Convert job embedding to tensor
        resume_tensor = torch.tensor(resume_embedding)  # Convert resume embedding to tensor

        # Compute cosine similarity
        similarity_score = torch.nn.functional.cosine_similarity(resume_tensor, job_embedding, dim=0).item()
        percentage_score = ((similarity_score + 1) / 2) * 100  # Convert to percentage

        best_match.append({"job_id": job_id, "score": round(percentage_score, 2)})

    # Return the top 10 best matches sorted by similarity score
    return sorted(best_match, key=lambda x: x["score"], reverse=True)[:10]



#=============================SAVING THE MATCH SCORE TO MONGODB============================#

def save_match_scores(user_id, resume_id,matches):
    """Save job match scores in the database"""
    print(f"Saving {len(matches)} job matches for user: {user_id}")  # Debugging
    
    for match in matches:
        try:
            job_details = DB.job_collection.find_one({"_id": ObjectId(match['job_id'])})
            if job_details:
                match_entry = {
                    "user_id": user_id,
                    "job_id": ObjectId(match['job_id']),
                      "resume_id":ObjectId(resume_id),  # Ensure ObjectId conversion
                    "score": match["score"]
                }
                result = DB.matches_collection.insert_one(match_entry)  # Insert into MongoDB
                print(f"Inserted match with ID: {result.inserted_id}")  # Debugging
            else:
                print(f"Job ID {match['job_id']} not found in job_postings_collection")
        except Exception as e:
            print(f"Error saving match: {e}")