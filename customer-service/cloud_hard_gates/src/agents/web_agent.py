from typing import Dict, Any, List
from google.adk.agents import Agent
from google.adk.tools import BaseTool
from src.models.model_config import ModelConfig
from src.mcp.playwright_mcp import PlaywrightMCP

class WebNavigationTool(BaseTool):
    name = "web_navigation"
    description = "Navigate to a specific URL"
    
    def __init__(self, mcp: PlaywrightMCP):
        self.mcp = mcp
        
    async def __call__(self, url: str) -> Dict[str, Any]:
        await self.mcp.navigate(url)
        return {"status": "success", "url": url}

class WebExtractionTool(BaseTool):
    name = "web_extraction"
    description = "Extract content from a webpage using CSS selectors"
    
    def __init__(self, mcp: PlaywrightMCP):
        self.mcp = mcp
        
    async def __call__(self, selectors: Dict[str, str]) -> Dict[str, str]:
        results = {}
        for field, selector in selectors.items():
            content = await self.mcp.get_content(selector)
            results[field] = content
        return results

class WebAgent(Agent):
    def __init__(
        self,
        model_config: ModelConfig,
        description: str = "A web-savvy assistant that can browse and interact with websites."
    ):
        self.mcp = PlaywrightMCP()
        tools = [
            WebNavigationTool(self.mcp),
            WebExtractionTool(self.mcp)
        ]
        
        super().__init__(
            model=model_config.get_client(),
            description=description,
            tools=tools
        )

    async def browse_website(self, url: str, task: str) -> Dict[str, Any]:
        """
        Browse a website and perform a specific task.
        
        Args:
            url: The URL to browse
            task: Description of what to do on the website
            
        Returns:
            Dict containing the results of the task
        """
        try:
            await self.mcp.initialize()
            
            # First navigate to the URL
            await self.tools[0](url)
            
            # Use the model to determine what actions to take
            response = await self.model.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a web automation expert. Given a task, determine the necessary actions."},
                    {"role": "user", "content": f"Task: {task}\nURL: {url}\nWhat actions should I take?"}
                ]
            )
            
            # Execute the determined actions
            actions = response.choices[0].message.content
            result = await self.mcp.execute_script(actions)
            
            return {
                "status": "success",
                "actions": actions,
                "result": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
        finally:
            await self.mcp.close()

    async def extract_information(self, url: str, selectors: Dict[str, str]) -> Dict[str, str]:
        """
        Extract specific information from a website using CSS selectors.
        
        Args:
            url: The URL to browse
            selectors: Dictionary mapping field names to CSS selectors
            
        Returns:
            Dict containing the extracted information
        """
        try:
            await self.mcp.initialize()
            
            # First navigate to the URL
            await self.tools[0](url)
            
            # Then extract the information
            results = await self.tools[1](selectors)
            return results
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
        finally:
            await self.mcp.close() 