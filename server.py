import socket
import threading

list_dat = []
SERVER_IP = "0.0.0.0"  # Změňte na vaši IP adresu
SERVER_PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_IP, SERVER_PORT))
server.listen()

clients = []

def broadcast(message, sender_socket=None):
    """ Posílá zprávu všem klientům """
    for client in clients:
        if client != sender_socket:  # Neposílat zprávu zpět odesílateli
            try:
                client.send(message)
            except:
                client.close()
                clients.remove(client)

def handle_client(client_socket):
    """ Funkce pro zpracování zpráv od klienta """
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            elif message.decode('utf-8') == "/list":
                client_socket.send(clients).encode('utf-8')
            else:
                t = list(message.decode('utf-8'))
                if t[0] == "[":
                    print(f"{message.decode('utf-8')}")
                    list_dat.append(f"{message.decode('utf-8')}")
                    broadcast(message, client_socket)
                else:
                    print(f"[Zpráva od klienta] {message.decode('utf-8')}")
                    list_dat.append(f"[Zpráva od klienta] {message.decode('utf-8')}")
                    broadcast(message, client_socket)
        except:
            clients.remove(client_socket)
            client_socket.close()
            break

def start_server():
    print("[SERVER] Server běží a čeká na připojení...")
    list_dat.append("[SERVER] Server běží a čeká na připojení...")
    while True:
        client_socket, client_address = server.accept()
        print(f"[PŘIPOJENÍ] {client_address} se připojil.")
        list_dat.append(f"[PŘIPOJENÍ] {client_address} se připojil.")
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

def send_from_server():
    """ Funkce pro posílání zpráv přímo ze serveru """
    while True:
        message = input("[SERVER ZPRÁVA]: ")
        list_dat.append(f"[SERVER] {message}")
        if message == "/stop":
            print("Server se vypiná...")
            list_dat.append("Server se vypiná...")
            for client in clients:
                client.close()
            server.close()
            with open("data.txt", "w") as file:
                file.write("\n".join(list_dat))
            exit()
        broadcast(f"[SERVER] {message}".encode('utf-8'))

try:
    threading.Thread(target=start_server).start()
    send_from_server()
except KeyboardInterrupt:
    print("Server se vypíná...")
    list_dat.append("Server se vypíná...")
    with open("data.txt", "w") as file:
        file.write("\n".join(list_dat))
finally:
    for client in clients:
        client.close()
    server.close()