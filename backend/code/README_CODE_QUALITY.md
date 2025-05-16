# Code Quality Analyzer

This extension to the Codebase Knowledge Builder analyzes code quality focusing on three key areas:

1. **Logging** - Centralizes logging, sensitive data protection, audit trails, correlation IDs, API call logging, log levels, and frontend error logging
2. **Availability** - Retry logic, high availability configurations, timeouts, auto-scaling, throttling/rate limiting, and circuit breaker patterns
3. **Error Handling** - Backend error handling, HTTP error codes, client-side error handling, and error documentation

## Usage

From the `backend/code` directory, run:

```bash
python code_quality_cli.py --dir /path/to/codebase
```

Or to analyze a GitHub repository:

```bash
python code_quality_cli.py --repo https://github.com/username/repo
```

### Command-Line Options

```
--repo URL                 URL of the public GitHub repository
--dir PATH                 Path to local directory
-n, --name NAME            Project name (optional, derived from repo/directory if omitted)
-t, --token TOKEN          GitHub personal access token (optional)
-o, --output DIR           Base directory for output (default: ./output)
-i, --include PATTERN      Include file patterns (e.g. '*.py' '*.js')
-e, --exclude PATTERN      Exclude file patterns (e.g. 'tests/*' 'docs/*')
-s, --max-size SIZE        Maximum file size in bytes (default: 1000000, about 1MB)
--no-cache                 Disable LLM response caching (default: caching enabled)
--focus AREA               Focus area of analysis: "logging", "availability", "error_handling", or "all" (default)
```

### ChromaDB Storage Options

```
--store-db                 Store analysis results in ChromaDB
--app-id ID                Unique ID for the application (generated if not provided)
--app-name NAME            Name of the application (defaults to project name)
--db-dir DIR               Directory for ChromaDB storage (default: ./code_quality_db)
--db-collection NAME       Collection name in ChromaDB (default: code_quality_analyses)
--embedding-model PATH/NAME Path to local embedding model or name of remote model
--meta KEY=VALUE           Additional metadata as key=value pairs
```

## Programmatic API

You can also call the analyzer from your own Python code:

```python
from backend.code import run_quality_analysis

# Run analysis on a local directory
result = run_quality_analysis(
    local_dir="/path/to/codebase",
    focus_areas=["logging", "error_handling"]  # Analyze specific areas
)

# Access the report
report_content = result["report_content"]
report_path = result["report_path"]

# Or analyze a GitHub repository with ChromaDB storage
result = run_quality_analysis(
    repo_url="https://github.com/username/repo",
    github_token="your_token",  # Optional
    focus_areas="all",          # Analyze all areas
    
    # Store in ChromaDB with app metadata
    store_in_chromadb=True,
    app_id="my-app-123",
    app_name="My Application",
    embedding_model_path="/path/to/local/model",  # Use local embedding model
    additional_metadata={"version": "1.0", "environment": "production"}
)

# Access ChromaDB document ID
chromadb_doc_id = result["chromadb_doc_id"]
```

See the `run_quality_analysis` function docstring for all available parameters.

## Output

The analyzer generates a detailed Markdown report with:

1. Executive summary
2. Detailed findings for each selected focus area
3. Code examples from the codebase
4. Recommendations for improvement

The report is saved to `output/<project_name>/code_quality_report.md`.

## Example

To analyze a local codebase focusing only on logging practices:

```bash
python code_quality_cli.py --dir /path/to/codebase --focus logging
```

To analyze a GitHub repo with a focus on all areas, storing results in ChromaDB:

```bash
python code_quality_cli.py --repo https://github.com/username/repo --focus all --store-db --app-id="my-app-123" --app-name="My App" --embedding-model=/path/to/model --meta version=1.0 environment=prod
```

## ChromaDB Integration

The system can store analysis results in ChromaDB for efficient retrieval and semantic search:

1. **Storage** - Reports are automatically chunked and stored with metadata
2. **Retrieval** - Reports can be retrieved by app ID, name, or focus areas
3. **Semantic Search** - Find relevant analyses with natural language queries
4. **Embedding Models** - Support for both local and remote embedding models

### Querying Stored Analyses

```python
from utils.chromadb_storage import CodeQualityStorage

# Initialize storage
storage = CodeQualityStorage(
    persist_directory="code_quality_db",
    embedding_model_path="/path/to/model"  # Optional
)

# Get a specific analysis
result = storage.get_analysis(app_id="my-app-123")

# Query across all analyses
results = storage.query_analyses(
    query_text="How does the error handling handle REST API failures?",
    focus_areas=["error_handling"]
)

# List all apps with stored analyses
apps = storage.get_all_apps()
```

## How It Works

1. The analyzer crawls through the codebase to gather all source files
2. For each selected focus area, it employs an LLM to analyze the code against established best practices
3. It identifies patterns, libraries, and techniques related to each focus area
4. The results are compiled into a comprehensive Markdown report
5. An executive summary is generated to highlight key findings and recommendations
6. Optionally, the analysis is stored in ChromaDB with application metadata

## Architecture

The system is split into three main components:

1. **Code Quality Engine** (`code_quality_engine.py`) - Core logic for analyzing code quality
   - Contains the `CodeQualityAnalyzer` node that performs the actual analysis
   - Integrates with the existing flow-based system

2. **Command Line Interface** (`code_quality_cli.py`) - User-friendly CLI
   - Provides command-line options for running analyses
   - Includes the `run_quality_analysis()` function for programmatic use

3. **ChromaDB Storage** (`utils/chromadb_storage.py`) - Vector database integration
   - Handles storing and retrieving analysis reports
   - Supports semantic search across analyses
   - Manages chunking and metadata

## Customization

You can modify the prompts used for analysis in `utils/validation_prompts.py` to focus on specific aspects or add additional criteria.

## Integration

This tool is designed to work with the existing Codebase Knowledge Builder system, sharing the same workflow architecture but with a different analysis focus. 