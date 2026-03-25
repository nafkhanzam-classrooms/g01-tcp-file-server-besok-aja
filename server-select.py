import socket, select, os

HOST, PORT, FILES_DIR = '0.0.0.0', 5000, 'server_files'
os.makedirs(FILES_DIR, exist_ok=True)

server = socket.socket()
server.bind((HOST, PORT))
server.listen()
sockets = [server]
print("[SELECT] Server running")

def handle_upload(sock, text):
    lines = text.splitlines()
    parts = lines[0].split()
    if len(parts) < 2: return sock.send(b"ERROR Usage: /upload <filename>\n")
    
    header = lines[1] if len(lines) > 1 else sock.recv(1024).decode().strip()
    _, fname, size = header.split()
    if header.split()[0] != "FILE": return sock.send(b"ERROR Invalid header\n")
    
    path = os.path.join(FILES_DIR, fname)
    with open(path, 'wb') as f:
        remaining = int(size)
        while remaining > 0:
            chunk = sock.recv(min(1024, remaining))
            if not chunk: break
            f.write(chunk)
            remaining -= len(chunk)
    sock.send(b"Upload complete\n")
    print(f"[UPLOAD] {fname} ({size} bytes)")

def handle_download(sock, text):
    parts = text.strip().split()
    if len(parts) < 2: return sock.send(b"ERROR Usage: /download <filename>\n")
    
    path = os.path.join(FILES_DIR, parts[1])
    if not os.path.exists(path): return sock.send(b"ERROR File not found\n")
    
    size = os.path.getsize(path)
    sock.sendall(f"FILE {parts[1]} {size}\n".encode())
    with open(path, 'rb') as f: sock.sendall(f.read())

while True:
    readable, _, _ = select.select(sockets, [], [])
    for sock in readable:
        if sock == server:
            sockets.append(server.accept()[0])
            continue
        
        try:
            data = sock.recv(1024)
            if not data: raise Exception
            
            text = data.decode()
            if text.startswith('/list'):
                files = os.listdir(FILES_DIR)
                sock.send((('\n'.join(files) if files else "(no files)") + '\n').encode())
            elif text.startswith('/upload'): handle_upload(sock, text)
            elif text.startswith('/download'): handle_download(sock, text)
            else: [s.send(data) for s in sockets if s not in (server, sock)]
        except:
            sockets.remove(sock)
            sock.close()