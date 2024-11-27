import socket
import threading
import tkinter as tk
import os

# Připojení k serveru
SERVER_IP = "172.20.21.185"  # Změňte na IP serveru
SERVER_PORT = 12345
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))


# Cesta k souboru
file_path = "C:/data/klient.txt"

# Kontrola, zda soubor existuje
if os.path.exists(file_path):
    # Soubor existuje, přečteme jméno
    with open(file_path, "r") as file:
        nick = file.read().strip()
else:
    # Soubor neexistuje, vytvoříme ho
    nick = input("Zadej jméno: ")
    with open(file_path, "w") as file:
        file.write(nick)

print(f"Váš nick byl nastaven na: {nick}")
print("Kdyby jste chtěli změnit nick, použijte '/nick [jméno]'")




# Inicializace GUI
root = tk.Tk()
root.geometry("400x400")
root.title("klient")

messages_frame = tk.Frame(root)
messages_frame.pack()

scrollbar = tk.Scrollbar(messages_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(messages_frame, height=20, width=50, yscrollcommand=scrollbar.set)
listbox.pack(side=tk.LEFT, fill=tk.BOTH)
scrollbar.config(command=listbox.yview)

entry_field = tk.Entry(root)
entry_field.pack(fill=tk.BOTH, padx=10, pady=10)

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            listbox.insert(tk.END, message)
        except:
            listbox.insert(tk.END, "Došlo k odpojení od serveru.")
            client.close()
            break

def send_message(event=None):
    global nick
    message = entry_field.get()
    entry_field.delete(0, tk.END)
    
    if message == "/stop":
        client.close()
        root.quit()  # Ukončení Tkinter aplikace
    elif message == "/help":
        listbox.insert(tk.END, "/stop pro ukončení aplikace.")
        listbox.insert(tk.END, "/help pro tuto zprávu.")
        listbox.insert(tk.END, "/list pro seznam všech klientů.")
        listbox.insert(tk.END, "/clear pro vymazání všech zpráv (nevymaže na straně serveru).")
        listbox.insert(tk.END, "/nick [jméno] zadej pro změnu jména.")
    elif message == "/list":
        client.send("/list".encode('utf-8'))
    elif message == "/clear":
        listbox.delete(0, tk.END)
    elif message.startswith("/nick"):
        parts = message.split(' ', 1)
        if len(parts) == 2:
            nick = parts[1]
            with open(file_path, "w") as file:
                file.write(nick)
            listbox.insert(tk.END, f"Nick úspěšně změněn na {nick}.")
    else:
        if nick != "":
            message_to_send = "[" + nick + "] " + message
        else:
            message_to_send = message

        client.send(message_to_send.encode('utf-8'))
        listbox.insert(tk.END, message_to_send)  # Zobrazit odeslanou zprávu

# Připojení vstupu k odesílání zpráv
entry_field.bind("<Return>", send_message)

# Spuštění vlákna pro přijímání zpráv
threading.Thread(target=receive_messages, daemon=True).start()

# Spuštění Tkinter aplikace
root.mainloop()
