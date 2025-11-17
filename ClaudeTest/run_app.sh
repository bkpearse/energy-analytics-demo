#!/bin/bash
# Script to run the Analytics Chat application

echo "🚀 Starting AI Analytics Chat..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    echo "Run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo "Run: cp .env.example .env and configure it"
    exit 1
fi

# Run Streamlit app
streamlit run app/main.py
