import socket
import threading
import json

class Server:
    def __init__(self, artefactos_path = "artefactos.json", HOST = '127.0.0.1', PORT = 8889):
        
    # rama ricardo
    # Se cargan los datos de los artefactos.
        with open(artefactos_path, "r") as j:
           self.artefactos = json.load(j)
        
        # Se crea el socket y se instancia en las variables anteriores.
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((HOST, PORT))
        self.s.listen()

        self.sock_clientes = []
        self.arte_clientes = {}
        self.clientes_dict = {}
        self.mutex = threading.Lock()

        # Se buscan clientes que quieran conectarse.
        while True:
            # Se acepta la conexión de un cliente
            conn, addr = self.s.accept()
            self.sock_clientes.append(conn)

            # Se manda el mensaje de bienvenida
            conn.send("¡Bienvenid@ al chat de Granjerxs!".encode())
            name_thread = threading.Thread(target=self.welcomy_function, args=(conn,))
            name_thread.start()


            

    def welcomy_function(self, client):
        client.send("\n[SERVER]: ¿Cuál es tu nombre?".encode())
        # Se pregunta por el nombre
        while True:
            try:
                data = client.recv(1024).decode()
            except:
                break
            if data != '':
                if data in self.clientes_dict.values():
                    client.send("[SERVER]: Nombre no disponible :(. Ingresa un nuevo nombre".encode())
                else: 
                    with self.mutex:
                        self.clientes_dict[client] = data
                    break
        print(f'[SERVER] Cliente {data} conectado')
        # Se pregunta por los artefactos 
        preguntar = True
        while preguntar:
            client.send("[SERVER]:  Cuéntame, ¿qué artefactos tienes?".encode())    
            while True:     
                try:
                    artefactos = client.recv(1024).decode()
                except:
                    break
                # Cuando se obtiene una respuesta, se separan en unla lista por comas
                if artefactos != '':
                    artefactos_list = artefactos.split(',')
                    if len(artefactos_list) < 7:
                        # Se registran los artefactos válidos
                        traduccion = [self.artefactos.get(key) if key in self.artefactos.keys() else '' for key in artefactos_list]
                        # Se consulta si es que los artefacots son los correctos
                        client.send(f"[SERVER] Tus artefactos son: {', '.join(traduccion)}. ¿Está bien? (Sí/No)".encode())
                        # Se espera una respuesta
                        while True:
                            try: 
                                respuesta = client.recv(1024).decode()
                            except:
                                break
                            if respuesta != '':
                                respuesta = respuesta.lower()
                                if respuesta == 'sí' or respuesta == 'si':
                                    preguntar = False
                                break
                        break
                    else:
                        client.send('No puedes tener más de 6 artefactos. Ingresa nuevamente tus artefactos'.encode())

        # Se agregan los artefactos al registro
        with self.mutex:
            self.arte_clientes[client] = artefactos_list
        # Se inicia el thread del cliente
        client_thread = threading.Thread(target=self.cliente, args=(client,))
        client_thread.start()
        for conn in self.sock_clientes:
            if conn != client:
                conn.send(f"[SERVER]: Cliente {data} conectado".encode())



    def cliente(self, sock):
        nombre = self.clientes_dict[sock]
        while True:
            try:
                data = sock.recv(1024).decode()
            except:
                break

            print(data)

            if data == ":q":
                sock.send("¡Adiós y suerte completando tu colección!".encode())
                
                # Se modifican las variables usando un mutex.
                with self.mutex:
                    self.sock_clientes.remove(sock)
            
                sock.close()
                for conn in self.sock_clientes:
                    if conn != sock:
                        name = self.clientes_dict[sock]
                        conn.send(f"[SERVER] Cliente {name} desconectado".encode())
                        print(f'[SERVER] Cliente {name} desconectado')
                break

            elif data == ":artefactos":
                # Se crea una lista con los nombres (no números) de los artefactos.
                arte_list = [self.artefactos.get(artefacto) if self.artefactos.get(artefacto) is not None else '' for artefacto in self.arte_clientes[sock]]
                sock.send(f"[SERVER] Tus artefactos son {', '.join(arte_list)}".encode())

            elif data == ":larva":
                data = "(:o)OOOooo"

            # Se manda el mensaje a todos los clientes.
            for s in self.sock_clientes:
                if s != sock:
                    s.send(f"CLIENTE {nombre}: {data}".encode())
                else:
                    s.send(f"Yo: {data}".encode())

    