import weaviate
from app.core.config import settings

class WeaviateClientService:
    def __init__(self):
        self.host = settings.WEAVIATE_HOST
        self.port = settings.WEAVIATE_PORT
        self.grpc_port = settings.WEAVIATE_GRPC_PORT

        # Fail fast validation if minimum OS parameters are missing
        if not all([self.host, self.port, self.grpc_port]):
            raise ValueError(
                "Missing required Weaviate environment variables. "
                "Please set WEAVIATE_HOST, WEAVIATE_PORT, and WEAVIATE_GRPC_PORT in your .env file."
            )

        # Establish the connection to Weaviate
        self.client = weaviate.connect_to_custom(
            http_host=self.host,
            http_port=int(self.port),
            http_secure=False,  # Set to True if using a managed cloud Weaviate
            grpc_host=self.host,
            grpc_port=int(self.grpc_port),
            grpc_secure=False
        )

    def get_client(self) -> weaviate.WeaviateClient:
        return self.client

# Singleton instance to be used across the application
weaviate_service = WeaviateClientService()