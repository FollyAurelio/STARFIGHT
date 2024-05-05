import socket
import threading

def client_thread(conn, addr):
    # Gérer la communication avec le client ici
    conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 12345))
server.listen()

while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=client_thread, args=(conn, addr))
    thread.start()