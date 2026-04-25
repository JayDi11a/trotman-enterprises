#!/bin/bash
set -e

echo "======================================"
echo " Trotman Chat - Installation"
echo "======================================"
echo

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -q langchain langchain-openai langchain-ollama langchain-anthropic

# Make executable
echo "🔧 Making trotman-chat executable..."
chmod +x trotman-chat.py

# Create symlink for easy access
echo "🔗 Creating symlink..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p ~/bin
ln -sf "$SCRIPT_DIR/trotman-chat.py" ~/bin/trotman-chat

# Add ~/bin to PATH if not already there
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    echo ""
    echo "⚠️  Add ~/bin to your PATH by adding this to ~/.zshrc or ~/.bashrc:"
    echo "    export PATH=\"\$HOME/bin:\$PATH\""
    echo ""
fi

echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  trotman-chat                    # Use vLLM (local, zero cost)"
echo "  trotman-chat --provider ollama  # Use Ollama (local, zero cost)"
echo "  trotman-chat -q \"your question\"  # Single query mode"
echo ""
echo "Try it out:"
echo "  trotman-chat -q \"List all namespaces in my cluster\""
echo ""
