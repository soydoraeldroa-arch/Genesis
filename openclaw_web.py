#!/usr/bin/env python3
"""
OpenClaw Web Interface for iPhone
Lightweight Flask-based web UI accessible from iPhone browser
Works with iSH or any remote server
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
import subprocess
import threading

try:
    from flask import Flask, render_template_string, request, jsonify
except ImportError:
    print("Flask not installed. Install with: pip install flask")
    print("For iSH: pip3 install flask")
    exit(1)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw Agent</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 10px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 600px;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        .content {
            padding: 20px;
        }
        .section {
            margin-bottom: 20px;
        }
        .section h2 {
            font-size: 16px;
            margin-bottom: 10px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 5px;
        }
        .input-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 5px;
            color: #555;
        }
        input, textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 13px;
            font-family: 'Monaco', 'Courier New', monospace;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        textarea {
            resize: vertical;
            min-height: 80px;
        }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:active {
            transform: scale(0.98);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .output {
            background: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 12px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            color: #333;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .output.success {
            border-left: 4px solid #22c55e;
        }
        .output.error {
            border-left: 4px solid #ef4444;
            color: #ef4444;
        }
        .spinner {
            display: inline-block;
            width: 14px;
            height: 14px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 8px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .button-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        .status {
            background: #f0f4ff;
            border-left: 4px solid #667eea;
            padding: 10px;
            border-radius: 4px;
            font-size: 12px;
            color: #555;
            margin-bottom: 15px;
        }
        .tool-list {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        .tool-btn {
            padding: 10px;
            font-size: 12px;
            background: #f0f4ff;
            color: #667eea;
            border: 1px solid #667eea;
        }
        .tool-btn:active {
            background: #667eea;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 OpenClaw Agent</h1>
            <p>iPhone-Optimized Command Interface</p>
        </div>
        
        <div class="content">
            <div class="status" id="status">Ready</div>
            
            <!-- Command Execution -->
            <div class="section">
                <h2>Execute Command</h2>
                <div class="input-group">
                    <label for="command">Command:</label>
                    <input type="text" id="command" placeholder="e.g., ls -la, pwd, whoami">
                </div>
                <button onclick="executeCommand()" id="execBtn">Run Command</button>
                <div id="execOutput" style="margin-top: 10px;"></div>
            </div>
            
            <!-- File Operations -->
            <div class="section">
                <h2>File Operations</h2>
                <div class="input-group">
                    <label for="filePath">File Path:</label>
                    <input type="text" id="filePath" placeholder="e.g., ~/test.txt">
                </div>
                <div class="button-group">
                    <button onclick="readFile()">Read File</button>
                    <button onclick="showWriteDialog()">Write File</button>
                </div>
                <div id="fileOutput" style="margin-top: 10px;"></div>
            </div>
            
            <!-- System Info -->
            <div class="section">
                <h2>System Info</h2>
                <button onclick="getSystemInfo()">Get System Info</button>
                <div id="sysOutput" style="margin-top: 10px;"></div>
            </div>
            
            <!-- Tools -->
            <div class="section">
                <h2>Available Tools</h2>
                <div class="tool-list">
                    <button class="tool-btn" onclick="showTool('shell')">Shell</button>
                    <button class="tool-btn" onclick="showTool('file')">Files</button>
                    <button class="tool-btn" onclick="showTool('system')">System</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        function updateStatus(msg, type = 'info') {
            const status = document.getElementById('status');
            status.textContent = msg;
            status.style.borderLeftColor = type === 'error' ? '#ef4444' : '#667eea';
        }

        async function executeCommand() {
            const cmd = document.getElementById('command').value;
            if (!cmd) return;
            
            const btn = document.getElementById('execBtn');
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span>Executing...';
            
            try {
                const response = await fetch('/api/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({cmd})
                });
                const result = await response.json();
                displayOutput('execOutput', result);
                updateStatus('✓ Command executed');
            } catch (e) {
                displayOutput('execOutput', {error: e.message}, 'error');
                updateStatus('✗ Error', 'error');
            } finally {
                btn.disabled = false;
                btn.innerHTML = 'Run Command';
            }
        }

        async function readFile() {
            const path = document.getElementById('filePath').value;
            if (!path) return;
            
            try {
                const response = await fetch('/api/read', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({path})
                });
                const result = await response.json();
                displayOutput('fileOutput', result);
                updateStatus('✓ File read');
            } catch (e) {
                displayOutput('fileOutput', {error: e.message}, 'error');
                updateStatus('✗ Error', 'error');
            }
        }

        function showWriteDialog() {
            const path = document.getElementById('filePath').value;
            if (!path) return;
            const content = prompt('Enter file content:');
            if (content !== null) writeFile(path, content);
        }

        async function writeFile(path, content) {
            try {
                const response = await fetch('/api/write', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({path, content})
                });
                const result = await response.json();
                displayOutput('fileOutput', result);
                updateStatus('✓ File written');
            } catch (e) {
                displayOutput('fileOutput', {error: e.message}, 'error');
                updateStatus('✗ Error', 'error');
            }
        }

        async function getSystemInfo() {
            try {
                const response = await fetch('/api/system-info');
                const result = await response.json();
                displayOutput('sysOutput', result);
                updateStatus('✓ System info retrieved');
            } catch (e) {
                displayOutput('sysOutput', {error: e.message}, 'error');
                updateStatus('✗ Error', 'error');
            }
        }

        function showTool(tool) {
            alert(`Tool: ${tool}\nAvailable in command interface`);
        }

        function displayOutput(elementId, data, type = null) {
            const elem = document.getElementById(elementId);
            const output = document.createElement('div');
            output.className = 'output ' + (data.error ? 'error' : 'success');
            
            let text = '';
            if (data.stdout) text += data.stdout;
            if (data.stderr) text += (text ? '\n' : '') + data.stderr;
            if (data.error) text = 'Error: ' + data.error;
            if (data.content) text = data.content;
            if (data.uname) text = data.uname;
            
            output.textContent = text || JSON.stringify(data, null, 2);
            elem.innerHTML = '';
            elem.appendChild(output);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/execute', methods=['POST'])
def execute():
    data = request.json
    cmd = data.get('cmd', '')
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return jsonify({
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Command timed out"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/read', methods=['POST'])
def read():
    data = request.json
    path = os.path.expanduser(data.get('path', ''))
    
    try:
        with open(path, 'r') as f:
            content = f.read()
        return jsonify({
            "success": True,
            "content": content,
            "size": len(content)
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/write', methods=['POST'])
def write():
    data = request.json
    path = os.path.expanduser(data.get('path', ''))
    content = data.get('content', '')
    
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return jsonify({
            "success": True,
            "filepath": path,
            "size": len(content)
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/system-info')
def system_info():
    try:
        uname = subprocess.check_output(["uname", "-a"], text=True).strip()
        return jsonify({
            "success": True,
            "uname": uname,
            "python_version": __import__('sys').version,
            "cwd": os.getcwd()
        })
    except Exception as e:
        return jsonify({"error": str(e)})

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw Web Interface")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    print(f"""
╔════════════════════════════════════╗
║     OpenClaw Web Interface         ║
╚════════════════════════════════════╝

Starting server on http://{args.host}:{args.port}

Access from iPhone:
  - On same network: http://<your-ip>:{args.port}
  - On iSH: http://localhost:{args.port}

Press Ctrl+C to stop.
    """)
    
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()
