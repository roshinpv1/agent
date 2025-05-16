import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import chromadb
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === CONFIGURATION ===

APPLICATION_FOLDER = "/Users/roshinpv/Documents/Projects/wiremock"  # <<<--- Update this
CHROMA_DB_DIR = "chromadb_store"
COLLECTION_NAME = "application_index"
MODEL_NAME = "all-MiniLM-L6-v2"
# Point this to your existing local model directory
LOCAL_MODEL_DIR = "/Users/roshinpv/.cache/torch/sentence_transformers"  # Update this to your local model path


# === RUN MAIN ===
if __name__ == "__main__":
   
    client = chromadb.PersistentClient(path="chromadb_store")
    collection = client.get_or_create_collection(
        name="application_index",
        metadata={"hnsw:space": "cosine"}
    )
        # Get or create the collection
    
        
        # Search the collection
    results = collection.query(
        query_texts=["how application logging is done consider the javascript files onlyclear"],
        n_results=2  # Return top 5 most relevant results
    )

    print (results)
