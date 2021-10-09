import socket
import threading
import sys


class Client:
    def __init__(self, name = 'default'):
        self.name = name

        # Se asume que el servidor está corriendo localmente en el puerto 8889.
        HOST = '127.0.0.1'
        PORT = 8889


        # Se crea el socket y se conecta al servidor.
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        print("Conectado al servidor")

        reading_thread = threading.Thread(target=self.leer, args=(self.s,))
        reading_thread.start()

        # Se revisa la entrada estándar y se envía lo que ingrese le usuarie.
        for line in sys.stdin:
            msg = line.rstrip()
            self.s.send(msg.encode())
            if msg == ":q":
                res = self.s.recv(1024).decode()
                break
            


    def leer(self, sock):
        while True:
            try:
                res = sock.recv(1024).decode()
            except:
                sock.close()
                break
            print(res)


    def close(self):
        self.s.close()