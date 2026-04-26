import os
from typing import Optional, Any, Dict
from langchain_openai import ChatOpenAI

class LLMService:
    """
    Service class to manage LLM instantiations.
    Centralizes configuration and allows flexible model creation.
    """
    def __init__(self):
        # Load application-wide defaults from environment variables
        self.default_model = os.environ.get("LLM_MODEL", "gpt-4o")
        self.default_temperature = float(os.environ.get("LLM_TEMPERATURE", "0.0"))
        
        # Base URL is completely optional. If not set, ChatOpenAI uses standard OpenAI routing.
        self.base_url = os.environ.get("OPENAI_BASE_URL", None)

    def get_llm(
        self, 
        model: Optional[str] = None, 
        temperature: Optional[float] = None, 
        **kwargs: Any
    ) -> ChatOpenAI:
        """
        Creates and returns a ChatOpenAI instance.
        Defaults are used unless explicitly overridden via arguments.
        """
        llm_kwargs: Dict[str, Any] = {
            "model": model if model is not None else self.default_model,
            "temperature": temperature if temperature is not None else self.default_temperature,
            **kwargs
        }
        
        # Only inject base_url if it's explicitly configured
        if self.base_url:
            llm_kwargs["base_url"] = self.base_url
            
        return ChatOpenAI(**llm_kwargs)

# Create a singleton instance to be imported and used across our application
llm_service = LLMService()