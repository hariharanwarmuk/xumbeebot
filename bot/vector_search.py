import os
import faiss
import numpy as np
from openai import OpenAI

# Initialize OpenAI client with your API key from environment variables.
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_embedding(text):
    """
    Obtain the embedding for a given text string using OpenAI's embedding API.
    This function uses the model "text-embedding-3-small".
    """
    response = client.embeddings.create(
        input=text,  # input is provided as a plain string
        model="text-embedding-3-small"
    )
    # Extract the embedding from the response
    embedding = response.data[0].embedding
    print(f"Obtained embedding of shape: {len(embedding)}")
    return np.array(embedding, dtype=np.float32)

def build_kb_index(kb_entries):
    """
    Build a FAISS index from a list of knowledge base entries.
    Each entry in kb_entries is a dict with keys 'question' and 'answer'.
    This function returns the FAISS index along with a mapping list, so that each vector's 
    corresponding KB entry can be retrieved.
    """
    embeddings = []
    mapping = []
    for entry in kb_entries:
        text = entry["question"]
        emb = get_embedding(text)
        embeddings.append(emb)
        mapping.append(entry)
    # Stack embeddings into a 2D numpy array (each row is an embedding)
    embeddings = np.vstack(embeddings)
    dimension = embeddings.shape[1]
    # Create a FAISS index with L2 (Euclidean) distance metric
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    print("index is created", index)
    print("mapping is created", mapping)
    return index, mapping

def search_kb(query, index, mapping, top_k=1):
    """
    Perform a vector search for the query in the provided FAISS index.
    Returns the best matching knowledge base entry (from the mapping list) and the L2 distance.
    If no match is found, returns (None, None).
    """
    query_embedding = get_embedding(query).reshape(1, -1)
    distances, indices = index.search(query_embedding, top_k)
    if indices[0][0] == -1:
        return None, None
    best_index = indices[0][0]
    print("best_index", best_index)
    return mapping[best_index], distances[0][0]
