#!/usr/bin/env python
"""
Command line script to analyze code quality focusing on logging, availability, and error handling.
This script leverages the existing codebase structure but focuses on generating quality reports.
"""

import argparse
import os
import sys
import uuid
from code_quality_engine import create_quality_analysis_flow
from utils.chromadb_storage import CodeQualityStorage

# Default file patterns
DEFAULT_INCLUDE_PATTERNS = {
    "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", "*.pyi", "*.pyx",
    "*.c", "*.cc", "*.cpp", "*.h", "*.md", "*.rst", "Dockerfile",
    "Makefile", "*.yaml", "*.yml", "config/*", "*.json", "*.properties", "*.xml"
}

DEFAULT_EXCLUDE_PATTERNS = {
    "assets/*", "data/*", "examples/*", "images/*", "public/*", "static/*", "temp/*",
    "docs/*", 
    "venv/*", ".venv/*", "*test*", "tests/*", "docs/*", "examples/*", "v1/*",
    "dist/*", "build/*", "experimental/*", "deprecated/*", "misc/*", 
    "legacy/*", ".git/*", ".github/*", ".next/*", ".vscode/*", "obj/*", "bin/*", "node_modules/*", "*.log"
}

def run_quality_analysis(
    repo_url=None, 
    local_dir=None, 
    project_name=None,
    github_token=None,
    output_dir="output",
    include_patterns=None,
    exclude_patterns=None,
    max_file_size=1000000,
    use_cache=True,
    focus_areas=None,
    # New parameters for ChromaDB storage
    store_in_chromadb=False,
    app_id=None,
    app_name=None,
    chromadb_dir="code_quality_db",
    chromadb_collection="code_quality_analyses",
    embedding_model_path=None,
    embedding_model_name=None,
    additional_metadata=None
):
    """
    Run code quality analysis programmatically.
    
    Args:
        repo_url (str, optional): URL of the GitHub repository to analyze.
        local_dir (str, optional): Path to local directory to analyze.
        project_name (str, optional): Custom project name. If None, derived from repo/dir.
        github_token (str, optional): GitHub token for API access.
        output_dir (str, optional): Directory to store output. Defaults to "output".
        include_patterns (set, optional): File patterns to include. Defaults to DEFAULT_INCLUDE_PATTERNS.
        exclude_patterns (set, optional): File patterns to exclude. Defaults to DEFAULT_EXCLUDE_PATTERNS.
        max_file_size (int, optional): Maximum file size in bytes. Defaults to 1000000.
        use_cache (bool, optional): Whether to use LLM response caching. Defaults to True.
        focus_areas (list, optional): List of areas to focus on. Defaults to all areas.
        
        # ChromaDB storage options
        store_in_chromadb (bool, optional): Whether to store results in ChromaDB. Defaults to False.
        app_id (str, optional): Unique ID for the application. Auto-generated if None.
        app_name (str, optional): Name of the application. Defaults to project_name if None.
        chromadb_dir (str, optional): Directory to store ChromaDB data. Defaults to "code_quality_db".
        chromadb_collection (str, optional): Collection name for ChromaDB. Defaults to "code_quality_analyses".
        embedding_model_path (str, optional): Path to a local embedding model.
        embedding_model_name (str, optional): Name of remote embedding model to use.
        additional_metadata (dict, optional): Additional metadata to store with the analysis.
        
    Returns:
        dict: A dictionary containing the analysis results with keys:
            - "report_content": The full content of the analysis report.
            - "report_path": Path to the saved report file.
            - "chromadb_doc_id": Document ID in ChromaDB (if stored).
    """
    # Validate input
    if not repo_url and not local_dir:
        raise ValueError("Either repo_url or local_dir must be provided")
    
    if repo_url and local_dir:
        raise ValueError("Only one of repo_url or local_dir should be provided")
        
    # Set default focus areas if not provided
    if focus_areas is None:
        focus_areas = ["logging", "availability", "error_handling"]
    elif isinstance(focus_areas, str):
        if focus_areas == "all":
            focus_areas = ["logging", "availability", "error_handling"]
        else:
            focus_areas = [focus_areas]
    
    # Set up default patterns if not provided
    if include_patterns is None:
        include_patterns = DEFAULT_INCLUDE_PATTERNS
    
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDE_PATTERNS
    
    # Get GitHub token from environment if not provided
    if repo_url and not github_token:
        github_token = os.environ.get('GITHUB_TOKEN')
        
    # Set up shared dictionary for the flow
    shared = {
        "repo_url": repo_url,
        "local_dir": local_dir,
        "project_name": project_name,  # Will be derived if None
        "github_token": github_token,
        "output_dir": output_dir,
        "include_patterns": include_patterns,
        "exclude_patterns": exclude_patterns,
        "max_file_size": max_file_size,
        "use_cache": use_cache,
        "focus_areas": focus_areas,
        "files": []
    }
    
    # Create and run the flow
    flow = create_quality_analysis_flow(focus_areas)
    flow.run(shared)
    
    # Prepare the result dictionary
    result = {
        "report_content": shared.get("code_quality_analysis", ""),
        "report_path": shared.get("code_quality_report_path", "")
    }
    
    # Store in ChromaDB if requested
    if store_in_chromadb:
        # Generate or use provided app_id
        if not app_id:
            app_id = str(uuid.uuid4())
            
        # Use project_name as app_name if not provided
        if not app_name:
            app_name = shared.get("project_name", "unknown_app")
        
        try:
            # Initialize ChromaDB storage
            storage = CodeQualityStorage(
                persist_directory=chromadb_dir,
                collection_name=chromadb_collection,
                embedding_model_path=embedding_model_path,
                embedding_model_name=embedding_model_name
            )
            
            # Store the analysis
            doc_id = storage.store_analysis(
                app_id=app_id,
                app_name=app_name,
                report_content=result["report_content"],
                focus_areas=focus_areas,
                additional_metadata=additional_metadata
            )
            
            # Add ChromaDB document ID to result
            result["chromadb_doc_id"] = doc_id
            result["app_id"] = app_id
            result["app_name"] = app_name
            
        except Exception as e:
            print(f"Error storing in ChromaDB: {e}")
            result["chromadb_error"] = str(e)
    
    return result

