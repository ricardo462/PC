import socket
import threading
import json

class Server:
    def __init__(self, artefactos_path = "artefactos.json", HOST = '127.0.0.1', PORT = 8889):
    # Se cargan los datos de los artefactos.
        with open(artefactos_path, "r") as j:
           self.artefactos = json.load(j)
        
        # Se crea el socket y se instancia en las variables anteriores.
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((HOST, PORT))
        self.s.listen()
        
        # Lista con los sockets de los clientes
        self.sock_clientes = []
        # Diccionario con los códigos de los artefactos de los clientes {"cliente":[artefactos]}
        self.arte_clientes = {}
        # Diccionario con los nombres de los ususarios {socket:"cliente"}
        self.clientes_dict = {}
        # Mutex para realizar cambios a las variables anteriores
        self.mutex = threading.Lock()

        # Se buscan clientes que quieran conectarse.
        while True:
            # Se acepta la conexión de un cliente
            conn, _ = self.s.accept()
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
            client.send("[SERVER]: Cuéntame, ¿qué artefactos tienes?".encode())    
            while True:     
                try:
                    artefactos = client.recv(1024).decode()
                except:
                    break
                # Cuando se obtiene una respuesta, se separan en una lista por comas
                artefactos_list = artefactos.split(',')
                if len(artefactos_list) < 7:
                    # Se registran los artefactos válidos
                    traduccion = [self.artefactos.get(key) if key in self.artefactos.keys() else '' for key in artefactos_list]
                    # Se consulta si es que los artefactos son los correctos
                    client.send(f"[SERVER] Tus artefactos son: {', '.join(traduccion)}. ¿Está bien? (Sí/No)".encode())
                    # Se espera una respuesta
                    while True:
                        try: 
                            respuesta = client.recv(1024).decode()
                        except:
                            break
            
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
            users = [] #Se crea un arreglo vacío en caso de envío del comando :u
            # Variable que controla el envío de mensajes a todos los clientes o a algunos clientes en específico
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
                    del self.clientes_dict[sock]
                    del self.arte_clientes[sock]
                    
                sock.close()
                # Se envía el mensaje de desconexión a todos los clientes
                for conn in self.sock_clientes:
                    if conn != sock:
                        conn.send(f"[SERVER] Cliente {self.clientes_dict[sock]} desconectado".encode())
                break

            elif data == ":artefactos":
                SEND = False #Mensaje solo se envía a usuario que mande el comando
                # Se crea una lista con los nombres (no números) de los artefactos.
                arte_list = [self.artefactos.get(artefacto) if self.artefactos.get(artefacto) is not None else '' for artefacto in self.arte_clientes[sock]]
                sock.send(f"[SERVER] Tus artefactos son {', '.join(arte_list)}\n".encode())
                

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
                # Se identifica el artefacto a consultar
                arteID = data[11:]
                SEND = False
                # Se envía el mensaje con el artefaco solicitado en el caso de existir
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
                
                #Identificamos a qué usuario queremos mandarle el susurro
                for user in new_users:
                    largo = len(user)
                    if data[3:3+largo] == user:
                        Id = data[3:3+largo]
                
                
                #Valor de conexión del cliente (socket) al cual le enviaremos el mensaje
                for client in self.clientes_dict:
                    if Id == self.clientes_dict[client]:
                        whisper_to = client
                
                #Se envía el mensaje al destinatario del susurro
                mensaje = data[len(Id)+3:]
                sock.send(f"*susurro* Yo: {mensaje}".encode())
                whisper_to.send(f"*susurro* CLIENTE {nombre}: {mensaje}".encode())

            elif data[:6] == ":offer":
                SEND = False
                #Agregamos usuarios conectados a una lista
                new_users = []
                for client in self.sock_clientes:
                    name = self.clientes_dict[client]
                    new_users.append(name)
                
                #Identificamos con quién queremos hacer el intercambio
                for user in new_users:
                    largo = len(user)
                    if data[7:7+largo] == user:
                        Id = data[7:7+largo]

                #Obtenemos valor de la conexión (socket) del destinatario
                for client in self.clientes_dict:
                    if Id == self.clientes_dict[client]:
                        exc_with = client

                largo = len(Id)

                artId = data[8+largo:10+largo]

                #Obtenemos número del artefacto ofrecido
                if artId[1] == ' ':
                    miArtId = artId[0]
                    suArtId = data[10+largo:]
                        
                #Obtenemos número del artefacto deseado (destinatario)
                if artId[1] != ' ':
                    miArtId = artId
                    suArtId = data[11+largo:]

                if len(suArtId)>2:
                    sock.send(f"Existe algún error en la numeración de los artefactos. Recuerda que son desde el 1 al 42. Realiza el intercambio nuevamente".encode())
                    continue

                #Lanzamos thread para realizar el intercambio
                intercambio_thread = threading.Thread(target=self.intercambio, args=(sock, exc_with, miArtId, suArtId))
                intercambio_thread.start()

            # Se espera una confirmación
            if data == ":accept" or data == ":reject":
                SEND = False
                sock.send("Para confirmar, envía tu respuesta nuevamente".encode())

            # Se manda el mensaje a todos los clientes si SEND es True.
            if SEND:
                for s in self.sock_clientes:
                    if s != sock:
                        if len(users)>0: #Si se envía comando :u, solo se envía la lista de usuarios, no quién envió el comando.
                            s.send(f"[SERVER] Los usuarios conectados son {', '.join(users)}".encode())
                        else: 
                            s.send(f"{nombre}: {data}".encode())
                    else:
                        if len(users)>0:
                            s.send(f"[SERVER] Los usuarios conectados son {', '.join(users)}".encode())
                        else: 
                            s.send(f"Yo: {data}".encode())

    
    def intercambio(self, client1, client2, artId1, artId2):
        while True:
            """
            client1: socket usuario que inicia intercambio
            client2: socket usuario que recibe el intercambio
            artId1: número de artefacto ofrecido
            artId2: número de artefacto deseado
            """

            #Verificamos existencia de artefactos
            if int(artId1)<1 or int(artId1) > 42:
                if int(artId2)<1 or int(artId2) > 42:
                    client1.send(f"Ninguno de los artefactos existe:(. Se cancela el intercambio".encode())
                    break
                else: 
                    client1.send(f"El artefacto con numeración {artId1} no existe:(. Se cancela el intercambio".encode())
                    break

            if int(artId2)<1 or int(artId2) > 42:
                if int(artId1)<1 or int(artId1) > 42:
                    client1.send(f"Ninguno de los artefactos existe:(. Se cancela el intercambio".encode())
                    break
                else: 
                    client1.send(f"El artefacto con numeración {artId2} no existe:(. Se cancela el intercambio".encode())
                    break
            
            #Nombre de cada artefacto
            artName1 = self.artefactos[artId1]
            artName2 = self.artefactos[artId2]

            #Nombre de cada usuario
            name1 = self.clientes_dict[client1]
            name2 = self.clientes_dict[client2]

            #se envía mensaje a cada cliente involucrado
            client1.send(f"Yo: Quiero intercambiar mi {artName1} por el {artName2} de {name2}".encode())
            client2.send(f"[SERVER] CLIENTE {name1} quiere intercambiar su {artName1} por tu {artName2}\n".encode())
            client2.send(f"Deseas proceder con el intercambio?[:accept/:reject]".encode())

            #Esperamos respuesta
            try:
                data = client2.recv(1024).decode()
            except:
                break

            #procedemos con el intercambio
            if data==":accept":
                #Si alguno de los clientes no posee el artefacto en cuestión, se cancela el intercambio
                if artId1 not in self.arte_clientes[client1]:
                    client1.send(f"[SERVER] No posees {artName1}. Se cancela el intercambio.".encode())
                    client2.send(f"[SERVER] {name1} no posee {artName1}. Se cancela el intercambio.".encode())
                    break

                elif artId2 not in self.arte_clientes[client2]:
                    client2.send(f"[SERVER] No posees {artName2}. Se cancela el intercambio.".encode())
                    client1.send(f"[SERVER] {name2} no posee {artName2}. Se cancela el intercambio.".encode())
                    break

                #Si ambos poseen cada artefacto, se procede con el intercambio
                else:
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
                client1.send(f"[SERVER] {name2} rechazó el intercambio.".encode())
                client2.send(f"[SERVER] Cancelaste el intercambio.".encode())

                break

            elif data!=":accept" or data!=":reject":
                client2.send(f"[SERVER] Perdón, solo entiendo :accept o :reject :(".encode())
