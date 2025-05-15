import asyncio
from dotenv import load_dotenv
import os
from models.model_config import ModelConfig
from agents.web_agent import WebAgent

async def test_agent():
    # Load environment variables
    load_dotenv()
    
    # Configure the model
    model_config = ModelConfig(
        model_name="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY", "test"),
        base_url=os.getenv("MODEL_BASE_URL", "http://localhost:1234/v1"),
        temperature=0.0,
        max_tokens=1000
    )
    
    # Create the web agent
    agent = WebAgent(model_config)
    
    # Test web navigation
    print("Testing web navigation...")
    result = await agent.browse_website(
        url="https://example.com",
        task="Get the main heading of the page"
    )
    print("Navigation result:", result)
    
    # Test information extraction
    print("\nTesting information extraction...")
    selectors = {
        "title": "h1",
        "description": "p"
    }
    result = await agent.extract_information(
        url="https://example.com",
        selectors=selectors
    )
    print("Extraction result:", result)

if __name__ == "__main__":
    asyncio.run(test_agent()) 