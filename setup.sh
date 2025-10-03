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
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env template if not exists
if [ ! -f ".env" ]; then
	echo "Creating .env template..."
	echo 'GEMINI_API_KEY="YOUR_API_KEY"' > .env
	echo "Please update .env with your actual Gemini API key."
fi

echo "Setup complete. To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo
echo "Before starting the server, run the ingest script to process ground truth documents and create the local database:"
echo "  python ingest.py"
echo
echo "To start the server:"
echo "  uvicorn main:app --reload"
