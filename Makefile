.PHONY: dev frontend backend build prod help

# Default ports
FRONTEND_PORT ?= 3000
BACKEND_PORT ?= 8000

# Default target
dev:
	@echo "Starting both frontend and backend servers..."
	@make -j2 frontend backend

# Run frontend development server
frontend:
	@echo "Starting frontend server on port $(FRONTEND_PORT)..."
	@cd frontend && BACKEND_URL=http://localhost:$(BACKEND_PORT) npm run dev -- --port $(FRONTEND_PORT)

# Run backend server with uv
backend:
	@echo "Starting backend server on port $(BACKEND_PORT)..."
	@cd backend && DEBUG=true PORT=$(BACKEND_PORT) uv run python main.py

# Build frontend for production
build:
	@echo "Building frontend for production..."
	@cd frontend && npm install && npm run build

# Run production servers
prod:
	@echo "Starting production servers..."
	@make -j2 prod-frontend backend

# Deploy command for Render (backend on 8000, frontend on $PORT)
deploy:
	@echo "Starting deployment servers..."
	@cd backend && PORT=8000 uv run python main.py &
	@cd frontend && BACKEND_URL=http://localhost:8000 npm run start -- --port $(PORT)

# Run frontend production server
prod-frontend:
	@echo "Starting frontend production server on port $(FRONTEND_PORT)..."
	@cd frontend && BACKEND_URL=http://localhost:$(BACKEND_PORT) npm run start -- --port $(FRONTEND_PORT)

# Show help
help:
	@echo "Available targets:"
	@echo "  dev      - Start both frontend and backend servers (default)"
	@echo "  frontend - Start only the frontend server"
	@echo "  backend  - Start only the backend server"
	@echo "  build    - Build frontend for production"
	@echo "  prod     - Start production servers"
	@echo "  help     - Show this help message"
	@echo ""
	@echo "Port configuration:"
	@echo "  FRONTEND_PORT=<port> - Set frontend port (default: 3000)"
	@echo "  BACKEND_PORT=<port>  - Set backend port (default: 8000)"
	@echo ""
	@echo "Examples:"
	@echo "  make dev FRONTEND_PORT=3001 BACKEND_PORT=8001"
	@echo "  make frontend FRONTEND_PORT=4000"
	@echo "  make backend BACKEND_PORT=9000"