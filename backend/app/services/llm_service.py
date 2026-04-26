from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.core.config import settings


class LLMService:
    """
    Service class to manage LLM instantiations.
    Centralizes configuration and allows flexible model creation.
    """

    def __init__(self):
        # Load application-wide defaults from environment variables
        self.default_model = settings.LLM_MODEL
        self.default_temperature = settings.LLM_TEMPERATURE
        self.default_embedding_model = settings.EMBEDDING_MODEL

        # Base URL is completely optional. If not set, ChatOpenAI uses standard OpenAI routing.
        self.base_url = settings.OPENAI_BASE_URL

    def get_llm(
        self,
        model: str | None = None,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> ChatOpenAI | ChatGoogleGenerativeAI:
        """
        Creates and returns a ChatOpenAI or ChatGoogleGenerativeAI instance.
        Defaults are used unless explicitly overridden via arguments.
        """
        model_name = model if model is not None else self.default_model

        llm_kwargs: dict[str, Any] = {
            "model": model_name,
            "temperature": temperature
            if temperature is not None
            else self.default_temperature,
            **kwargs,
        }

        if model_name.startswith("gemini"):
            return ChatGoogleGenerativeAI(**llm_kwargs)
        else:
            # Only inject base_url if it's explicitly configured
            if self.base_url:
                llm_kwargs["base_url"] = self.base_url

            return ChatOpenAI(**llm_kwargs)

    def get_embeddings(
        self, model: str | None = None, **kwargs: Any
    ) -> OpenAIEmbeddings | GoogleGenerativeAIEmbeddings:
        """
        Creates and returns an Embeddings instance.
        Defaults are used unless explicitly overridden via arguments.
        """
        model_name = model if model is not None else self.default_embedding_model

        embed_kwargs: dict[str, Any] = {"model": model_name, **kwargs}

        # Route to Google if using Google's conventions or 'gemini'
        if (
            model_name.startswith("models/")
            or "gemini-embedding" in model_name
            or "text-embedding-004" in model_name
            or "embedding-001" in model_name
            or "gemini" in model_name
        ):
            # Gemini API expects the 'models/' prefix for embeddings
            if not model_name.startswith("models/"):
                embed_kwargs["model"] = f"models/{model_name}"
            return GoogleGenerativeAIEmbeddings(**embed_kwargs)
        else:
            # Optional: Remove the next 2 lines if MeshAPI strictly doesn't support embeddings
            # and you want to default directly to standard OpenAI servers for embeddings instead.
            if self.base_url:
                embed_kwargs["base_url"] = self.base_url

            return OpenAIEmbeddings(**embed_kwargs)


# Create a singleton instance to be imported and used across our application
llm_service = LLMService()
