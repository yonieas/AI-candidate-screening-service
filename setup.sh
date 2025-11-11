#!/bin/bash
set -e

# Install system dependencies for ChromaDB
echo "Installing system dependencies..."
sudo apt-get install libsqlite3-dev -y

# Create Python virtual environment
if [ ! -d "venv" ]; then
	echo "Creating Python virtual environment..."
	python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
./venv/bin/pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
./venv/bin/pip install -r requirements.txt

# Copy .env from .env.example if not exists
if [ ! -f ".env" ]; then
	if [ -f ".env.example" ]; then
		echo "Copying .env.example to .env..."
		cp .env.example .env
		echo "Please update .env with your actual API keys and settings."
	else
		echo ".env.example not found. Please create your .env manually."
	fi
fi

echo ""
echo "Setup complete!"
echo "---------------------------------------------"
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo
echo "Before starting the server, run the ingest script to process source documents and create the local database:"
echo "  python ingest.py"
echo
echo "To start the server:"
echo "  uvicorn main:app --reload"
echo "---------------------------------------------"
