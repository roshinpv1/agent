# Web Agent Ecosystem

A comprehensive agent ecosystem built with Google ADK that combines local model integration and Playwright MCP for web automation.

## Features

- Integration with both local and cloud-based language models
- Web automation capabilities using Playwright
- Flexible model configuration
- Async support for better performance
- Error handling and resource cleanup

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install
```

4. Create a `.env` file with your configuration:
```
OPENAI_API_KEY=your_api_key
MODEL_BASE_URL=http://localhost:1234/v1  # For local model
```

## Usage

The project provides a `WebAgent` class that combines language model capabilities with web automation:

```python
from models.model_config import ModelConfig
from agents.web_agent import WebAgent

# Configure the model
model_config = ModelConfig(
    model_name="gpt-3.5-turbo",
    api_key="your_api_key",
    base_url="http://localhost:1234/v1"
)

# Create the web agent
agent = WebAgent(model_config)

# Extract information from a website
selectors = {
    "title": "h1",
    "content": "article"
}
result = await agent.extract_information(
    url="https://example.com",
    selectors=selectors
)

# Perform a task on a website
task_result = await agent.browse_website(
    url="https://example.com",
    task="Find and click the contact button"
)
```

## Project Structure

```
.
├── src/
│   ├── agents/
│   │   └── web_agent.py
│   ├── models/
│   │   └── model_config.py
│   ├── mcp/
│   │   └── playwright_mcp.py
│   └── main.py
├── requirements.txt
└── README.md
```

## Contributing

Feel free to submit issues and enhancement requests! 