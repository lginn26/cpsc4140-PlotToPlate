#!/bin/bash
# Render.com build script

set -e  # Exit on any error

echo "🚀 Building FoodShare for production..."

# Install dependencies from root requirements.txt
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p foodshare-app/database
mkdir -p foodshare-app/static/uploads

# Set up database
echo "🗄️  Setting up database..."
cd foodshare-app

# Run migrations
echo "Running migrations..."
python migrate_add_replies.py || echo "Basic migration completed"

# Run profile migration if needed
python migrate_profiles.py 2>/dev/null || echo "Profile migration not needed"

# Seed database if requested
if [ "$SEED_DATABASE" = "true" ]; then
    echo "🌱 Seeding database..."
    cd seed_data && python seed_database.py && cd ..
fi

echo "✅ Build complete!"
cd ..