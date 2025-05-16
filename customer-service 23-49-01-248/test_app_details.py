#!/usr/bin/env python3
"""Test script for the get_application_details tool."""

import asyncio
import logging
from cloud_hard_gates.agent import get_app_info, root_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_get_app_details():
    """Test the get_application_details tool using various approaches."""
    
    print("\n=== Testing get_application_details tool ===\n")
    
    # Test 1: Using the helper function
    print("Test 1: Using helper function get_app_info")
    response = await get_app_info("app-123")
    print(f"Response for app-123 (without metrics):\n{response}\n")
    
    # Test 2: Using helper function with metrics
    print("Test 2: Using helper function with metrics")
    response = await get_app_info("app-456", include_metrics=True)
    print(f"Response for app-456 (with metrics):\n{response}\n")
    
    # Test 3: Using direct agent query
    print("Test 3: Using direct agent query")
    prompt = "Can you tell me about the application with ID app-789? Please include metrics."
    response = await root_agent.generate_content(prompt)
    print(f"Direct agent response:\n{response}\n")
    
    # Test 4: Testing error handling
    print("Test 4: Testing error handling")
    response = await get_app_info("non-existent-app")
    print(f"Response for non-existent app:\n{response}\n")
    
    # Test 5: Interactive mode
    print("Test 5: Interactive mode")
    print("Enter 'quit' to exit")
    
    while True:
        app_id = input("Enter an application ID to look up: ")
        if app_id.lower() == 'quit':
            break
            
        include_metrics = input("Include metrics? (y/n): ").lower() == 'y'
        response = await get_app_info(app_id, include_metrics)
        print(f"\nResponse:\n{response}\n")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_get_app_details()) 