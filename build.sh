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

# Populate database with seed data
echo "🌱 Seeding database with sample data..."
if [ -f "seed_data/seed_database.py" ]; then
    python seed_data/seed_database.py
    echo "✅ Database seeded successfully!"
else
    echo "⚠️  Seed script not found, skipping database seeding"
fi

echo "✅ Build complete!"