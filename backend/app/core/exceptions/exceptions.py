class LiaisonBaseException(Exception):
    """Base exception for the Liaison-Spark application."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class LLMRateLimitException(LiaisonBaseException):
    """Raised when the LLM provider returns a rate limit or quota error."""
    def __init__(self, message: str = "LLM rate limit exceeded. Please try again later."):
        super().__init__(message, status_code=429)

class LLMProviderException(LiaisonBaseException):
    """Raised when the LLM provider returns a generic error."""
    def __init__(self, message: str = "An error occurred with the LLM provider."):
        super().__init__(message, status_code=502)

class VectorDBException(LiaisonBaseException):
    """Raised when Weaviate or vector search operations fail."""
    def __init__(self, message: str = "Vector database operation failed."):
        super().__init__(message, status_code=500)