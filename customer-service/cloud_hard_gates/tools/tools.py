import os
import logging
from tqdm import tqdm
import chromadb
from sentence_transformers import SentenceTransformer
from typing import Dict, Any, List
from chromadb.config import Settings

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("indexing.log"),
        logging.StreamHandler()
    ]
)

# --- Configuration ---
SOURCE_DIR = "/path/to/your/source/code"        # Update this
CHROMA_DB_DIR = "./chroma_db"
COLLECTION_NAME = "code_index"
MODEL_NAME = "all-MiniLM-L6-v2"

SUPPORTED_EXTENSIONS = {
    ".py", ".java", ".js", ".ts", ".jsx", ".tsx",
    ".html", ".css", ".scss", ".json", ".xml", ".yml", ".yaml",
    ".cpp", ".c", ".h", ".hpp", ".cs", ".php", ".rb", ".go",
    ".swift", ".kt", ".rs", ".sql", ".sh", ".bat", ".ini",
    ".gradle", ".m", ".mm", ".pl", ".r", ".dart"
}

def initialize_chroma():
    logging.info("Initializing ChromaDB client...")
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        logging.info(f"Collection '{COLLECTION_NAME}' already exists. Loading it.")
        collection = client.get_collection(name=COLLECTION_NAME)
    else:
        logging.info(f"Creating new collection: '{COLLECTION_NAME}'")
        collection = client.create_collection(name=COLLECTION_NAME)

    return collection

def load_model():
    logging.info(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    logging.info("Model loaded successfully.")
    return model

def get_source_files(directory):
    logging.info(f"Scanning directory: {directory}")
    code_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1].lower() in SUPPORTED_EXTENSIONS:
                code_files.append(os.path.join(root, file))
    logging.info(f"Found {len(code_files)} source files to index.")
    return code_files

def index_files(file_list, collection, model):
    success_count = 0
    for file_path in tqdm(file_list, desc="Indexing source files"):
        rel_path = os.path.relpath(file_path, SOURCE_DIR)
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if not content.strip():
                logging.warning(f"Skipping empty file: {rel_path}")
                continue

            embedding = model.encode(content)
            collection.add(
                documents=[content],
                embeddings=[embedding.tolist()],
                ids=[rel_path]
            )
            success_count += 1
            logging.info(f"Indexed: {rel_path}")

        except Exception as e:
            logging.error(f"Failed to index {rel_path}: {e}")

    logging.info(f"✅ Indexed {success_count} out of {len(file_list)} files successfully.")

def search_application_context(query: str, collection_name: str = "application_code") -> Dict[str, Any]:
    """
    Searches ChromaDB for application context based on user query.

    Args:
        query (str): The search query to find relevant code context.
        collection_name (str): Name of the ChromaDB collection to search in.

    Returns:
        dict: Search results with relevant code context.

    Example:
        >>> search_application_context("error handling implementation")
        {
            'status': 'success',
            'results': [
                {
                    'file_path': 'src/error_handler.py',
                    'code_snippet': 'def handle_error(error): ...',
                    'relevance_score': 0.85
                }
            ]
        }
    """
    logger.info("Searching application context for query: %s", query)
    
    try:
        # Initialize ChromaDB client with new configuration
        client = chromadb.PersistentClient(path="./chroma_db")
        
        # Get or create the collection
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Search the collection
        results = collection.query(
            query_texts=[query],
            n_results=5  # Return top 5 most relevant results
        )
        
        # Format results
        formatted_results = []
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            formatted_results.append({
                'file_path': metadata.get('file_path', 'unknown'),
                'code_snippet': doc,
                'relevance_score': 1 - distance  # Convert distance to similarity score
            })
        
        return {
            'status': 'success',
            'results': formatted_results
        }
        
    except Exception as e:
        logger.error("Error searching application context: %s", str(e))
        return {
            'status': 'error',
            'error': str(e),
            'results': []
        }

if __name__ == "__main__":
    logging.info("🔍 Starting code indexing script...")
    collection = initialize_chroma()
    model = load_model()
    files_to_index = get_source_files(SOURCE_DIR)
    index_files(files_to_index, collection, model)
    logging.info("🏁 Indexing complete.")
