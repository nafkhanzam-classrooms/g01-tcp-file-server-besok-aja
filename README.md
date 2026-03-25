[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
| Fathiya Nayla Husna Wibowo                | 5025241204           |           |
|                |            |           |

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```

```

## Penjelasan Program
### Servers and Client

The program will be provided on different file, I will explain step by step how the program works:

#### A. [server-sync.py](https://github.com/nafkhanzam-classrooms/g01-tcp-file-server-besok-aja/blob/main/server-sync.py)
This server is fully synchronous, it handles one client at a time. It accepts a connection, processes everything for that client, then moves to the next one.
1. When a client connects, `handle_client()` runs in a loop. It keeps reading commands until the client disconnects.
2. The server supports `/list` to send list of files, `/upload` to receive and save file, `/download` to send file, and reply "unknown command" for other.
3. On upload handling, it reads header (`FILE name size`), then receives file in chunks and saves it.
4. On download handling, checks file then sends header then sends file using `sendall()`.

#### B. [server-select.py](https://github.com/nafkhanzam-classrooms/g01-tcp-file-server-besok-aja/blob/main/server-select.py)
This server uses `select()` to handle multiple clients in one loop.
1. All sockets are stored in a list, and `select()` tells which ones are ready.
2. If the server socket is ready, it means a new client is connecting. The server accepts it and adds it to the `sockets` list.
3. The server supports `/list` to send list of files, `/upload` to receive and save file, `/download` to send file, and broadcast message to other clients for other.
4. On upload handling, it reads header (`FILE name size`), then receives file in chunks and saves it.
5. On download handling, checks file then sends header then sends file using `sendall()`.

#### C. [server-poll.py](https://github.com/nafkhanzam-classrooms/g01-tcp-file-server-besok-aja/blob/main/server-poll.py)
1. The server uses `poll()` to watch all connections instead of `select()`. Each socket is tracked using its file descriptor (`fd_map`). When something happens, `poll()` tells the server which socket to handle.
2. If the server socket is triggered, it means a new client is connecting. The server accepts it, registers it to `poll()`, and stores it in `fd_map`.
3. The server supports `/list` to send list of files, `/upload` to receive and save file, `/download` to send file, and broadcast message to other clients for other.
4. On upload handling, it reads header (`FILE name size`), then receives file in chunks and saves it.
5. On download handling, checks file then sends header then sends file using `sendall()`.

#### D. [server-thread.py](https://github.com/nafkhanzam-classrooms/g01-tcp-file-server-besok-aja/blob/main/server-thread.py)
This server uses threading, so each client runs in its own thread. That means multiple clients can connect and be handled at the same time.
1. When a client connects, it gets added to a `clients` list. Each client is handled in `handle_client()` running in a separate thread.
2. The server supports `/list` to send list of files, `/upload` to receive and save file, `/download` to send file, and broadcast message to other clients for other.
4. On upload handling, it reads header (`FILE name size`), then receives file in chunks and saves it.
5. On download handling, checks file then sends header then sends file using `sendall()`.

#### E. [client.py](https://github.com/nafkhanzam-classrooms/g01-tcp-file-server-besok-aja/blob/main/client.py)
1. The client connects to the server using a host and port. If it gets disconnected, it will automatically try to reconnect.
2. A separate thread (`receive()`) keeps listening for incoming data. If it sees a `FILE` header, it downloads and saves the file. Otherwise, it treats it as a normal message from the server
3. The user can type messages `/upload <file>` to upload a file to the server but also other
* anything else → send as a regular chat message
4. The client first sends a header (`/upload + FILE name size`), then sends the file content in binary.
5. If the connection drops, the client will: 1. Print “Disconnected” 2. Reconnect to the server 3. Restart the receiving thread

### Run

I'm using W2 assignment to run the program, 4 different terminals will be provided.

1. Add WSL terminal then run the said server using `python [sinsert-server].py`.
2. Add another WSL terminal then run `bore local 5000 --to bore.pub` accordingly. It will gives you random port for laterr client.
3. Add another 2 terminal to run clients. The program will ask you to provide the port that bore has given from the bore before after running `client.py`

## Screenshot Hasil

### 1. server-sync.py

<img width="1648" height="472" alt="image" src="https://github.com/user-attachments/assets/fd4b9b85-298a-46ed-a6e5-6ca0d48f4171" />

### 2. server-thread.py

<img width="1408" height="515" alt="image" src="https://github.com/user-attachments/assets/a5d88a6c-d638-4d28-83fe-5207a537de09" />

### 3. server-select.py

<img width="1403" height="498" alt="image" src="https://github.com/user-attachments/assets/22b56683-f434-4fe7-a7b6-3e26bb365215" />

### 4. server-poll.py

<img width="1397" height="498" alt="image" src="https://github.com/user-attachments/assets/8eacf798-d1d1-4b2d-95df-a17d3064ef47" />
