#!/usr/bin/env python3
"""
OpenClaw Agent for iPhone/iSH
A lightweight agent system designed to run on iOS via iSH terminal or web interface.
Supports command execution, tool calling, and agent reasoning.
"""

import subprocess
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading
import time

class OpenClawAgent:
    """Lightweight agent for iPhone deployment"""
    
    def __init__(self, name: str = "Genesis Agent", tools: Optional[List[str]] = None):
        self.name = name
        self.tools = tools or ["shell", "file", "system"]
        self.history = []
        self.running = False
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file or create default"""
        config_path = os.path.expanduser("~/.openclaw/config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {
            "agent_name": self.name,
            "max_retries": 3,
            "timeout": 30,
            "log_level": "INFO",
            "tools_enabled": self.tools
        }
    
    def execute_command(self, cmd: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute a shell command safely"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "timestamp": datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def read_file(self, filepath: str) -> Dict[str, Any]:
        """Read file content"""
        try:
            with open(os.path.expanduser(filepath), 'r') as f:
                content = f.read()
            return {
                "success": True,
                "content": content,
                "size": len(content),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """Write content to file"""
        try:
            path = os.path.expanduser(filepath)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            return {
                "success": True,
                "filepath": filepath,
                "size": len(content),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call a specific tool"""
        if tool_name == "shell":
            return self.execute_command(kwargs.get("cmd", ""))
        elif tool_name == "file_read":
            return self.read_file(kwargs.get("path", ""))
        elif tool_name == "file_write":
            return self.write_file(kwargs.get("path", ""), kwargs.get("content", ""))
        elif tool_name == "system_info":
            return self._get_system_info()
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            uname = subprocess.check_output(["uname", "-a"], text=True).strip()
            return {
                "success": True,
                "uname": uname,
                "python_version": sys.version,
                "cwd": os.getcwd(),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def process_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Process an action and return result"""
        tool = action.get("tool")
        params = action.get("params", {})
        
        result = self.call_tool(tool, **params)
        result["action"] = tool
        
        self.history.append({
            "action": action,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def start_interactive(self):
        """Start interactive mode"""
        self.running = True
        print(f"\n{self.name} - Interactive Mode")
        print("Commands: 'help', 'status', 'tool <name>', 'exit'")
        print("-" * 50)
        
        while self.running:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                elif user_input.lower() == "exit":
                    self.running = False
                elif user_input.lower() == "help":
                    self._show_help()
                elif user_input.lower() == "status":
                    self._show_status()
                elif user_input.startswith("tool "):
                    tool_cmd = user_input[5:].strip()
                    self._handle_tool_command(tool_cmd)
                elif user_input.startswith("run "):
                    cmd = user_input[4:].strip()
                    result = self.execute_command(cmd)
                    self._print_result(result)
                else:
                    print("Unknown command. Type 'help' for options.")
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'exit' to quit.")
            except Exception as e:
                print(f"Error: {e}")
        
        print("\nAgent stopped.")
    
    def _show_help(self):
        """Show help menu"""
        print("""
Available Commands:
  run <cmd>        - Execute shell command
  tool <name>      - Show tool info
  status           - Show agent status
  help             - Show this help
  exit             - Exit agent

Example:
  run ls -la
  tool shell
        """)
    
    def _show_status(self):
        """Show agent status"""
        print(f"""
Agent Status:
  Name: {self.name}
  Running: {self.running}
  Tools: {', '.join(self.tools)}
  History: {len(self.history)} actions
  Uptime: {datetime.now().isoformat()}
        """)
    
    def _handle_tool_command(self, cmd: str):
        """Handle tool command"""
        if cmd in self.tools:
            print(f"Tool: {cmd}")
            if cmd == "shell":
                print("  Execute shell commands")
            elif cmd == "file":
                print("  Read/write files")
            elif cmd == "system":
                info = self._get_system_info()
                if info.get("success"):
                    print(f"  System: {info.get('uname', 'N/A')}")
        else:
            print(f"Unknown tool: {cmd}")
    
    def _print_result(self, result: Dict[str, Any]):
        """Print result nicely"""
        if result.get("success"):
            print("✓ Success")
            if "stdout" in result:
                print(result["stdout"])
        else:
            print("✗ Failed")
            if "error" in result:
                print(f"Error: {result['error']}")
            if "stderr" in result:
                print(result["stderr"])


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw Agent for iPhone/iSH")
    parser.add_argument("--name", default="Genesis Agent", help="Agent name")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive mode")
    parser.add_argument("--run", help="Run a command")
    parser.add_argument("--tool", help="Call a specific tool")
    
    args = parser.parse_args()
    
    agent = OpenClawAgent(name=args.name)
    
    if args.interactive:
        agent.start_interactive()
    elif args.run:
        result = agent.execute_command(args.run)
        agent._print_result(result)
    elif args.tool:
        print(f"Available tools: {', '.join(agent.tools)}")
    else:
        agent.start_interactive()


if __name__ == "__main__":
    main()
