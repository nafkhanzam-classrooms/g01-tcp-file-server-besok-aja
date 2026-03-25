import socket, select, os

HOST, PORT, FILES_DIR = '0.0.0.0', 5000, 'server_files'
os.makedirs(FILES_DIR, exist_ok=True)

server = socket.socket()
server.bind((HOST, PORT))
server.listen()

poller = select.poll()
poller.register(server, select.POLLIN)
fd_map = {server.fileno(): server}
print("POLL is running")

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
    if len(parts) < 2: return sock.send(b"[ERROR] /download <filename>\n")
    
    path = os.path.join(FILES_DIR, parts[1])
    if not os.path.exists(path): return sock.send(b"ERROR File not found\n")
    
    size = os.path.getsize(path)
    sock.sendall(f"FILE {parts[1]} {size}\n".encode())
    with open(path, 'rb') as f: sock.sendall(f.read())

while True:
    for fd, flag in poller.poll():
        sock = fd_map[fd]
        if sock == server:
            conn, addr = server.accept()
            poller.register(conn, select.POLLIN)
            fd_map[conn.fileno()] = conn
            print("Connected:", addr)
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
            else: [s.send(data) for s in fd_map.values() if s not in (server, sock)]
        except:
            poller.unregister(fd)
            del fd_map[fd]
            sock.close()