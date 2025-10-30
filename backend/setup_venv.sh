#!/bin/bash
# ============================================================================
# VIRTUAL ENVIRONMENT SETUP SCRIPT
# Path: backend/setup_venv.sh
# ============================================================================

echo "🚀 Setting up Python virtual environment..."

# Navigate to backend directory
cd "$(dirname "$0")"

# Check if venv already exists
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists!"
    read -p "Do you want to delete and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing old venv..."
        rm -rf venv
    else
        echo "❌ Aborted."
        exit 1
    fi
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Check installation
echo ""
echo "✅ Installation complete!"
echo ""
echo "📊 Installed packages:"
pip list | grep -E "fastapi|langchain|supabase|google-generativeai"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Virtual environment setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate, run:"
echo "  deactivate"
echo ""
echo "To run the server:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"