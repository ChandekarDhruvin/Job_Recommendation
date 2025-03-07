import data_extraction
import embedding
import recommendation
from bson import ObjectId
import DB

def process_resume(resume_id, user_id, extracted_text):
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

    # If no skills, experience, or location are extracted, use extracted_text
    if not extracted_data['skills'] and not extracted_data['experience'] and not extracted_data['location']:
        combined_data = extracted_text if isinstance(extracted_text, str) else " "
        
    else:
        combined_data = " ".join(extracted_data["skills"] + extracted_data["location"] + extracted_data["experience"])

    resume_embedding = embedding.create_embedding(combined_data)
    best_matches = recommendation.find_best_matching_jobs(resume_embedding)

    for match in best_matches:
        match["resume_id"] = resume_id

    recommendation.save_match_scores(user_id, resume_id, best_matches)

    return {
        "message": "Resume processed successfully",
        "resume_id": resume_id,
        "user_id": user_id,
        "matches": best_matches
    }


