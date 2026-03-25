import socket, threading, os

HOST, PORT, FILES_DIR = '0.0.0.0', 5000, 'server_files'
clients = []
os.makedirs(FILES_DIR, exist_ok=True)

def broadcast(msg, sender=None):
    for c in clients:
        if c != sender:
            try: c.sendall(msg)
            except: pass

def handle_upload(conn, text):
    lines = text.splitlines()
    parts = lines[0].split()
    if len(parts) < 2: return conn.send(b"ERROR Usage: /upload <filename>\n")
    
    header = lines[1] if len(lines) > 1 else conn.recv(1024).decode().strip()
    _, fname, size = header.split()
    if header.split()[0] != "FILE": return conn.send(b"ERROR Invalid header\n")
    
    path = os.path.join(FILES_DIR, fname)
    with open(path, 'wb') as f:
        remaining = int(size)
        while remaining > 0:
            chunk = conn.recv(min(1024, remaining))
            if not chunk: break
            f.write(chunk)
            remaining -= len(chunk)
    conn.send(b"Upload complete\n")
    print(f"Uploaded: {fname} ({size} bytes)")

def handle_download(conn, text):
    parts = text.strip().split()
    if len(parts) < 2: return conn.send(b"ERROR Usage: /download <filename>\n")
    
    path = os.path.join(FILES_DIR, parts[1])
    if not os.path.exists(path): return conn.send(b"ERROR File not found\n")
    
    size = os.path.getsize(path)
    conn.sendall(f"FILE {parts[1]} {size}\n".encode())
    with open(path, 'rb') as f: conn.sendall(f.read())

def handle_client(conn, addr):
    clients.append(conn)
    print(f"Connected: {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data: break
            text = data.decode()
            
            if text.startswith('/list'):
                files = os.listdir(FILES_DIR)
                conn.send((('\n'.join(files) if files else "(no files)") + '\n').encode())
            elif text.startswith('/upload'): handle_upload(conn, text)
            elif text.startswith('/download'): handle_download(conn, text)
            else: print(f"{addr}: {text.strip()}"); broadcast(data, conn)
    finally:
        print(f"Disconnected: {addr}")
        clients.remove(conn)
        conn.close()

with socket.socket() as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server running on port {PORT}")
    while True:
        threading.Thread(target=handle_client, args=(*s.accept(),), daemon=True).start()