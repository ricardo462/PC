import socket
import threading
import json

class Server:
    def __init__(self, artefactos_path = "artefactos.json", HOST = '127.0.0.1', PORT = 8889):
    # Rama hola

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
            print("Cliente conectado")
            self.sock_clientes.append(conn)

            # Se manda el mensaje de bienvenida
            conn.send("[SERVER]: ¡Bienvenid@ al chat de Granjerxs!".encode())
            name_thread = threading.Thread(target=self.welcomy_function, args=(conn,))
            name_thread.start()


            

    def welcomy_function(self, client):
        client.send("[SERVER]: ¿Cuál es tu nombre?".encode())
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
                    break

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
                            if respuesta == 'Sí' or respuesta == 'sí' or respuesta == 'si':
                                preguntar = False
                            break
                    break

        # Se agrega al cliente al registro
        with self.mutex:
            self.clientes_dict[client] = data
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
            users = []
            #Agregué este SEND para hacerlo False en el momento que no quiera mandar un mensaje para todos
            SEND = True
            try:
                data = sock.recv(1024).decode()
            except:
                break

            print(data)

            if data == ":q":
                sock.send("[SERVER]¡Adiós y suerte completando tu colección!".encode())
                
                # Se modifican las variables usando un mutex.
                with self.mutex:
                    self.sock_clientes.remove(sock)
            
                sock.close()
                for conn in self.sock_clientes:
                    if conn != sock:
                        conn.send(f"[SERVER] Cliente {self.clientes_dict[sock]} desconectado".encode())
                break

            elif data == ":artefactos":
                # Se crea una lista con los nombres (no números) de los artefactos.
                arte_list = [self.artefactos.get(artefacto) if self.artefactos.get(artefacto) is not None else '' for artefacto in self.arte_clientes[sock]]
                sock.send(f"[SERVER] Tus artefactos son {', '.join(arte_list)}\n".encode())
                SEND = False

            elif data == ":larva":
                data = "(:o)OOOooo"

            elif data == ":u":
                #Creamos lista con nombres de los usuarios conectados
                for client in self.sock_clientes:
                    name = self.clientes_dict[client]
                    users.append(name)

            elif data == ":smile":
                data = ":)"

            elif data == ":angry":
                data = ">:("
            
            elif data == ":combito":
                data = "Q('-'Q)"
            
            elif data[:10] == ":artefacto" and data != ":artefactos":
                arteID = data[11:]
                SEND = False
                if int(arteID) < 1 or int(arteID)>42:
                    sock.send(f"[SERVER] Ese artefacto no existe:(\n".encode())
                else: 
                    artefacto = self.artefactos[arteID]
                    sock.send(f"[SERVER] El artefacto {arteID} corresponde a {artefacto}\n".encode())

            elif data[:2] == ":p":
                SEND = False
                #Agregamos usuarios conectados a una lista
                new_users = []
                for client in self.sock_clientes:
                    name = self.clientes_dict[client]
                    new_users.append(name)
                
                #Vemos a qué usuario queremos mandarle el susurro
                for user in new_users:
                    largo = len(user)
                    if data[3:3+largo] == user:
                        Id = data[3:3+largo]
                
                
                #Valor de conexión del cliente al cual le enviaremos el mensaje
                for client in self.clientes_dict:
                    if Id == self.clientes_dict[client]:
                        whisper_to = client
                
                #whisper_to: socket, sock: socket (qn envia)
                mensaje = data[len(Id)+3:]
                sock.send(f"*susurro* Yo: {mensaje}".encode())
                whisper_to.send(f"*susurro* CLIENTE {nombre}: {mensaje}".encode())

            elif data[:6] == ":offer":
                SEND = False
                new_users = []
                for client in self.sock_clientes:
                    name = self.clientes_dict[client]
                    new_users.append(name)
                
                #Vemos a con quien queremos hacer el intercambio
                for user in new_users:
                    largo = len(user)
                    if data[3:3+largo] == user:
                        Id = data[3:3+largo]


                for client in self.clientes_dict:
                    if Id == self.clientes_dict[client]:
                        exc_with = client

                largo = len(Id)

                artId = data[6+largo:6+largo+2]

                if int(artId) < 10:
                    suArtId = data[6+largo+1:]

                if int(artId) >= 10:
                    suArtId = data[6+largo+2:]

                intercambio_thread = threading.Thread(target=self.intercambio, args=(sock, exc_with, artId, suArtId))
                intercambio_thread.start()


            # Se manda el mensaje a todos los clientes si SEND es True.
            if SEND:
                for s in self.sock_clientes:
                    if s != sock:
                        if len(users)>0:
                            s.send(f"[SERVER] Los usuarios conectados son {', '.join(users)}".encode())
                        else: 
                            s.send(f"CLIENTE {nombre}: {data}".encode())
                    else:
                        if len(users)>0:
                            s.send(f"[SERVER] Los usuarios conectados son {', '.join(users)}".encode())
                        else: 
                            s.send(f"Yo: {data}".encode())

    
    def intercambio(self, client1, client2, artId1, artId2):
        while True:
            artName1 = self.artefactos[artId1]
            artName2 = self.artefactos[artId2]

            name1 = self.clientes_dict[client1]
            name2 = self.clientes_dict[client2]

            client1.send(f"Yo: Quiero intercambiar un {artName1} por un {artName2} con {name2}".encode())
            client2.send(f"[SERVER] CLIENTE {name1} quiere intercambiar un {artName1} por un {artName2}\n".encode())
            client2.send(f"Deseas proceder con el intercambio?[:accept/:reject]".encode())

            try:
                data = client2.recv(1024).decode()
            except:
                break

            if data==":accept":
                #procedemos con el intercambio
                if artId1 not in self.arte_clientes[client1]:
                    client1.send(f"[SERVER] No posees {artName1}. Se cancela el intercambio.".encode())
                    client2.send(f"[SERVER] {name1} no posee {artName1}. Se cancela el intercambio.".encode())
                    break

                elif artId2 not in self.arte_clientes[client2]:
                    client2.send(f"[SERVER] No posees {artName2}. Se cancela el intercambio.".encode())
                    client1.send(f"[SERVER] {name2} no posee {artName2}. Se cancela el intercambio.".encode())
                    break

                elif artId1 in self.arte_clientes[client1] and artId2 in self.arte_clientes:
                    art_cliente1 = self.arte_clientes[client1]
                    art_cliente2 = self.arte_clientes[client2]

                    art_cliente1.remove(artId1)
                    art_cliente2.remove(artId2)

                    art_cliente1.append(artId2)
                    art_cliente2.append(artId1)

                    client1.send(f"[SERVER] Intercambio exitoso.".encode())
                    client2.send(f"[SERVER] Intercambio exitoso.".encode())

                    break


            elif data==":reject":
                client1.send(f"[SERVER] {name2} rechazó el intercambio.")
                client2.send(f"[SERVER] Cancelaste el intercambio.")

            elif data!=":accept" or data!=":reject":
                client2.send(f"[SERVER] Perdón, solo entiendo :accept o :reject :(".encode())