import random
from socket import *

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', 12001))  # Utiliza un puerto diferente al del servidor de ping

client_status = {}  # Almacena la última vez que se recibió un latido de cada cliente

print('El servidor está listo para recibir solicitudes...')

while True:
    rand = random.randint(0, 10)
    message, address = serverSocket.recvfrom(1024)
    message = message.decode()
    
    if message.startswith('Heartbeat'):
        parts = message.split()
        client_address = address[0]
        sequence_number = int(parts[1])
        current_time = float(parts[2])
        client_status[client_address] = current_time
        response_message = f'Heartbeat response to {client_address}'
        serverSocket.sendto(response_message.encode(), address)
    
    if rand < 4:
        continue
    
    if message.startswith('Ping'):
        message = message.upper()
        serverSocket.sendto(message.encode(), address)

    # Detectar pérdida de clientes
    current_time = time.time()
    for client_address, last_time in list(client_status.items()):
        if current_time - last_time > 30:  # Si no se recibe un latido en 30 segundos, se asume que el cliente ha fallado
            print(f'Client at {client_address} has failed')
            del client_status[client_address]
