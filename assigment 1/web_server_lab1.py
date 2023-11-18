from socket import *
import sys  

# Configuración del servidor
serverPort = 8086 
ip = '127.0.0.1'
serverSocket = socket(AF_INET, SOCK_STREAM)

# Asocia el socket con una dirección IP y un puerto
serverSocket.bind((ip, serverPort))
serverSocket.listen(1)

print('El servidor está listo para recibir solicitudes...')

while True:
    # Acepta la conexión entrante
    connectionSocket, addr = serverSocket.accept()

    try:
        # Recibe la solicitud HTTP del cliente
        message = connectionSocket.recv(1024).decode()

        # Obtiene el nombre del archivo solicitado desde la solicitud
        filename = message.split()[1][1:] 

        # Abre el archivo solicitado y lee su contenido
        with open(filename, 'rb') as file:
            outputdata = file.read()

        # Prepara la respuesta HTTP
        response = "HTTP/1.1 200 OK\r\n\r\n".encode() + outputdata

        # Envía la respuesta al cliente
        connectionSocket.send(response)

        # Cierra la conexión
        connectionSocket.close()

    except IOError:
        # Si el archivo no se encuentra, envía un mensaje de "404 Not Found"
        not_found_response = "HTTP/1.1 404 Not Found\r\n\r\nFile Not Found"
        connectionSocket.send(not_found_response.encode())

        # Cierra la conexión
        connectionSocket.close()

serverSocket.close()
sys.exit()#Terminate the program after sending the corresponding data