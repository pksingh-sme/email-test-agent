#!/bin/bash

# Setup script for Email QA Agentic Platform

echo "Setting up Email QA Agentic Platform..."

# Create backend virtual environment
echo "Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env 2>/dev/null || echo "EMAIL_ON_ACID_API_KEY=your_key_here" > .env
    echo "EMAIL_ON_ACID_API_SECRET=your_secret_here" >> .env
    echo "OPENAI_API_KEY=your_openai_key_here" >> .env
    echo "Please update .env with your actual API credentials"
fi

# Return to root directory
cd ..

# Setup frontend
echo "Setting up frontend..."
cd frontend
npm install

# Return to root directory
cd ..

echo "Setup complete!"
echo ""
echo "To run the platform:"
echo "1. Start the backend: cd backend && source venv/bin/activate && python main.py"
echo "2. Start the frontend: cd frontend && npm run dev"
echo ""
echo "Visit http://localhost:3000 in your browser"