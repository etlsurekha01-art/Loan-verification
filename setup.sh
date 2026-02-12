#!/bin/bash
# Quick start script for the Agentic AI Loan Verification System

echo "=================================================="
echo "  Agentic AI Loan Verification System Setup"
echo "=================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

echo "✓ Python detected: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✓ All dependencies installed"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your GEMINI_API_KEY"
    echo "   You can get one from: https://makersuite.google.com/app/apikey"
    echo ""
    echo "   The system will work without it, but AI features will use fallback logic."
    echo ""
else
    echo "✓ .env file exists"
    echo ""
fi

echo "=================================================="
echo "  Setup Complete!"
echo "=================================================="
echo ""
echo "To start the server:"
echo "  source venv/bin/activate"
echo "  uvicorn main:app --reload"
echo ""
echo "To run tests:"
echo "  python test_system.py"
echo ""
echo "API will be available at:"
echo "  http://localhost:8000/docs"
echo ""
