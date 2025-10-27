#!/bin/bash

# Household Ledger MySQL Database Quick Start Script

echo "🚀 Starting Household Ledger MySQL Database..."

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q "^household-ledger-db$"; then
    echo "⚠️  Container 'household-ledger-db' already exists"
    read -p "Do you want to remove it? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker rm -f household-ledger-db
        echo "✅ Removed existing container"
    else
        echo "Starting existing container..."
        docker start household-ledger-db
        echo "✅ Database started on localhost:3306"
        exit 0
    fi
fi

# Build image (if not exists)
if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^household-ledger-mysql:latest$"; then
    echo "📦 Building MySQL image..."
    docker build -t household-ledger-mysql:latest -f "$(dirname "$0")/Dockerfile.mysql" "$(dirname "$0")"
fi

# Run container
echo "🔄 Creating and starting container..."
docker run -d \
  --name household-ledger-db \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=wjdwhdans \
  -e MYSQL_DATABASE=household_ledger \
  -e MYSQL_USER=gary \
  -e MYSQL_PASSWORD=wjdwhdans \
  household-ledger-mysql:latest

# Wait for MySQL to be ready
echo "⏳ Waiting for MySQL to be ready..."
sleep 5

# Check if container is running
if docker ps --format '{{.Names}}' | grep -q "^household-ledger-db$"; then
    echo "✅ Database started successfully!"
    echo ""
    echo "📊 Connection Info:"
    echo "   Host: 127.0.0.1"
    echo "   Port: 3306"
    echo "   User: gary"
    echo "   Password: wjdwhdans"
    echo "   Database: household_ledger"
    echo ""
    echo "🔧 Commands:"
    echo "   Logs:     docker logs household-ledger-db"
    echo "   Stop:     docker stop household-ledger-db"
    echo "   Remove:   docker rm household-ledger-db"
else
    echo "❌ Failed to start database"
    docker logs household-ledger-db
    exit 1
fi

