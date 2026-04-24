# Genesis

A collection of powerful command-line tools written in Python for terminal automation, mobile control, and data manipulation.

---

## 🎯 OpenClaw Agent - iPhone Edition ⭐ PRIMARY TOOL

**Complete agent environment for running commands on iPhone with iSH terminal or web interface. Execute shell commands, manage files, and monitor your system from any device.**

### Description

OpenClaw Agent is a lightweight, feature-rich command execution framework designed to work seamlessly on iPhone via iSH (a Linux terminal emulator) or any Unix-like system. It provides two interfaces:

1. **Terminal Agent** - SSH-like interactive command execution
2. **Web Interface** - Mobile-optimized browser UI for Safari

Perfect for:
- Personal iPhone command center
- Remote server management
- Development and testing
- System monitoring and automation
- Cross-device control

### Key Features

✅ **Full Command Execution** - Run any shell command with error handling  
✅ **Terminal Interface** - Interactive mode with command history  
✅ **Web UI** - Mobile-optimized, touch-friendly design  
✅ **Tool System** - Shell, file operations, system information  
✅ **Configuration Management** - Customizable settings  
✅ **Network Access** - Share across devices on same network  
✅ **One-Click Setup** - Automated installation script  
✅ **Comprehensive Docs** - 2000+ lines of documentation  

### Installation

#### Quick Setup (Recommended)
```bash
# Clone and enter directory
git clone https://github.com/soydoraeldroa-arch/Genesis.git
cd Genesis

# Run automated setup
bash setup_openclaw.sh

# Optional: Install Flask for web interface
pip3 install flask
```

#### Manual Setup
```bash
# Create directories
mkdir -p ~/.openclaw/{logs,config,scripts}

# Make scripts executable
chmod +x openclaw_agent.py openclaw_web.py
```

### User Manual

#### Mode 1: Terminal Agent (Interactive)

**Best for:** SSH-like experience, scripting, offline use

**Start interactive mode:**
```bash
python3 openclaw_agent.py --interactive
```

**Available Commands:**
| Command | Purpose |
|---------|---------|
| `run <cmd>` | Execute shell command |
| `status` | Show agent information |
| `tool <name>` | Display tool details |
| `help` | Show help menu |
| `exit` | Exit agent |

**Examples:**
```bash
> run whoami                    # Show current user
> run ls -la ~/Documents        # List files
> run pwd                       # Show directory
> run python3 script.py         # Run Python script
> run uname -a                  # System info
> run df -h                     # Disk space
> run git status                # Git status
> status                        # Show agent status
```

**Single Command Mode:**
```bash
python3 openclaw_agent.py --run "ls -la"
```

#### Mode 2: Web Interface (Browser)

**Best for:** Mobile use, file viewing, graphical interface

**Start server:**
```bash
python3 openclaw_web.py
```

**Access from:**
- iPhone on iSH: `http://localhost:5000`
- Same network: `http://<your-ip>:5000`

**Features in Web UI:**
- 🔧 **Execute Commands** - Run shell commands with real-time output
- 📁 **File Operations** - Read and write files
- 💾 **System Info** - View system information
- 📊 **Output Display** - View large command outputs
- 📱 **Mobile Friendly** - Optimized for touch input

**Using the Web Interface:**
1. Enter command in "Execute Command" section
2. Click "Run Command"
3. View output in real-time
4. Use "File Operations" for file management
5. Click "Get System Info" for system details

#### Mode 3: On iPhone with iSH

**Step-by-step:**
1. Install iSH app from App Store
2. Install dependencies: `apk add python3 py3-pip`
3. Clone repository and run setup
4. Choose terminal or web interface
5. Start using!

**For detailed iPhone setup:** See [iPhone Setup Guide](iPhone_SETUP.md)

### Configuration

**Config file location:** `~/.openclaw/config.json`

**Default configuration:**
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

**Customizable options:**
- `timeout` - Command timeout in seconds (default: 30)
- `port` - Web server port (default: 5000)
- `log_level` - DEBUG, INFO, or ERROR
- `agent_name` - Custom agent name

### Common Tasks

**System Monitoring:**
```bash
> run ps aux                    # List processes
> run top -n 1                  # Top processes
> run df -h                     # Disk usage
> run free -h                   # Memory usage
```

**File Management:**
```bash
> run ls -lah                   # List files detailed
> run find . -name "*.log"      # Find files
> run cat file.txt              # Read file
> run echo "text" > file.txt    # Write file
```

