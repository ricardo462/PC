import socket
import sys
import threading

def leer(sock):
    while True:
        try:
            res = sock.recv(1024).decode()
        except:
            sock.close()
            break
        print(res)

# Se asume que el servidor está corriendo localmente en el puerto 8889.
HOST = '127.0.0.1'
PORT = 8889

# Se crea el socket y se conecta al servidor.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("Conectado al servidor")

reading_thread = threading.Thread(target=leer, args=(s,))
reading_thread.start()

# Se revisa la entrada estándar y se envía lo que ingrese le usuarie.
for line in sys.stdin:
    msg = line.rstrip()
    s.send(msg.encode())

    if msg == ":q":
        res = s.recv(1024).decode()
        break
    
s.close()