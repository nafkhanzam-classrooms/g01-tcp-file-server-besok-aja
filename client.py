import socket, threading, os

HOST, PORT = "bore.pub", int(input("Port: "))
s, connected = None, False

def connect():
    global s, connected
    while True:
        s = socket.socket()
        s.connect((HOST, PORT))
        connected = True
        print("Connected.")
        return

def receive():
    global connected
    while True:
        try:
            data = s.recv(1024)
            if not data: raise ConnectionError
            
            if data.startswith(b"FILE"):
                _, filename, size = data.decode().split()
                with open(filename, 'wb') as f:
                    remaining = int(size)
                    while remaining > 0:
                        chunk = s.recv(min(1024, remaining))
                        f.write(chunk)
                        remaining -= len(chunk)
                print(f"\nDownloaded: {filename}")
            else: print("\nServer:", data.decode(), end='')
        except:
            print("\nDisconnected. Reconnecting...")
            connected = False
            connect()
            threading.Thread(target=receive, daemon=True).start()
            break

connect()
threading.Thread(target=receive, daemon=True).start()

while True:
    try:
        msg = input("Message: ")
        if not msg: continue
        
        if msg.startswith('/upload'):
            parts = msg.split()
            if len(parts) != 2: print("Usage: /upload <filename>"); continue
            if not os.path.exists(parts[1]): print("File not found"); continue
            
            size = os.path.getsize(parts[1])
            s.sendall(f"/upload {parts[1]}\nFILE {parts[1]} {size}\n".encode())
            with open(parts[1], 'rb') as f: s.sendall(f.read())
        else:
            s.sendall((msg + '\n').encode())
    except KeyboardInterrupt: break
    except: connected = False; connect(); threading.Thread(target=receive, daemon=True).start()