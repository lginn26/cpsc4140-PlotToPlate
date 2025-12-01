#!/bin/bash
# Quick setup script for FoodShare database seeding

echo "🌱 FoodShare Database Seeding Setup"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -f "seed_database.py" ]; then
    echo "❌ Error: seed_database.py not found!"
    echo "Please run this script from the seed_data directory:"
    echo "  cd foodshare-app/seed_data"
    echo "  ./quick_seed.sh"
    exit 1
fi

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 not found!"
    echo "Please install Python3 to continue."
    exit 1
fi

# Stop any running Flask app
echo "🛑 Stopping Flask app..."
pkill -f "python3 app.py" 2>/dev/null || true
sleep 1

# Run the seed script
echo ""
echo "🚀 Running seed script..."
echo ""
python3 seed_database.py

# Check if seeding was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Seeding completed successfully!"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Navigate to foodshare-app directory:"
    echo "      cd .."
    echo ""
    echo "   2. Start the Flask app:"
    echo "      python3 app.py"
    echo ""
    echo "   3. Open your browser to:"
    echo "      http://127.0.0.1:5000"
    echo ""
    echo "   4. Test with example users:"
    echo "      • sarah_gardener - Master Gardener"
    echo "      • mike_green - Community Gardener"
    echo "      • lisa_organics - Garden Coordinator"
    echo ""
else
    echo ""
    echo "❌ Seeding failed! Check the error messages above."
    exit 1
fi
