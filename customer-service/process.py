import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import chromadb
from chromadb.config import Settings

# === CONFIGURATION ===
APPLICATION_FOLDER = "path/to/your/applications"  # <<<--- Update this
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
client = chromadb.Client(Settings(
    persist_directory=CHROMA_DB_DIR,
    chroma_db_impl="duckdb+parquet"
))
model = SentenceTransformer("all-MiniLM-L6-v2")

# === GET OR CREATE COLLECTION ===
existing_collections = [col.name for col in client.list_collections()]
if COLLECTION_NAME in existing_collections:
    collection = client.get_collection(name=COLLECTION_NAME)
else:
    collection = client.create_collection(name=COLLECTION_NAME)

# === READ FILE CONTENT ===
def read_file(file_path: Path) -> str | None:
    try:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"[WARN] Cannot read {file_path}: {e}")
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
    print(f"[INFO] Found {len(files)} eligible files to index.")

    existing_ids = set(collection.get(ids=None)["ids"])  # all current doc ids

    new_documents, new_embeddings, new_ids, new_metadatas = [], [], [], []

    doc_id = len(existing_ids)

    for i in tqdm(range(0, len(files), BATCH_SIZE), desc="Indexing files"):
        batch = files[i:i + BATCH_SIZE]

        texts = []
        valid_paths = []

        for file_path in batch:
            content = read_file(file_path)
            if content and len(content.strip()) > 20:  # skip tiny or empty files
                doc_identifier = f"doc_{hash(file_path)}"
                if doc_identifier not in existing_ids:
                    texts.append(content)
                    valid_paths.append(file_path)

        if texts:
            embeddings = model.encode(texts)
            for content, emb, path in zip(texts, embeddings, valid_paths):
                doc_identifier = f"doc_{hash(path)}"
                new_documents.append(content)
                new_embeddings.append(emb)
                new_ids.append(doc_identifier)
                new_metadatas.append({"file_path": str(path)})

            collection.add(
                documents=new_documents,
                embeddings=new_embeddings,
                ids=new_ids,
                metadatas=new_metadatas
            )

            new_documents.clear()
            new_embeddings.clear()
            new_ids.clear()
            new_metadatas.clear()

    client.persist()
    print("[DONE] Indexing complete and persisted to disk.")

# === RUN MAIN ===
if __name__ == "__main__":
    if not Path(APPLICATION_FOLDER).exists():
        print(f"[ERROR] Application folder does not exist: {APPLICATION_FOLDER}")
    else:
        index_files()
