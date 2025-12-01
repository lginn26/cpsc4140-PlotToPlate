# FoodShare Application Makefile
# For School of Computing Linux environments

PYTHON = python3
PIP = pip3
APP_DIR = foodshare-app
VENV_DIR = $(APP_DIR)/venv
PYTHON_VENV = $(VENV_DIR)/bin/python
PIP_VENV = $(VENV_DIR)/bin/pip

.PHONY: help install run clean test migrate setup example deploy

# Default target - show help
help:
	@echo "FoodShare Application - Available Commands"
	@echo "=========================================="
	@echo "make setup      - Complete setup (venv + dependencies + database)"
	@echo "make install    - Install all dependencies"
	@echo "make migrate    - Run database migrations"
	@echo "make run        - Start the Flask application"
	@echo "make example    - Populate database with example data for testing"
	@echo "make deploy     - Test production deployment locally"
	@echo "make clean      - Remove virtual environment and cache files"
	@echo "make test       - Run application tests"
	@echo ""
	@echo "Quick Start:"
	@echo "  1. make setup"
	@echo "  2. make example    (optional - adds test data)"
	@echo "  3. make run"
	@echo "  4. Open browser to http://localhost:5000"

# Complete setup - creates venv, installs dependencies, sets up database
setup: clean
	@echo "Setting up FoodShare application..."
	@echo "1. Creating virtual environment..."
	cd $(APP_DIR) && $(PYTHON) -m venv venv
	@echo "2. Installing dependencies..."
	$(PIP_VENV) install --upgrade pip
	$(PIP_VENV) install -r $(APP_DIR)/requirements.txt
	@echo "3. Setting up database..."
	cd $(APP_DIR) && venv/bin/python migrate_add_replies.py
	@echo ""
	@echo "✓ Setup complete! Run 'make run' to start the application."

# Install dependencies only (assumes venv exists)
install:
	@echo "Installing dependencies..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(PIP_VENV) install --upgrade pip
	$(PIP_VENV) install -r $(APP_DIR)/requirements.txt
	@echo "✓ Dependencies installed."

# Run database migrations
migrate:
	@echo "Running database migrations..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	cd $(APP_DIR) && venv/bin/python migrate_add_replies.py
	@echo "✓ Migrations complete."

# Start the Flask application
run:
	@echo "Starting FoodShare application..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Application will be available at: http://localhost:5000"
	@echo "Press Ctrl+C to stop the server"
	@echo ""
	cd $(APP_DIR) && venv/bin/python app.py

# Clean up virtual environment and cache files
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleanup complete."

# Run tests (placeholder for future test implementation)
test:
	@echo "Running tests..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Test suite not yet implemented."

# Check if database exists
check-db:
	@if [ -f "$(APP_DIR)/database/foodshare.db" ]; then \
		echo "✓ Database exists"; \
	else \
		echo "✗ Database not found. Run 'make setup' or 'make migrate'"; \
		exit 1; \
	fi

# Populate database with example data for testing
example:
	@echo "Populating database with example data..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@if [ ! -f "$(APP_DIR)/database/foodshare.db" ]; then \
		echo "Database not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "This will clear existing data and add example users, gardens, and posts."
	@read -p "Continue? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		cd $(APP_DIR)/seed_data && ../venv/bin/python seed_database.py; \
		echo ""; \
		echo "✓ Example data added successfully!"; \
		echo ""; \
		echo "Test Users:"; \
		echo "  • sarah_gardener - Master Gardener"; \
		echo "  • mike_green - Community Gardener"; \
		echo "  • lisa_organics - Garden Coordinator"; \
		echo "  • john_novice - Garden Volunteer"; \
		echo "  • emma_harvest - Community Gardener"; \
	else \
		echo "Cancelled."; \
	fi

# Test production deployment locally
deploy:
	@echo "Testing production deployment locally..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Installing production dependencies..."
	$(PIP_VENV) install gunicorn
	@echo ""
	@echo "🚀 Starting production server..."
	@echo "Application will be available at: http://localhost:8000"
	@echo "Press Ctrl+C to stop the server"
	@echo ""
	cd $(APP_DIR) && venv/bin/gunicorn --bind 127.0.0.1:8000 wsgi:app
