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

ALLOWED_EXTENSIONS = {
    ".py", ".java", ".js", ".ts", ".html", ".css", ".cpp", ".c", ".cs",
    ".go", ".rb", ".php", ".xml", ".json", ".yaml", ".yml", ".sh", ".sql",
    ".swift", ".kt", ".rs", ".scala", ".ini", ".cfg", ".env", ".pl", ".r",
    ".ipynb", ".bat", ".toml", ".gradle", ".txt", ".md"
}
SPECIAL_FILENAMES = {"makefile", "dockerfile"}  # Case-insensitive

BATCH_SIZE = 32  # Number of files to embed per batch for efficiency

# === INIT CHROMADB AND EMBEDDINGS MODEL ===
client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
model = SentenceTransformer("all-MiniLM-L6-v2")

# === GET OR CREATE COLLECTION ===
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)

# === READ FILE CONTENT ===
def read_file(file_path: Path) -> str | None:
    try:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        logger.warning(f"Cannot read {file_path}: {e}")
        return None

# === RECURSIVE FILE DISCOVERY ===
def discover_files(base_path: str) -> list[Path]:
    result = []
    for root, _, files in os.walk(base_path):
        for file in files:
            file_path = Path(root) / file
            ext = file_path.suffix.lower()
            if ext in ALLOWED_EXTENSIONS or file_path.name.lower() in SPECIAL_FILENAMES:
                result.append(file_path)
    return result

# === MAIN INDEXING FUNCTION ===
def index_files():
    files = discover_files(APPLICATION_FOLDER)
    logger.info(f"Found {len(files)} eligible files to index.")

    # Get existing IDs from collection
    try:
        existing_ids = set(collection.get()["ids"])
    except:
        existing_ids = set()

    new_documents, new_ids, new_metadatas = [], [], []
    processed = 0

    for i in tqdm(range(0, len(files), BATCH_SIZE), desc="Indexing files"):
        batch = files[i:i + BATCH_SIZE]

        for file_path in batch:
            content = read_file(file_path)
            if content and len(content.strip()) > 20:  # skip tiny or empty files
                doc_identifier = f"doc_{hash(file_path)}"
                if doc_identifier not in existing_ids:
                    new_documents.append(content)
                    new_ids.append(doc_identifier)
                    new_metadatas.append({"file_path": str(file_path)})
                    processed += 1

        if new_documents:
            try:
                collection.add(
                    documents=new_documents,
                    ids=new_ids,
                    metadatas=new_metadatas
                )
                logger.info(f"Added batch of {len(new_documents)} documents")
                new_documents.clear()
                new_ids.clear()
                new_metadatas.clear()
            except Exception as e:
                logger.error(f"Error adding documents: {e}")

    logger.info(f"Indexing complete. Processed {processed} new files.")

# === RUN MAIN ===
if __name__ == "__main__":
    if not Path(APPLICATION_FOLDER).exists():
        logger.error(f"Application folder does not exist: {APPLICATION_FOLDER}")
    else:
        logger.info("Starting indexing process...")
        index_files()
        logger.info("Indexing completed successfully.")
