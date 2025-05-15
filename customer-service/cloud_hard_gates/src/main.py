import asyncio
from dotenv import load_dotenv
import os
from src.models.model_config import ModelConfig
from src.agents.web_agent import WebAgent

async def main():
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
    
    # Example: Extract information from a website
    selectors = {
        "title": "h1",
        "main_content": "article",
        "price": ".price"
    }
    
    result = await agent.extract_information(
        url="https://example.com",
        selectors=selectors
    )
    print("Extracted Information:", result)
    
    # Example: Perform a task on a website
    task_result = await agent.browse_website(
        url="https://example.com",
        task="Find the contact information and click the contact button"
    )
    print("Task Result:", task_result)

if __name__ == "__main__":
    asyncio.run(main()) 