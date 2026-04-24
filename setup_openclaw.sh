#!/bin/bash
# OpenClaw Agent Setup Script for iPhone/iSH
# Install and configure OpenClaw agents for iPhone deployment

set -e

echo "╔════════════════════════════════════╗"
echo "║  OpenClaw Agent Setup for iPhone   ║"
echo "╚════════════════════════════════════╝"
echo

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check Python
echo -n "Checking Python... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python3 not found"
    echo "Install with: apt install python3 (on iSH)"
    exit 1
fi

# Setup directories
echo -n "Setting up directories... "
mkdir -p ~/.openclaw/{logs,config,scripts}
echo -e "${GREEN}✓${NC}"

# Create default config
echo -n "Creating configuration... "
cat > ~/.openclaw/config.json << 'EOF'
{
    "agent_name": "Genesis",
    "environment": "iphone",
    "max_retries": 3,
    "timeout": 30,
    "log_level": "INFO",
    "tools_enabled": ["shell", "file", "system"],
    "web": {
        "host": "0.0.0.0",
        "port": 5000,
        "debug": false
    }
}
EOF
echo -e "${GREEN}✓${NC}"

# Check Flask for web interface
echo -n "Checking Flask... "
if python3 -c "import flask" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Flask installed"
else
    echo -e "${YELLOW}⚠${NC} Flask not found"
    echo "Install with: pip3 install flask"
    read -p "Install now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip3 install flask
        echo -e "${GREEN}✓${NC} Flask installed"
    fi
fi

# Make scripts executable
echo -n "Setting permissions... "
chmod +x openclaw_agent.py openclaw_web.py 2>/dev/null || true
echo -e "${GREEN}✓${NC}"

# Create launcher script
echo -n "Creating launcher... "
cat > ~/.openclaw/launch.sh << 'EOF'
#!/bin/bash
# OpenClaw Agent Launcher

case "$1" in
    agent|terminal)
        python3 openclaw_agent.py --interactive
        ;;
    web|server)
        python3 openclaw_web.py --host 0.0.0.0 --port 5000
        ;;
    *)
        echo "Usage: launch.sh [agent|web]"
        echo ""
        echo "  agent  - Start interactive terminal agent"
        echo "  web    - Start web interface (http://localhost:5000)"
        ;;
esac
EOF
chmod +x ~/.openclaw/launch.sh
echo -e "${GREEN}✓${NC}"

# Display setup complete
echo
echo -e "${GREEN}═══════════════════════════════════${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════${NC}"
echo
echo "Configuration saved to: ~/.openclaw/"
echo
echo "Quick Start:"
echo "  1. Terminal Agent:    python3 openclaw_agent.py --interactive"
echo "  2. Web Interface:     python3 openclaw_web.py"
echo
echo "On iPhone:"
echo "  • iSH Terminal:  Run commands directly"
echo "  • Web Browser:   http://localhost:5000 (iSH) or http://<ip>:5000 (network)"
echo
