from socket import *
import sys

if len(sys.argv) <= 1:
    print('Uso: "python ProxyServer.py ip_servidor"\n[ip_servidor: es la dirección IP del servidor proxy]')
    sys.exit(2)

# Crea un socket del servidor, vincúlalo a un puerto y comienza a escuchar
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(('', 8888))  # Asigna el puerto 8888, puedes cambiarlo si lo necesitas
tcpSerSock.listen(5)

while True:
    # Comienza a recibir datos del cliente
    print('Listo para servir...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Se ha recibido una conexión de:', addr)
    message = tcpCliSock.recv(1024).decode('utf-8', errors='ignore')  # Recibe el mensaje del cliente
    print(message)

    print(message.split()[0])  # Verifica el tipo de solicitud (GET, POST, etc.)
    print(message.split()[1])  # Verifica la dirección URL
    request_type = message.split()[0]
    filename = message.split()[1].partition("/")[2]
    
    if request_type != "GET" or not filename.startswith("http://"):
        print("Solicitud no válida para el servidor proxy.")
        tcpCliSock.close()
        continue 

    # Extrae el nombre de archivo del mensaje dado
    print(message.split()[1])
    filename = message.split()[1].partition("/")[2]
    print(filename)
    fileExist = "false"
    filetouse = "/" + filename
    print(filetouse)

    try:
        # Comprueba si el archivo existe en la caché
        f = open(filetouse[1:], "r")
        outputdata = f.readlines()
        fileExist = "true"
        # El servidor proxy encuentra un acierto en la caché y genera un mensaje de respuesta
        tcpCliSock.send("HTTP/1.0 200 OK\r\n")
        tcpCliSock.send("Content-Type:text/html\r\n")
        tcpCliSock.send("\r\n")
        # Envía el contenido del archivo desde la caché al cliente
        for i in range(len(outputdata)):
            tcpCliSock.send(outputdata[i].encode())
        print('Leído desde la caché')

    # Manejo de errores para archivo no encontrado en la caché
    except IOError:
        if fileExist == "false":
            # Crea un socket en el servidor proxy
            c = socket(AF_INET, SOCK_STREAM)
            hostn = filename.replace("www.", "", 1)
            print(hostn)

            try:
                # Conéctate al socket al puerto 80
                c.connect((hostn, 80))
                # Crea un archivo temporal en este socket y solicita el puerto 80
                # para el archivo solicitado por el cliente
                fileobj = c.makefile('r', 0)
                fileobj.write("GET " + "http://" + filename + " HTTP/1.0\n\n")
                # Lee la respuesta en el búfer
                buffer = fileobj.readlines()
                # Crea un nuevo archivo en la caché para el archivo solicitado
                tmpFile = open("./" + filename, "wb")
                # Envía la respuesta desde el servidor web al cliente y la guarda en la caché
                for i in range(len(buffer)):
                    tcpCliSock.send(buffer[i].encode())
                    tmpFile.write(buffer[i].encode())
                tmpFile.close()
            except FileNotFoundError as e:
                print("Archivo no encontrado:", e)
            except OSError as e:
                print("Error de conexión:", e)
            except socket.error as e:
                print("Error de resolución de dirección:", e)
            except Exception as e:
                print("Otro tipo de error:", e)
        else:
            # Mensaje de respuesta HTTP para archivo no encontrado
            tcpCliSock.send("HTTP/1.0 404 Not Found\r\n")
            tcpCliSock.send("Content-Type:text/html\r\n")
            tcpCliSock.send("\r\n")
    
    # Cierra los sockets del cliente y del servidor
    tcpCliSock.close()

# Cierra el socket del servidor
tcpSerSock.close()
