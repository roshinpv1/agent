import asyncio
from dotenv import load_dotenv
import os
from models.model_config import ModelConfig
from agents.hard_gates_agent import HardGatesAgent

async def test_hard_gates():
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
    
    # Create the Hard Gates validation agent
    agent = HardGatesAgent(model_config)
    
    # Test context
    context = {
        "environment": "production",
        "application": "example-app",
        "region": "us-west-2",
        "deployment_type": "cloud",
        "infrastructure": {
            "alerting": {
                "enabled": True,
                "thresholds": {
                    "cpu": 80,
                    "memory": 85,
                    "disk": 90
                }
            },
            "monitoring": {
                "enabled": True,
                "metrics": ["cpu", "memory", "disk", "network"]
            }
        },
        "application": {
            "logging": {
                "enabled": True,
                "level": "INFO",
                "retention": "30d"
            },
            "error_handling": {
                "enabled": True,
                "retry_count": 3,
                "timeout": 30
            }
        }
    }
    
    # Test single criteria validation
    print("Testing single criteria validation...")
    result = await agent.validate_criteria(
        criteria_id="alerting",
        context=context
    )
    print("Single criteria result:", result)
    
    # Test validation chain
    print("\nTesting validation chain...")
    criteria_chain = ["alerting", "auditability", "availability"]
    results = await agent.validate_chain(
        criteria_ids=criteria_chain,
        context=context
    )
    
    # Generate and print validation report
    report = await agent.generate_validation_report(results)
    print("\nValidation Report:")
    print(report)

if __name__ == "__main__":
    asyncio.run(test_hard_gates()) 