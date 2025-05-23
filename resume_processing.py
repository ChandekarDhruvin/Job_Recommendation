import DB
from bson import ObjectId
import recommendation
import embedding
import data_extraction


import os
import torch
import nltk
from nltk.corpus import stopwords
from bson import ObjectId
import data_extraction


# Download stopwords if not already available
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

def process_resume(resume_id, user_id):
    resume_doc = DB.resumes_collection.find_one({"_id": ObjectId(resume_id)})
    if not resume_doc:
        return {"error": "Resume not found"}
    
    resume_text = data_extraction.download_resume(resume_doc["current_file_url"])
    if not resume_text:
        return {"error": "Could not extract text from resume"}
    
    extracted_data = data_extraction.extract_resume_details(resume_text)

    # Debugging: Print extracted data
    print(f"Extracted {len(extracted_data['skills'])} skills: {extracted_data['skills']}")
    print(f"Extracted {len(extracted_data['location'])} locations: {extracted_data['location']}")
    print(f"Extracted {len(extracted_data['experience'])} experience details: {extracted_data['experience']}")

    # Combine extracted data
    combined_text = " ".join(extracted_data["skills"] + extracted_data["location"] + extracted_data["experience"])

    # Remove stop words
    filtered_text = " ".join([word for word in combined_text.split() if word.lower() not in stop_words])

    # Generate embedding
    resume_embedding = embedding.create_embedding(filtered_text)

    # Find best matching jobs
    best_matches = recommendation.find_best_matching_jobs(resume_embedding)
    for match in best_matches:
        match["resume_id"] = resume_id

    # Save match scores
    recommendation.save_match_scores(user_id, resume_id, best_matches)
    
    return {
        "message": "Resume processed successfully",
        "resume_id": resume_id,
        "user_id": user_id,
        "matches": best_matches
    }

