# OpenClaw Agent - iPhone Setup Guide

Step-by-step instructions for setting up OpenClaw agents on iPhone using iSH.

## Installation Steps

### Step 1: Install iSH

1. Open App Store on your iPhone
2. Search for "iSH"
3. Install iSH Shell (by iSH contributors)
4. Open iSH app

### Step 2: Initial System Setup

In iSH terminal, run:

```bash
# Update package manager
apk update
apk upgrade

# Install Python and dependencies
apk add python3 py3-pip git

# Verify installation
python3 --version
pip3 --version
```

### Step 3: Clone/Download Genesis

```bash
# Clone repository (requires git)
git clone https://github.com/soydoraeldroa-arch/Genesis.git
cd Genesis

# OR download files directly
cd ~
mkdir Genesis
cd Genesis
# Copy openclaw_agent.py and openclaw_web.py here
```

### Step 4: Run Setup Script

```bash
bash setup_openclaw.sh
```

This will:
- Create ~/.openclaw directory
- Generate config.json
- Set permissions
- Create launcher script

### Step 5: Install Optional Dependencies

For web interface (recommended):

```bash
pip3 install flask
# Or on iSH with restrictions:
pip3 install --break-system-packages flask
```

---

## Quick Start Options

### ✅ Option 1: Terminal Rcliff Agent (Simplest)

No dependencies needed!

```bash
cd ~/Genesis
python3 openclaw_agent.py --interactive
```

Commands:
```
> run whoami
> run ls -la
> run pwd
> run date
> status
> exit
```

**Perfect for:**
- Quick command execution
- SSH-like experience
- Works offline

---

### ✅ Option 2: Web Interface (Most User-Friendly)

Requires Flask.

```bash
# Install Flask (one time)
pip3 install --break-system-packages flask

# Start web server
cd ~/Genesis
python3 openclaw_web.py
```

Then open Safari:
```
http://localhost:5000
```

**Perfect for:**
- Graphical interface
- Multiple operations at once
- Better for file viewing
- Share with other apps

---

### ✅ Option 3: Split View (Best of Both)

Use iSH split view with web:

1. Open iSH
2. Swipe from left edge to show split view menu
3. Open Safari in split view
4. In iSH: `python3 openclaw_web.py`
5. In Safari: Open `http://localhost:5000`

**Perfect for:**
- Monitoring + control
- Drag & drop files (if supported)
- Multitasking

---

## Common Tasks

### Check System Info

**Terminal:**
```
> run uname -a
> run df -h
> run date
```

**Web Interface:**
Click "Get System Info" button

### Run Python Script

**Terminal:**
```
> run python3 ~/my_script.py
```

**Web Interface:**
Execute command: `python3 ~/my_script.py`

### List Files

**Terminal:**
```
> run ls -lah ~/
```

**Web Interface:**
Execute command: `find ~/ -type f | head -20`

### Create a File

**Terminal:**
```
> run echo "Hello World" > ~/test.txt
```

**Web Interface:**
- Click "Write File"
- Path: `~/test.txt`
- Content: `Hello World`

### Install Python Package

```bash
pip3 install --break-system-packages <package>
```

---

## Network Access

### Local Network
Find your iPhone's IP:
```
> run ifconfig
```

Look for inet address (e.g., 192.168.1.100)

### Share Agent with Mac/Desktop
1. Both on same WiFi
2. Run web interface: `python3 openclaw_web.py`
3. On desktop: `http://<iphone-ip>:5000`

### Port Forwarding via SSH
```bash
# From your Mac
ssh -L 5000:localhost:5000 -D 1080 ubuntu@your-iphone
# Then access: http://localhost:5000
```

---

## Keyboard Shortcuts (Terminal)

In iSH, useful shortcuts:
- `Ctrl+A` - Move to start of line
- `Ctrl+E` - Move to end of line
- `Ctrl+U` - Clear line
- `Ctrl+C` - Interrupt command
- `Ctrl+D` - Exit (or type `exit`)
- `↑/↓` - Command history

---

## Settings & Customization

### Change Port

```bash
python3 openclaw_web.py --port 8080
```

Then access: `http://localhost:8080`

### Enable Debug Mode

```bash
python3 openclaw_web.py --debug
```

### Change Timeout (for slow connections)

Edit `~/.openclaw/config.json`:
```json
"timeout": 60
```

### Add Custom Tools

Edit `openclaw_agent.py` and add tool methods:
```python
def custom_tool(self, **kwargs):
    # Your code here
    return result
```

---

## Troubleshooting

### "command not found: python3"
```bash
apk add python3 py3-pip
```

### "No module named flask"
```bash
pip3 install --break-system-packages flask
```

### "Port 5000 already in use"
```bash
python3 openclaw_web.py --port 8080
```

### "Permission denied"
```bash
chmod +x openclaw_agent.py openclaw_web.py
```

### Web interface not loading
1. Check server is running
2. Try `http://127.0.0.1:5000` instead
3. Check firewall settings
4. Restart iSH app

### Slow performance
- Close other apps
- Use simpler commands first
- Consider running on jailbroken device
- Use SSH tunnel for remote access

---

## Voice Control Integration (Optional)

With Siri Shortcuts, you can automate commands:

1. Open Shortcuts app
2. Create new shortcut  
3. Add "Open URL" action
4. URL: `http://localhost:5000/api/execute`
5. Method: POST
6. Body with command JSON

Example:
```
POST http://localhost:5000/api/execute
{
  "cmd": "ls -la"
}
```

---

## Persistence & Automation

### Keep Agent Running After Close

Use screen/tmux:
```bash
# Install tmux
apk add tmux

# Run in background
tmux new-session -d -s agent "python3 openclaw_web.py"

# Check status
tmux ls

# Reattach
tmux attach -t agent
```

### Auto-Start on iSH Launch

Add to `~/.profile`:
```bash
# Auto-start web interface
# python3 ~/Genesis/openclaw_web.py &
```

**Note:** Commented out by default (can slow startup)

---

## Performance Tips

1. **Use web interface for large outputs** - Terminal scrolling can be slow
2. **Increase timeout for network commands** - iSH can be slower
3. **Reduce log verbosity** - Set `log_level: ERROR` in config
4. **Close unnecessary apps** - Frees up memory
5. **Use simple commands** - Complex pipes can timeout

---

## Example Workflows

### Daily System Check
```bash
# In terminal agent
> run date
> run df -h
> run free -h
> run whoami
```

### File Management
```bash
> run ls -lah ~/Documents
> run find . -name "*.txt"
> run du -sh ~/*
```

### Development
```bash
> run git status
> run git log --oneline
> run python3 -m pytest
```

### Monitoring
```bash
# Keep running
> run watch -n 5 "ps aux"
```

---

## Security Reminders

⚠️ **Important:**
- Agent has your user's permissions
- Don't run untrusted scripts
- Be careful with file deletion
- Consider VPN for remote network access
- Limit who can access your iPhone

---

## Next Steps

1. ✅ Install iSH
2. ✅ Run setup_openclaw.sh
3. ✅ Choose terminal or web interface
4. ✅ Start executing commands!

**Get started:**
```bash
cd ~/Genesis
python3 openclaw_agent.py --interactive
```

**Enjoy your iPhone command center!** 🚀

---

## Additional Resources

- GitHub: https://github.com/soydoraeldroa-arch/Genesis
- iSH Documentation: https://github.com/ish-app/ish
- Python Docs: https://docs.python.org/3/

Need help? Create an issue on GitHub or check the main README.
