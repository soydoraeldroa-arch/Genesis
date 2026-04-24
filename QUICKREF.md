# OpenClaw Agent - Quick Reference

## TL;DR Installation

```bash
# 1. In iSH on iPhone
apk add python3 py3-pip

# 2. Get the code
git clone https://github.com/soydoraeldroa-arch/Genesis.git
cd Genesis

# 3. Run setup
bash setup_openclaw.sh

# 4A. Terminal Agent (no dependencies)
python3 openclaw_agent.py --interactive

# 4B. Web Interface (better UI)
pip3 install --break-system-packages flask
python3 openclaw_web.py
# Then open Safari to http://localhost:5000
```

---

## Files Created

| File | Purpose |
|------|---------|
| `openclaw_agent.py` | Terminal-based agent, interactive mode |
| `openclaw_web.py` | Web interface, mobile-optimized UI |
| `setup_openclaw.sh` | One-command setup script |
| `OPENCLAW_README.md` | Full documentation |
| `iPhone_SETUP.md` | iPhone/iSH step-by-step guide |
| `QUICKREF.md` | This file |

---

## Usage Modes

### 1️⃣ Terminal Agent
```bash
python3 openclaw_agent.py --interactive
```
**When to use:** SSH-like experience, scripting, offline

**Commands:**
```
run <cmd>        Execute command
status           Show agent info
tool <name>      Show tool details
help             Display menu
exit             Quit
```

**Examples:**
```
> run whoami
> run ls -la
> run python3 script.py
> run date
```

---

### 2️⃣ Web Interface
```bash
pip3 install --break-system-packages flask
python3 openclaw_web.py
# Safari: http://localhost:5000
```
**When to use:** Mobile interface, sharing, large outputs, file operations

**Features:**
- Execute commands
- Read/write files
- System info
- Mobile-optimized UI

---

### 3️⃣ One-off Commands
```bash
python3 openclaw_agent.py --run "whoami"
python3 openclaw_agent.py --run "ls -la"
```

---

## Common Commands

### System Info
```bash
> run uname -a          # OS info
> run whoami            # Current user
> run pwd               # Current directory
> run date              # Date/time
> run df -h             # Disk space
> run free -h           # Memory usage
```

### File Operations
```bash
> run ls -la            # List files
> run cat file.txt      # Read file
> run echo "x" > f.txt  # Write file
> run find . -name "*.py"  # Find files
> run rm file.txt       # Delete file
```

### Development
```bash
> run python3 script.py
> run git status
> run npm test
> run curl https://api.example.com
```

---

## Configuration

**Location:** `~/.openclaw/config.json`

```json
{
    "agent_name": "Genesis",
    "timeout": 30,
    "tools_enabled": ["shell", "file", "system"]
}
```

**Key settings:**
- `timeout`: Command timeout in seconds
- `log_level`: DEBUG, INFO, ERROR
- `web.port`: Change from 5000 to custom port

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Python not found | `apk add python3 py3-pip` |
| Flask error | `pip3 install --break-system-packages flask` |
| Port in use | Use `--port 8080` |
| Permission denied | `chmod +x openclaw_agent.py` |
| Command timeout | Increase `timeout` in config |
| Connection refused | Ensure iSH has internet access |

---

## Tips & Tricks

### Keep Running in Background
```bash
tmux new-session -d -s openclaw "python3 openclaw_web.py"
```

### Create Alias
```bash
# Add to ~/.profile
alias agent="python3 ~/Genesis/openclaw_agent.py --interactive"
alias agentd="python3 ~/Genesis/openclaw_web.py"
```
Then: `agent` or `agentd`

### Access from Mac/Desktop
1. Both on same WiFi
2. In iSH: `python3 openclaw_web.py`
3. On Mac: `http://<iphone-ip>:5000`
4. Find IP: `> run ifconfig`

### Redirect Output
```bash
> run echo "hello" > ~/output.txt
> run command > ~/log.txt 2>&1
```

---

## Architecture

```
openclaw_agent.py
├── Core Agent Class
├── Tool System (shell, file, system)
├── Interactive Mode
└── Command Executor

openclaw_web.py
├── Flask Server
├── REST API (/api/execute, /api/read, /api/write)
├── Mobile HTML UI
└── WebSocket Support
```

---

## Security Considerations

- ⚠️ Agent runs with your user permissions
- Don't run untrusted scripts
- Be careful with file deletion
- Use VPN for remote network access
- Consider rate limiting for public access

---

## Development

Add custom tools to `openclaw_agent.py`:

```python
def call_tool(self, tool_name: str, **kwargs):
    if tool_name == "my_tool":
        return self.my_custom_function(**kwargs)
    # ...

def my_custom_function(self):
    # Your code here
    return {"success": True, "data": "..."}
```

---

## Project Structure

```
Genesis/
├── openclaw_agent.py      ⭐ Main agent
├── openclaw_web.py        ⭐ Web UI
├── setup_openclaw.sh      ⭐ Setup script
├── emoji_hide.py          (Existing)
├── agent.py               (Existing)
├── OPENCLAW_README.md     📖 Full docs
├── iPhone_SETUP.md        📖 iPhone guide
└── QUICKREF.md            📖 This file
```

---

## API Reference

### Terminal Agent API
```python
agent = OpenClawAgent(name="MyAgent")
result = agent.execute_command("ls -la")
result = agent.read_file("~/file.txt")
agent.process_action({"tool": "shell", "params": {"cmd": "pwd"}})
```

### Web API
```
POST /api/execute       {"cmd": "..."}
POST /api/read          {"path": "..."}
POST /api/write         {"path": "...", "content": "..."}
GET  /api/system-info   →  {}
```

---

## Performance Benchmarks

On iPhone 12, iSH:
- Simple command: ~100-500ms
- File read (1MB): ~1-2s
- Python script: depends on script
- Web UI render: ~500ms

---

## Next Steps

1. ✅ **Install:** Follow Installation section
2. ✅ **Choose mode:** Terminal or web
3. ✅ **Test:** Run `> run whoami`
4. ✅ **Customize:** Edit config.json
5. ✅ **Extend:** Add custom tools

---

## Support

📖 **Full Documentation:** See `OPENCLAW_README.md`  
📱 **iPhone Setup:** See `iPhone_SETUP.md`  
🐛 **Issues:** GitHub issues  
💬 **Questions:** Check FAQ in full docs  

---

## Version Info

- **OpenClaw Agent:** v1.0
- **Python Required:** 3.6+
- **Dependencies:** flask (optional, for web UI)
- **Platform:** iPhone (iSH), any Linux/Unix

---

**Ready to start?**
```bash
python3 openclaw_agent.py --interactive
```

Enjoy! 🚀
