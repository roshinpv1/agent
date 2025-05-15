"""Tools module for the Hard Gates validation system."""

import logging
from typing import Dict, Any, List
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

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
        # Initialize ChromaDB client
        client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_db"
        ))
        
        # Get the collection
        collection = client.get_collection(collection_name)
        
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

def validate_alerting(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates alerting configuration and implementation.

    Args:
        config (dict): Alerting configuration including thresholds, routing, and documentation.

    Returns:
        dict: Validation results with status and details.

    Example:
        >>> validate_alerting({
            'thresholds': {'cpu': 80, 'memory': 85},
            'routing': {'email': True, 'slack': True},
            'documentation': 'Alert procedures documented'
        })
        {'status': 'pass', 'checks': [{'name': 'Alert Configuration', 'status': 'pass'}]}
    """
    logger.info("Validating alerting configuration: %s", config)
    
    checks = [
        {
            "name": "Alert Configuration",
            "status": "pass" if config.get("thresholds") else "fail",
            "details": "Alert thresholds properly configured" if config.get("thresholds") else "Missing alert thresholds",
            "recommendations": []
        },
        {
            "name": "Alert Routing",
            "status": "pass" if config.get("routing") else "fail",
            "details": "Alert routing properly configured" if config.get("routing") else "Missing alert routing",
            "recommendations": []
        }
    ]
    
    return {
        "criteria_id": "alerting",
        "status": "pass" if all(check["status"] == "pass" for check in checks) else "fail",
        "checks": checks
    }

def validate_auditability(logs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates logging and audit trail implementation.

    Args:
        logs (dict): Logging configuration including storage, retention, and search.

    Returns:
        dict: Validation results with status and details.

    Example:
        >>> validate_auditability({
            'storage': {'enabled': True, 'retention': '30d'},
            'search': {'enabled': True},
            'audit_trail': {'enabled': True}
        })
        {'status': 'pass', 'checks': [{'name': 'Log Storage', 'status': 'pass'}]}
    """
    logger.info("Validating auditability implementation: %s", logs)
    
    checks = [
        {
            "name": "Log Storage",
            "status": "pass" if logs.get("storage", {}).get("enabled") else "fail",
            "details": "Log storage properly configured" if logs.get("storage", {}).get("enabled") else "Log storage not enabled",
            "recommendations": []
        },
        {
            "name": "Audit Trail",
            "status": "pass" if logs.get("audit_trail", {}).get("enabled") else "fail",
            "details": "Audit trail properly implemented" if logs.get("audit_trail", {}).get("enabled") else "Audit trail not enabled",
            "recommendations": []
        }
    ]
    
    return {
        "criteria_id": "auditability",
        "status": "pass" if all(check["status"] == "pass" for check in checks) else "fail",
        "checks": checks
    }

def validate_availability(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates availability features and configurations.

    Args:
        config (dict): Availability configuration including retry logic and circuit breaker.

    Returns:
        dict: Validation results with status and details.

    Example:
        >>> validate_availability({
            'retry_logic': {'enabled': True, 'max_retries': 3},
            'circuit_breaker': {'enabled': True, 'threshold': 5}
        })
        {'status': 'pass', 'checks': [{'name': 'Retry Logic', 'status': 'pass'}]}
    """
    logger.info("Validating availability features: %s", config)
    
    checks = [
        {
            "name": "Retry Logic",
            "status": "pass" if config.get("retry_logic", {}).get("enabled") else "fail",
            "details": "Retry logic properly implemented" if config.get("retry_logic", {}).get("enabled") else "Retry logic not enabled",
            "recommendations": []
        },
        {
            "name": "Circuit Breaker",
            "status": "pass" if config.get("circuit_breaker", {}).get("enabled") else "fail",
            "details": "Circuit breaker properly configured" if config.get("circuit_breaker", {}).get("enabled") else "Circuit breaker not enabled",
            "recommendations": []
        }
    ]
    
    return {
        "criteria_id": "availability",
        "status": "pass" if all(check["status"] == "pass" for check in checks) else "fail",
        "checks": checks
    }

def validate_error_handling(code: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates error handling implementation.

    Args:
        code (dict): Error handling configuration including logging and error codes.

    Returns:
        dict: Validation results with status and details.

    Example:
        >>> validate_error_handling({
            'error_logging': {'enabled': True},
            'http_codes': {'standard': True}
        })
        {'status': 'pass', 'checks': [{'name': 'Error Logging', 'status': 'pass'}]}
    """
    logger.info("Validating error handling implementation: %s", code)
    
    checks = [
        {
            "name": "Error Logging",
            "status": "pass" if code.get("error_logging", {}).get("enabled") else "fail",
            "details": "Error logging properly implemented" if code.get("error_logging", {}).get("enabled") else "Error logging not enabled",
            "recommendations": []
        },
        {
            "name": "HTTP Error Codes",
            "status": "pass" if code.get("http_codes", {}).get("standard") else "fail",
            "details": "HTTP error codes properly used" if code.get("http_codes", {}).get("standard") else "Non-standard HTTP error codes used",
            "recommendations": []
        }
    ]
    
    return {
        "criteria_id": "error_handling",
        "status": "pass" if all(check["status"] == "pass" for check in checks) else "fail",
        "checks": checks
    }

def validate_monitoring(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates monitoring setup and configuration.

    Args:
        metrics (dict): Monitoring configuration including CPU and memory monitoring.

    Returns:
        dict: Validation results with status and details.

    Example:
        >>> validate_monitoring({
            'cpu_monitoring': {'enabled': True, 'threshold': 80},
            'memory_monitoring': {'enabled': True, 'threshold': 85}
        })
        {'status': 'pass', 'checks': [{'name': 'CPU Monitoring', 'status': 'pass'}]}
    """
    logger.info("Validating monitoring setup: %s", metrics)
    
    checks = [
        {
            "name": "CPU Monitoring",
            "status": "pass" if metrics.get("cpu_monitoring", {}).get("enabled") else "fail",
            "details": "CPU monitoring properly configured" if metrics.get("cpu_monitoring", {}).get("enabled") else "CPU monitoring not enabled",
            "recommendations": []
        },
        {
            "name": "Memory Monitoring",
            "status": "pass" if metrics.get("memory_monitoring", {}).get("enabled") else "fail",
            "details": "Memory monitoring properly configured" if metrics.get("memory_monitoring", {}).get("enabled") else "Memory monitoring not enabled",
            "recommendations": []
        }
    ]
    
    return {
        "criteria_id": "monitoring",
        "status": "pass" if all(check["status"] == "pass" for check in checks) else "fail",
        "checks": checks
    }

def validate_recoverability(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates recovery strategy and procedures.

    Args:
        plan (dict): Recovery plan configuration including strategy and testing.

    Returns:
        dict: Validation results with status and details.

    Example:
        >>> validate_recoverability({
            'strategy': {'documented': True},
            'testing': {'procedures': True}
        })
        {'status': 'pass', 'checks': [{'name': 'Recovery Strategy', 'status': 'pass'}]}
    """
    logger.info("Validating recovery strategy: %s", plan)
    
    checks = [
        {
            "name": "Recovery Strategy",
            "status": "pass" if plan.get("strategy", {}).get("documented") else "fail",
            "details": "Recovery strategy properly documented" if plan.get("strategy", {}).get("documented") else "Recovery strategy not documented",
            "recommendations": []
        },
        {
            "name": "Recovery Testing",
            "status": "pass" if plan.get("testing", {}).get("procedures") else "fail",
            "details": "Recovery testing procedures in place" if plan.get("testing", {}).get("procedures") else "Recovery testing procedures missing",
            "recommendations": []
        }
    ]
    
    return {
        "criteria_id": "recoverability",
        "status": "pass" if all(check["status"] == "pass" for check in checks) else "fail",
        "checks": checks
    }

def validate_testing(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates testing implementation and coverage.

    Args:
        results (dict): Testing results including regression and performance tests.

    Returns:
        dict: Validation results with status and details.

    Example:
        >>> validate_testing({
            'regression': {'implemented': True, 'coverage': 85},
            'performance': {'implemented': True, 'metrics': ['response_time', 'throughput']}
        })
        {'status': 'pass', 'checks': [{'name': 'Regression Testing', 'status': 'pass'}]}
    """
    logger.info("Validating testing implementation: %s", results)
    
    checks = [
        {
            "name": "Regression Testing",
            "status": "pass" if results.get("regression", {}).get("implemented") else "fail",
            "details": "Regression testing properly implemented" if results.get("regression", {}).get("implemented") else "Regression testing not implemented",
            "recommendations": []
        },
        {
            "name": "Performance Testing",
            "status": "pass" if results.get("performance", {}).get("implemented") else "fail",
            "details": "Performance testing properly configured" if results.get("performance", {}).get("implemented") else "Performance testing not implemented",
            "recommendations": []
        }
    ]
    
    return {
        "criteria_id": "testing",
        "status": "pass" if all(check["status"] == "pass" for check in checks) else "fail",
        "checks": checks
    }