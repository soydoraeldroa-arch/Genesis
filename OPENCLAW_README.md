# OpenClaw Agent for iPhone

Complete setup guide for running OpenClaw agents on iPhone using iSH terminal or web interface.

## Overview

This package provides:
- **Terminal Agent**: Full command execution in iSH terminal
- **Web Interface**: Browser-based control accessible from iPhone Safari
- **Tool System**: Shell, file operations, and system info tools
- **Easy Setup**: One-command installation and configuration

## Getting Started

### Prerequisites

- iPhone with iSH app installed ([App Store](https://apps.apple.com/app/ish-shell/id1436902243))
- Python 3.6+ (usually pre-installed in iSH)
- Optional: Flask for web interface (`pip3 install flask`)

### Quick Setup

1. **On your iPhone in iSH:**

```bash
# Navigate to Genesis directory
cd ~/Genesis

# Run setup script
bash setup_openclaw.sh

# Or manual setup
mkdir -p ~/.openclaw/{logs,config,scripts}
```

2. **Start the agent:**

#### Option 1: Terminal Agent (Interactive)
```bash
python3 openclaw_agent.py --interactive
```

#### Option 2: Web Interface (Browser)
```bash
python3 openclaw_web.py --port 5000
```

Then open Safari and go to `http://localhost:5000`

## Usage

### Terminal Agent

**Interactive Mode:**
```bash
python3 openclaw_agent.py --interactive
```

Available commands:
- `run <cmd>` - Execute shell command
- `tool <name>` - Show tool information
- `status` - Show agent status
- `help` - Display help menu
- `exit` - Exit agent

**Examples:**
```
> run ls -la
> run pwd
> run whoami
> tool shell
> status
```

**Command Line Mode:**
```bash
# Execute single command
python3 openclaw_agent.py --run "ls -la"

# Show available tools
python3 openclaw_agent.py --tool
```

### Web Interface

**Start server:**
```bash
python3 openclaw_web.py --host 0.0.0.0 --port 5000
```

**Access from:**
- iPhone on same WiFi: `http://<your-iphone-ip>:5000`
- iSH terminal: `http://localhost:5000`
- macOS/desktop: `http://<iphone-ip>:5000`

**Features:**
- Execute shell commands
- Read/write files
- View system information
- Response display with syntax highlighting

### Tool Commands

#### Shell Commands
```bash
> run whoami
> run date
> run uname -a
> run ps aux
> run top -n 1
```

#### File Operations
```bash
> run cat ~/file.txt
> run echo "hello" > ~/test.txt
> run ls -lah ~
```

#### System Information
```bash
> run uname -a
> run df -h
> run free -h
```

## Directory Structure

```
~/.openclaw/
├── config.json      # Configuration file
├── logs/            # Agent logs
├── scripts/         # Custom scripts
└── launch.sh        # Quick launcher

~/Genesis/
├── openclaw_agent.py    # Terminal agent
├── openclaw_web.py      # Web interface
├── setup_openclaw.sh    # Setup script
└── OPENCLAW_README.md   # This file
```

## Configuration

Edit `~/.openclaw/config.json`:

```json
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
```

## Advanced Usage

### Running as Background Service

**Terminal multiplexer (tmux/screen):**
```bash
# Start in detached session
tmux new-session -d -s openclaw "python3 openclaw_web.py"

# View logs
tmux attach -t openclaw
```

### Custom Aliases

Add to your iSH shell profile:
```bash
# ~/.profile or ~/.bashrc
alias agent="python3 ~/Genesis/openclaw_agent.py --interactive"
alias agentd="python3 ~/Genesis/openclaw_web.py"
```

Then:
```bash
agent      # Start terminal agent
agentd     # Start web interface (daemon)
```

### Environment Variables

```bash
# Set timeout
export OPENCLAW_TIMEOUT=60

# Enable debug
export OPENCLAW_DEBUG=1

# Custom port
export OPENCLAW_PORT=8080
```

## Troubleshooting

### Flask Not Installed

```bash
pip3 install flask
# On iSH
pip3 install --break-system-packages flask
```

### Port Already in Use

```bash
# Use different port
python3 openclaw_web.py --port 8080
```

### iSH Terminal Issues

- Install required packages: `apk add python3 py3-pip`
- For networking: Ensure WiFi is connected
- Check iSH settings: Settings → Command → Enable SSH/networking

### Permissions

```bash
# Make scripts executable
chmod +x ~/.openclaw/launch.sh
chmod +x openslaw_agent.py openclaw_web.py
```

## Features & Capabilities

### Terminal Agent
✓ Execute shell commands  
✓ Interactive command loop  
✓ Error handling & retry logic  
✓ Command history  
✓ System information  
✓ File operations (read/write)  

### Web Interface
✓ Mobile-optimized UI  
✓ Real-time execution  
✓ System info display  
✓ File browser integration  
✓ Responsive design  
✓ Works on any iPhone browser  

### Tools
✓ Shell execution  
✓ File read/write  
✓ System info retrieval  
✓ Extensible tool framework  

## Network Access

### Local Network
If your iPhone and Mac are on same WiFi:

```bash
# On iSH, find your IP
ifconfig

# On Mac, access agent
open http://<iphone-ip>:5000
```

### Port Forwarding
Using SSH tunnel:
```bash
ssh -L 5000:localhost:5000 user@iphone.local
```

## Performance Tips

1. **Increase timeout for slow networks:**
   ```json
   {"timeout": 60}
   ```

2. **Disable debug mode in production:**
   ```json
   {"log_level": "ERROR"}
   ```

3. **Use web interface for large outputs** (better than scrolling terminal)

4. **Run in tmux for persistent sessions**

## Security Notes

⚠️ **Important:**
- Agent runs with your user privileges
- Be cautious with file operations
- Don't expose to untrusted networks
- Use firewall/VPN for remote access
- Consider authentication layer for deployment

## Examples

### System Monitoring Dashboard
```bash
# Run in web interface
# Execute: while true; do uname -a; df -h; free -h; sleep 5; done
```

### Backup Script
```bash
run tar -czf ~/backup.tar.gz ~/Documents
run ls -lh ~/backup.tar.gz
```

### Development Tools
```bash
run git status
run npm test
run python3 -m pytest
```

## Extending OpenClaw

Add custom tools in `openclaw_agent.py`:

```python
def call_tool(self, tool_name: str, **kwargs):
    if tool_name == "custom_tool":
        return self.my_custom_function(**kwargs)
    # ... existing tools
```

## Support & Issues

For issues or questions:
1. Check configuration: `cat ~/.openclaw/config.json`
2. Review logs: Check terminal output
3. Test connectivity: `run ping 8.8.8.8`
4. Restart agent: Exit and restart process

## License

Part of Genesis project. See LICENSE for details.

---

**Ready to use!** Start with:
```bash
python3 openclaw_agent.py --interactive
```

Enjoy your iPhone command center! 🚀
