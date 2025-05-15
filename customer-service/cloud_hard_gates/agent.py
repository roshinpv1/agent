
"""Agent module for the customer service agent."""

import logging
import warnings
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters , SseServerParams


from .config import Config
from .myprompts import GLOBAL_INSTRUCTION, INSTRUCTION
from .shared_libraries.callbacks import (
    rate_limit_callback,
    before_agent,   
    before_tool,
)
from .tools.tools import (
    validate_alerting,
    validate_alerting,
    validate_auditability,
    validate_availability,
    validate_error_handling,
    validate_monitoring,
    validate_recoverability,
    validate_testing
)

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

configs = Config()

# configure logging __name__
logger = logging.getLogger(__name__)

root_agent = Agent(
    model= LiteLlm(model="gpt-3.5-turbo", base_url="http://localhost:1234/v1" , api_key="sdsd" ),
    global_instruction=GLOBAL_INSTRUCTION,
    instruction=INSTRUCTION,
    name="Cloud_Hard_Gates",
    tools=[
        validate_alerting,
        validate_alerting,
        validate_auditability,
        validate_availability,
        validate_error_handling,
        validate_monitoring,
        validate_recoverability,
        validate_testing
    ],
    before_tool_callback=before_tool,
    before_agent_callback=before_agent,
    before_model_callback=rate_limit_callback,
)
