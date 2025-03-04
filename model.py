from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
import spacy



nlp_resume = spacy.load("model-best")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

