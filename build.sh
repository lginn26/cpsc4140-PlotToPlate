#!/bin/bash
# Render.com build script

echo "🚀 Building FoodShare for production..."

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
mkdir -p foodshare-app/database
mkdir -p foodshare-app/static/uploads

# Setup database
cd foodshare-app

# Run migrations
python migrate_add_replies.py

# Run additional migration if it exists
if [ -f "migrate_profiles.py" ]; then
    python migrate_profiles.py
fi

echo "✅ Build complete!"