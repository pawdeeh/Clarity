#!/bin/bash
# Clarity - Stop Development Environment (Docker)
# Stops all running docker containers

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "======================================"
echo "🛑 Stopping Clarity"
echo "======================================"
echo ""

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed or not in PATH"
    exit 1
fi

# Stop all services
echo "Stopping docker-compose services..."
docker-compose down

echo ""
echo "======================================"
echo "✅ Services Stopped"
echo "======================================"
