# raspberry_pi_server.py
import socket

server_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
server_sock.bind(("", 1))
server_sock.listen(1)

print("Waiting for connection on RFCOMM channel 1...")

client_sock, client_info = server_sock.accept()
print(f"Accepted connection from {client_info}")

try:
    while True:
        data = client_sock.recv(1024)
        if not data:
            break
        command = data.decode().strip()
        print(f"Received command: {command}")
        # You can act on the command here
        if command == "ping":
            client_sock.send(b"pong\n")
        else:
            client_sock.send(b"Unknown command\n")
except OSError:
    pass

print("Disconnected.")
client_sock.close()
server_sock.close()
