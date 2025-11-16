import socket
import threading
import sys
from datetime import datetime

class RemoteAdminServer:
    def __init__(self, host='0.0.0.0', port=9001):
        self.host = host
        self.port = port
        self.clients = {}  # {client_id: {'socket': socket, 'address': address, 'name': name}}
        self.client_counter = 0
        self.lock = threading.Lock()
        
    def start(self):
        """Start the server and listen for connections"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        
        print(f"[+] Server started on {self.host}:{self.port}")
        print("[+] Waiting for client connections...")
        
        # Start the command handler in a separate thread
        command_thread = threading.Thread(target=self.command_handler, daemon=True)
        command_thread.start()
        
        try:
            while True:
                client_socket, address = server.accept()
                self.handle_new_client(client_socket, address)
        except KeyboardInterrupt:
            print("\n[!] Server shutting down...")
            server.close()
            sys.exit(0)
    
    def handle_new_client(self, client_socket, address):
        """Handle a new client connection"""
        with self.lock:
            self.client_counter += 1
            client_id = self.client_counter
            
            # Get hostname from client
            try:
                client_socket.send(b"HOSTNAME\n")
                hostname = client_socket.recv(1024).decode().strip()
            except:
                hostname = "Unknown"
            
            self.clients[client_id] = {
                'socket': client_socket,
                'address': address,
                'name': hostname
            }
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[+] New client connected!")
            print(f"    ID: {client_id}")
            print(f"    Name: {hostname}")
            print(f"    Address: {address[0]}:{address[1]}")
            print(f"    Time: {timestamp}")
            
        # Start a thread to monitor this client
        monitor_thread = threading.Thread(
            target=self.monitor_client, 
            args=(client_id,),
            daemon=True
        )
        monitor_thread.start()
    
    def monitor_client(self, client_id):
        """Monitor client connection and handle disconnection"""
        client = self.clients.get(client_id)
        if not client:
            return
        
        try:
            # Keep connection alive
            while True:
                client['socket'].settimeout(30)
                # Send keepalive
                client['socket'].send(b"PING\n")
                response = client['socket'].recv(1024)
                if not response:
                    break
        except:
            pass
        
        # Client disconnected
        with self.lock:
            if client_id in self.clients:
                print(f"\n[!] Client {client_id} ({self.clients[client_id]['name']}) disconnected")
                try:
                    self.clients[client_id]['socket'].close()
                except:
                    pass
                del self.clients[client_id]
    
    def list_clients(self):
        """Display all connected clients"""
        if not self.clients:
            print("\n[!] No clients connected")
            return
        
        print("\n" + "="*70)
        print("Connected Clients:")
        print("="*70)
        print(f"{'ID':<5} {'Name':<20} {'Address':<20} {'Port':<10}")
        print("-"*70)
        
        with self.lock:
            for client_id, info in self.clients.items():
                name = info['name']
                address = info['address'][0]
                port = info['address'][1]
                print(f"{client_id:<5} {name:<20} {address:<20} {port:<10}")
        
        print("="*70)
    
    def interact_with_client(self, client_id):
        """Start interactive shell with a specific client"""
        with self.lock:
            if client_id not in self.clients:
                print(f"[!] Client {client_id} not found")
                return
            
            client = self.clients[client_id]
            client_socket = client['socket']
            client_name = client['name']
        
        print(f"\n[+] Starting interactive session with {client_name} (ID: {client_id})")
        print("[+] Type 'exit' to return to main menu")
        print("-"*70)
        
        try:
            while True:
                command = input(f"{client_name}> ")
                
                if command.lower() == 'exit':
                    print("[+] Exiting interactive session")
                    break
                
                if not command.strip():
                    continue
                
                try:
                    # Send command to client
                    client_socket.send((command + "\n").encode())
                    
                    # Receive response
                    client_socket.settimeout(10)
                    response = b""
                    
                    while True:
                        try:
                            chunk = client_socket.recv(4096)
                            if not chunk:
                                break
                            response += chunk
                            
                            # Check if we received the end marker
                            if b"[CMD_END]" in response:
                                response = response.replace(b"[CMD_END]", b"")
                                break
                        except socket.timeout:
                            break
                    
                    # Display response
                    if response:
                        print(response.decode('utf-8', errors='ignore'), end='')
                    
                except socket.timeout:
                    print("[!] Command timeout")
                except Exception as e:
                    print(f"[!] Error: {e}")
                    break
                    
        except KeyboardInterrupt:
            print("\n[+] Exiting interactive session")
    
    def command_handler(self):
        """Handle user commands for the server"""
        print("\n[+] Command handler started")
        print("[+] Type 'help' for available commands\n")
        
        while True:
            try:
                cmd = input("Server> ").strip().lower()
                
                if cmd == 'help':
                    self.show_help()
                elif cmd == 'list' or cmd == 'ls':
                    self.list_clients()
                elif cmd.startswith('interact ') or cmd.startswith('session ') or cmd.startswith('use '):
                    try:
                        client_id = int(cmd.split()[1])
                        self.interact_with_client(client_id)
                    except (ValueError, IndexError):
                        print("[!] Usage: interact <client_id>")
                elif cmd == 'exit' or cmd == 'quit':
                    print("[!] Shutting down server...")
                    sys.exit(0)
                elif cmd == '':
                    continue
                else:
                    print(f"[!] Unknown command: {cmd}")
                    print("[+] Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\n[!] Use 'exit' to quit")
            except Exception as e:
                print(f"[!] Error: {e}")
    
    def show_help(self):
        """Display help information"""
        print("\n" + "="*70)
        print("Available Commands:")
        print("="*70)
        print("  list, ls              - List all connected clients")
        print("  interact <id>         - Start interactive shell with client")
        print("  session <id>          - Alias for interact")
        print("  use <id>              - Alias for interact")
        print("  help                  - Show this help message")
        print("  exit, quit            - Shutdown the server")
        print("="*70)

if __name__ == "__main__":
    # You can change the port here if needed
    server = RemoteAdminServer(host='0.0.0.0', port=9001)
    server.start()
