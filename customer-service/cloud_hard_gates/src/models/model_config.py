from typing import Optional, Union
from pydantic import BaseModel
from openai import OpenAI
from google.adk.models.lite_llm import LiteLlm

class ModelConfig(BaseModel):
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 1000
    top_p: float = 0.95
    top_k: int = 40

    def get_client(self) -> Union[LiteLlm, OpenAI]:
        if self.base_url and "localhost" in self.base_url:
            return LiteLlm(
                model=self.model_name,
                api_key=self.api_key,
                base_url=self.base_url,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                top_k=self.top_k
            )
        else:
            return OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            ) 