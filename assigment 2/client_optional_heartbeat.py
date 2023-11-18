import time
from socket import *

server_host = '127.0.0.1'  # Cambia esto por la IP o el nombre del servidor real
server_port = 12001  # Utiliza un puerto diferente al del servidor de ping

client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(1.0)

sequence_number = 1

while True:
    start_time = time.time()
    message = f'Heartbeat {sequence_number} {start_time}'
    client_socket.sendto(message.encode(), (server_host, server_port))
    
    try:
        response, server_address = client_socket.recvfrom(1024)
        end_time = time.time()
        rtt = end_time - start_time
        print(f'Heartbeat response from {server_host}, RTT = {rtt} seconds')
    except timeout:
        print(f'Heartbeat request to {server_host} timed out')
    
    sequence_number += 1
    time.sleep(5)  # Envía un latido cada 5 segundos

client_socket.close()