**Development:**
```bash
> run git status                # Git status
> run npm test                  # NPM tests
> run python3 -m pytest         # Python tests
> run curl https://api.example.com  # API calls
```

**Administration:**
```bash
> run whoami                    # Current user
> run date                      # Date/time
> run uptime                    # System uptime
> run uname -a                  # OS details
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Python not found | `apk add python3 py3-pip` (on iSH) |
| Flask not installed | `pip3 install flask` |
| Port already in use | Use `--port 8080` flag |
| Permission denied | `chmod +x openclaw_agent.py` |
| Command timeout | Increase `timeout` in config.json |

### Documentation

- 📖 **[Full Documentation](OPENCLAW_README.md)** - Complete reference guide (700+ lines)
- 📱 **[iPhone Setup Guide](iPhone_SETUP.md)** - Step-by-step instructions (550+ lines)
- ⚡ **[Quick Reference](QUICKREF.md)** - Commands and tips (350+ lines)
- 🏗️ **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - Technical details

---

## 📋 Terminal Agent (Original)

Simple command executor that reads from stdin.

**Usage:**
```bash
python3 agent.py
```

Or executable mode:
```bash
chmod +x agent.py
./agent.py
```

Reads commands from stdin (one per line), executes them, and handles errors with automatic retries.

---

## 🎨 Emoji Hide Tool

`emoji_hide.py` provides emoji steganography - hide and reveal text inside emoji strings using zero-width characters.

### Features

- 🔐 Encode text messages into emoji strings
- 🔍 Decode hidden messages from emoji strings
- 🌐 Web interface for easy use
- 💻 Command-line interface for scripting

### Usage

**Command Line:**
```bash
# Encode a message
python3 emoji_hide.py encode "secret message"

# Encode with custom cover emoji
python3 emoji_hide.py encode "secret message" --cover "😀😃😄"

# Decode a message
python3 emoji_hide.py decode "<encoded emoji text>"

# Run self-test
python3 emoji_hide.py test
```

**Web Interface:**
```bash
python3 emoji_hide.py serve
```

Open the web interface at http://localhost:3000 and use the encode/decode forms. The default encoding uses a single emoji (`😀`) as the cover.

## Requirements

- **Python:** 3.6 or higher
- **Optional:** Flask (for web interface) - `pip3 install flask`
- **For iPhone:** iSH app from App Store
- **Disk Space:** ~50MB for full installation

---

## 🚀 Getting Started

### 1. Clone Repository
```bash
git clone https://github.com/soydoraeldroa-arch/Genesis.git
cd Genesis
```

### 2. Run Setup (Optional but Recommended)
```bash
bash setup_openclaw.sh
```

This will:
- Create configuration directory
- Set up file permissions
- Configure settings
- Create launcher scripts

### 3. Start Using

**Terminal Mode (No dependencies):**
```bash
python3 openclaw_agent.py --interactive
```

**Web Mode (Requires Flask):**
```bash
python3 openclaw_web.py
# Open http://localhost:5000
```

---

## 📂 Project Structure

```
Genesis/
├── openclaw_agent.py           Terminal agent
├── openclaw_web.py             Web interface
├── setup_openclaw.sh           Setup script
├── emoji_hide.py               Emoji steganography
├── agent.py                    Original agent
├── OPENCLAW_README.md          Full documentation
├── iPhone_SETUP.md             iPhone guide
├── QUICKREF.md                 Quick reference
└── README.md                   This file
```

---

## 💡 Quick Examples

### Monitor System
```bash
python3 openclaw_agent.py --interactive
> run uname -a
> run df -h
> run free -m
```

### Execute Python Script
```bash
> run python3 ~/my_script.py
> run python3 -m pytest
```

### Network Access
```bash
# On iPhone: Run web interface
python3 openclaw_web.py

# On Mac/Desktop: Access from same WiFi
# Open http://<iphone-ip>:5000
```

---

## 📞 Support

- **Full Docs:** See [OPENCLAW_README.md](OPENCLAW_README.md)
- **iPhone Setup:** See [iPhone_SETUP.md](iPhone_SETUP.md)  
- **Quick Ref:** See [QUICKREF.md](QUICKREF.md)
- **Issues:** Create GitHub issue with Python version and OS

---

## 📜 License

[Add license information here]
