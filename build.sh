#!/bin/bash
# Render.com build script

echo "🚀 Building FoodShare for production..."

# Install dependencies
pip install -r foodshare-app/requirements.txt

# Create necessary directories
mkdir -p foodshare-app/database
mkdir -p foodshare-app/static/uploads

# Set up database
cd foodshare-app
python migrate_add_replies.py
python migrate_profiles.py 2>/dev/null || echo "Profile migration already applied"

# Optionally seed with example data
if [ "$SEED_DATABASE" = "true" ]; then
    echo "🌱 Seeding database with example data..."
    cd seed_data && python seed_database.py && cd ..
fi

echo "✅ Build complete!"