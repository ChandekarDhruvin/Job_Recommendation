import DB
from bson import ObjectId
import recommendation
import embedding
import data_extraction
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

    resume_embedding = embedding.create_embedding(" ".join(extracted_data["skills"] + extracted_data["location"] + extracted_data["experience"]))
    best_matches = recommendation.find_best_matching_jobs(resume_embedding)
    for match in best_matches:
        match["resume_id"] = resume_id

    recommendation.save_match_scores(user_id,resume_id, best_matches)
    
    return {
        "message": "Resume processed successfully",
        
                "resume_id": resume_id,

        "user_id": user_id,
        "matches": best_matches
    }
