#!/bin/bash
set -e

echo "======================================"
echo " Trotman Chat - UV Installation"
echo "======================================"
echo

# Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "✅ uv already installed"
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create venv and install dependencies
echo "🔧 Creating virtual environment with uv..."
uv venv

echo "📦 Installing dependencies with uv..."
uv pip install -r requirements.txt

# Create wrapper script
echo "🔗 Creating wrapper script..."
cat > trotman-chat-uv.sh << EOF
#!/bin/bash
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
source "\$SCRIPT_DIR/.venv/bin/activate"
python "\$SCRIPT_DIR/trotman-chat.py" "\$@"
EOF

chmod +x trotman-chat-uv.sh

# Update symlink to use uv version
mkdir -p ~/bin
ln -sf "$SCRIPT_DIR/trotman-chat-uv.sh" ~/bin/trotman-chat

echo ""
echo "✅ Installation complete with uv!"
echo ""
echo "Benefits:"
echo "  ⚡ 10-100x faster dependency installs"
echo "  🔒 Isolated virtual environment"
echo "  📦 Better dependency resolution"
echo ""
echo "Usage:"
echo "  trotman-chat --provider llama     # Llama 3.1 (function calling)"
echo "  trotman-chat --provider mistral   # Mistral (function calling)"
echo "  trotman-chat --provider hermes    # Hermes (function calling)"
echo ""