def main():
    parser = argparse.ArgumentParser(
        description="Analyze code quality focusing on logging, availability, and error handling."
    )

    # Create mutually exclusive group for source
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--repo", help="URL of the public GitHub repository.")
    source_group.add_argument("--dir", help="Path to local directory.")

    parser.add_argument("-n", "--name", help="Project name (optional, derived from repo/directory if omitted).")
    parser.add_argument("-t", "--token", help="GitHub personal access token (optional, reads from GITHUB_TOKEN env var if not provided).")
    parser.add_argument("-o", "--output", default="output", help="Base directory for output (default: ./output).")
    parser.add_argument("-i", "--include", nargs="+", help="Include file patterns (e.g. '*.py' '*.js').")
    parser.add_argument("-e", "--exclude", nargs="+", help="Exclude file patterns (e.g. 'tests/*' 'docs/*').")
    parser.add_argument("-s", "--max-size", type=int, default=1000000, help="Maximum file size in bytes (default: 1000000, about 1MB).")
    parser.add_argument("--no-cache", action="store_true", help="Disable LLM response caching (default: caching enabled)")
    parser.add_argument("--focus", choices=["logging", "availability", "error_handling", "all"], default="all", 
                      help="Focus area(s) of the analysis (default: all)")
                      
    # Add ChromaDB-related arguments
    chromadb_group = parser.add_argument_group('ChromaDB Storage Options')
    chromadb_group.add_argument("--store-db", action="store_true", help="Store analysis results in ChromaDB")
    chromadb_group.add_argument("--app-id", help="Unique ID for the application (generated if not provided)")
    chromadb_group.add_argument("--app-name", help="Name of the application (defaults to project name)")
    chromadb_group.add_argument("--db-dir", default="code_quality_db", help="Directory for ChromaDB storage (default: ./code_quality_db)")
    chromadb_group.add_argument("--db-collection", default="code_quality_analyses", help="Collection name in ChromaDB")
    chromadb_group.add_argument("--embedding-model", help="Path to local embedding model or name of remote model")
    chromadb_group.add_argument("--meta", nargs="+", help="Additional metadata as key=value pairs")

    args = parser.parse_args()

    # Get GitHub token from argument or environment variable if using repo
    github_token = None
    if args.repo:
        github_token = args.token or os.environ.get('GITHUB_TOKEN')
        if not github_token:
            print("Warning: No GitHub token provided. You might hit rate limits for public repositories.")
    
    # Prepare include/exclude patterns
    include_patterns = set(args.include) if args.include else DEFAULT_INCLUDE_PATTERNS
    exclude_patterns = set(args.exclude) if args.exclude else DEFAULT_EXCLUDE_PATTERNS

    # Convert focus argument to list
    if args.focus == "all":
        focus_areas = ["logging", "availability", "error_handling"]
    else:
        focus_areas = [args.focus]

    # Parse additional metadata if provided
    additional_metadata = {}
    if args.meta:
        for item in args.meta:
            if "=" in item:
                key, value = item.split("=", 1)
                additional_metadata[key.strip()] = value.strip()

    # Determine embedding model path vs name
    embedding_model_path = None
    embedding_model_name = None
    if args.embedding_model:
        if os.path.exists(args.embedding_model):
            embedding_model_path = args.embedding_model
        else:
            embedding_model_name = args.embedding_model

    # Display starting message
    source = args.repo or args.dir
    print(f"Starting code quality analysis for: {source}")
    print(f"Focus areas: {', '.join(focus_areas)}")
    print(f"LLM caching: {'Disabled' if args.no_cache else 'Enabled'}")
    
    if args.store_db:
        app_id = args.app_id or str(uuid.uuid4())
        app_name = args.app_name or args.name or (os.path.basename(args.dir) if args.dir else "unknown")
        print(f"Will store results in ChromaDB as {app_name} (ID: {app_id})")
        if embedding_model_path:
            print(f"Using local embedding model: {embedding_model_path}")
        elif embedding_model_name:
            print(f"Using remote embedding model: {embedding_model_name}")

    # Run analysis using the function
    result = run_quality_analysis(
        repo_url=args.repo,
        local_dir=args.dir,
        project_name=args.name,
        github_token=github_token,
        output_dir=args.output,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        max_file_size=args.max_size,
        use_cache=not args.no_cache,
        focus_areas=focus_areas,
        # ChromaDB options
        store_in_chromadb=args.store_db,
        app_id=args.app_id,
        app_name=args.app_name,
        chromadb_dir=args.db_dir,
        chromadb_collection=args.db_collection,
        embedding_model_path=embedding_model_path,
        embedding_model_name=embedding_model_name,
        additional_metadata=additional_metadata if additional_metadata else None
    )

    print(f"\nCode quality analysis complete! Report is in: {result['report_path']}")
    
    if args.store_db and "chromadb_doc_id" in result:
        print(f"Analysis stored in ChromaDB with ID: {result['chromadb_doc_id']}")
    elif args.store_db and "chromadb_error" in result:
        print(f"Error storing in ChromaDB: {result['chromadb_error']}")
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 