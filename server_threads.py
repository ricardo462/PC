import socket
import threading
import json

sock_clientes = []
arte_dict = {}
mutex = threading.Lock()

# Se cargan los datos de los artefactos.
with open("artefactos.json", "r") as j:
    artefactos = json.load(j)

def cliente(sock):
    global sock_clientes, arte_dict, artefactos

    nombre = "Sebastian"
    arte_dict[nombre] = ["12", "15"]

    while True:
        try:
            data = sock.recv(1024).decode()
        except:
            break

        print(data)

        if data == ":q":
            sock.send("¡Adiós y suerte completando tu colección!".encode())
            
            # Se modifican las variables globales usando un mutex.
            with mutex:
                sock_clientes.remove(sock)
                arte_dict.pop(nombre)
            sock.close()
            break

        elif data == ":artefactos":
            # Se crea una lista con los nombres (no números) de los artefactos.
            arte_list = [artefactos[k] for k in arte_dict[nombre]]
            sock.send(f"[SERVER] Tus artefactos son {', '.join(arte_list)}".encode())

        elif data == ":larva":
            data = "(:o)OOOooo"

        # Se manda el mensaje a todos los clientes.
        for s in sock_clientes:
            if s != sock:
                s.send(f"CLIENTE {nombre}: {data}".encode())
            else:
                s.send(f"Yo: {data}".encode())

# Se configura el servidor para que corra localmente y en el puerto 8889.
HOST = '127.0.0.1'
PORT = 8889

# Se crea el socket y se instancia en las variables anteriores.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

# Se buscan clientes que quieran conectarse.
while True:

    # Se acepta la conexión de un cliente
    conn, addr = s.accept()
    print("Cliente conectado")
    sock_clientes.append(conn)

    # Se manda el mensaje de bienvenida
    conn.send("¡Bienvenid@ al chat de Granjerxs!".encode())

    # Se inicia el thread del cliente
    client_thread = threading.Thread(target=cliente, args=(conn,))
    client_thread.start()