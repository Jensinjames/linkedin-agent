#!/bin/bash

# Quick setup script for simplified LinkedIn Agent
# This version requires minimal external configuration

set -e

echo "🚀 Setting up Simplified LinkedIn Agent..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p storage/data/jobs
mkdir -p storage/data/logs
mkdir -p storage/backups

# Copy example configuration
echo "⚙️ Setting up configuration..."
if [ ! -f .env ]; then
    cp examples/env.example .env
    echo "✅ Created .env file from example"
    echo "📝 Edit .env to add your OpenAI API key (optional)"
else
    echo "✅ .env already exists"
fi

# Create admin user for local authentication
echo "👤 Setting up local admin user..."
cd backend
python3 -c "
import asyncio
from src.adapters.simple_local_adapter import SimpleLocalAdapter

async def setup_admin():
    adapter = SimpleLocalAdapter(data_dir='../storage/data')
    try:
        adapter.create_user('admin', 'admin123', is_admin=True)
        print('✅ Created admin user: admin/admin123')
        print('🔒 Please change this password in production!')
    except Exception as e:
        print(f'ℹ️ Admin user setup: {e}')

asyncio.run(setup_admin())
"
cd ..

# Build and start simplified version
echo "🐳 Building simplified Docker image..."
cd infrastructure/docker
docker-compose -f docker-compose.simple.yml build

echo "🎉 Setup complete!"
echo ""
echo "🚀 To start the simplified agent:"
echo "   cd infrastructure/docker"
echo "   docker-compose -f docker-compose.simple.yml up"
echo ""
echo "📋 Test the agent:"
echo "   cd backend"
echo "   python simple_main.py examples/input.json"
echo ""
echo "🌐 Access points:"
echo "   - API: http://localhost:8000"
echo "   - Web UI: http://localhost:3000 (optional)"
echo ""
echo "🔑 Default admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   (Change these in production!)"
