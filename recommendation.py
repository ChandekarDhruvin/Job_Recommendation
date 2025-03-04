
import DB 
import torch
from bson import ObjectId



def find_best_matching_jobs(resume_embedding):
    """Find the top 10 best matching jobs using cosine similarity"""
    job_posts = DB.embedding_collection.find({})
    best_match = []
    for job in job_posts:
        job_id = job["job_id"]
        job_embedding = torch.tensor(job["embedding"])
        similarity_score = torch.nn.functional.cosine_similarity(resume_embedding, job_embedding, dim=0).item()
        percentage_score = ((similarity_score + 1) / 2) * 100
        best_match.append({"job_id": job_id, "score": round(percentage_score, 2)})
    
    return sorted(best_match, key=lambda x: x["score"], reverse=True)[:10]


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