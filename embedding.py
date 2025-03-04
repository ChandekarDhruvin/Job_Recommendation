import model
def create_embedding(text_data):
    """Generate embedding for the given text"""
    return model.embedder.encode(text_data, convert_to_tensor=True)
