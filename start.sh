#!/bin/bash
# Clarity - Start Development Environment (Docker)
# Starts the full stack using docker-compose with proper rebuild handling

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "======================================"
echo "🐳 Starting Clarity with Docker"
echo "======================================"
echo ""

# Check if Docker and Docker Compose are available
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed or not in PATH"
    exit 1
fi

# Parse flags
FRONTEND_SERVICE=""
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --frontend-dev)
            FRONTEND_SERVICE="frontend-dev"
            shift
            ;;
        --frontend-prod)
            FRONTEND_SERVICE="frontend-prod"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--frontend-dev|--frontend-prod]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--frontend-dev|--frontend-prod]"
            exit 1
            ;;
    esac
done

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down 2>/dev/null || true

# Clean Docker cache to prevent build issues
echo "🧹 Cleaning Docker cache..."
docker system prune -a --volumes -f > /dev/null 2>&1 || true

# Build and start services (start DB and backend by default)
echo ""
echo "🔨 Building and starting services..."
SERVICES=(db app)
if [ -n "$FRONTEND_SERVICE" ]; then
    SERVICES+=("$FRONTEND_SERVICE")
fi
docker-compose up -d --build "${SERVICES[@]}"

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
echo ""
echo "======================================"
echo "✅ Services Started Successfully!"
echo "======================================"
echo ""
echo "🐳 Docker Containers:"
docker-compose ps
echo ""
echo "📝 Log in with:"
echo "   Email: admin@clarity.local"
echo "   Password: admin123"
echo ""
if [ "$FRONTEND_SERVICE" = "frontend-prod" ]; then
    echo "📱 Frontend (prod):  http://localhost:5173"
elif [ "$FRONTEND_SERVICE" = "frontend-dev" ]; then
    echo "📱 Frontend (dev):  http://localhost:5173"
else
    echo "📱 Frontend:  not started (use --frontend-dev or --frontend-prod)"
fi
echo "🔌 Backend:   http://localhost:8000"
echo "📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "📋 To see logs: docker-compose logs -f"
echo "🛑 To stop: ./stop.sh"
echo ""
echo "Showing logs (Ctrl+C to exit)..."
if [ -n "$FRONTEND_SERVICE" ]; then
    docker-compose logs -f app "$FRONTEND_SERVICE"
else
    docker-compose logs -f app
fi
