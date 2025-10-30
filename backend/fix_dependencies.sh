#!/bin/bash
# ============================================================================
# FIX DEPENDENCY CONFLICT
# Path: backend/fix_dependencies.sh
# ============================================================================

echo "🔧 FIXING DEPENDENCY CONFLICT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Make sure we're in backend directory
cd "$(dirname "$0")"

# Check if venv is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated!"
    echo ""
    echo "Please run:"
    echo "  source venv/bin/activate"
    echo ""
    exit 1
fi

echo "✅ Virtual environment detected: $VIRTUAL_ENV"
echo ""

# Uninstall conflicting packages
echo "🗑️  Uninstalling old packages..."
pip uninstall -y langchain langchain-core langchain-groq langchain-community pydantic langsmith 2>/dev/null

echo ""
echo "📦 Installing compatible versions..."
pip install --upgrade pip

# Install new requirements
pip install -r requirements.txt

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Dependencies fixed!"
echo ""
echo "📊 Installed versions:"
pip show langchain langchain-core langchain-groq pydantic | grep -E "Name|Version"

echo ""
echo "🚀 Now try running:"
echo "  python main.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"