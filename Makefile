.PHONY: install backend frontend docker-up docker-down clean

# Install dependencies for both backend and frontend
install:
	@echo "Installing backend dependencies..."
	cd backend && uv pip install fastapi "uvicorn[standard]" pydantic pydantic-settings python-dotenv structlog "weaviate-client>=4.0.0" langchain langchain-core langchain-google-genai langchain-openai langchain-weaviate langgraph
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Start the Weaviate vector database in the background
docker-up:
	@echo "Starting Weaviate Docker container..."
	docker-compose up -d

# Stop the Weaviate vector database
docker-down:
	@echo "Stopping Weaviate Docker container..."
	docker-compose down

# Start the FastAPI backend server
backend:
	@echo "Starting FastAPI backend..."
	cd backend && uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

# Start the React frontend server
frontend:
	@echo "Starting React frontend..."
	cd frontend && npm start