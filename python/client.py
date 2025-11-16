import socket
import subprocess
import os
import platform
import time

class RemoteAdminClient:
    def __init__(self, server_host, server_port=9001):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        
    def connect(self):
        """Connect to the server"""
        while True:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.server_host, self.server_port))
                print(f"[+] Connected to server at {self.server_host}:{self.server_port}")
                return True
            except Exception as e:
                print(f"[!] Connection failed: {e}")
                print("[+] Retrying in 5 seconds...")
                time.sleep(5)
    
    def send_hostname(self):
        """Send hostname to server"""
        try:
            hostname = platform.node()
            self.socket.send(hostname.encode() + b"\n")
        except Exception as e:
            print(f"[!] Error sending hostname: {e}")
    
    def execute_command(self, command):
        """Execute a command and return the output"""
        try:
            # Handle special commands
            if command.strip() == "PING":
                return "PONG"
            
            if command.strip() == "HOSTNAME":
                return platform.node()
            
            # Change directory command
            if command.strip().startswith("cd "):
                try:
                    path = command.strip()[3:].strip()
                    os.chdir(path)
                    return f"Changed directory to: {os.getcwd()}"
                except Exception as e:
                    return f"Error: {str(e)}"
            
            # Get current directory
            if command.strip() == "pwd":
                return os.getcwd()
            
            # Execute command
            if platform.system() == "Windows":
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    executable='/bin/bash'
                )
            
            output = result.stdout + result.stderr
            
            if not output:
                output = "[Command executed successfully with no output]"
            
            return output
            
        except subprocess.TimeoutExpired:
            return "[!] Command timeout (30 seconds)"
        except Exception as e:
            return f"[!] Error executing command: {str(e)}"
    
    def start(self):
        """Start the client and listen for commands"""
        if not self.connect():
            return
        
        # Send hostname first
        try:
            request = self.socket.recv(1024).decode().strip()
            if request == "HOSTNAME":
                self.send_hostname()
        except:
            pass
        
        print("[+] Client started. Waiting for commands...")
        
        while True:
            try:
                # Receive command from server
                self.socket.settimeout(60)
                command = self.socket.recv(4096).decode().strip()
                
                if not command:
                    print("[!] Connection lost")
                    break
                
                if command == "PING":
                    self.socket.send(b"PONG\n")
                    continue
                
                print(f"[+] Executing: {command}")
                
                # Execute the command
                output = self.execute_command(command)
                
                # Send response back to server
                response = output + "[CMD_END]"
                self.socket.send(response.encode())
                
            except socket.timeout:
                continue
            except ConnectionResetError:
                print("[!] Server disconnected")
                break
            except Exception as e:
                print(f"[!] Error: {e}")
                break
        
        # Try to reconnect
        print("[+] Attempting to reconnect...")
        self.socket.close()
        time.sleep(5)
        self.start()

if __name__ == "__main__":
    import sys
    
    server_ip = "localhost"

    print(f"[+] Starting Remote Administration Client")
    print(f"[+] Server: {server_ip}:9001")
    print(f"[+] Hostname: {platform.node()}")
    print(f"[+] Platform: {platform.system()}")
    
    client = RemoteAdminClient(server_ip)
    client.start()
