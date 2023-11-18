import time
from socket import *

server_host = '127.0.0.1'  # Cambia esto por la IP o el nombre del servidor real
server_port = 12000

client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(1.0)

total_pings = 10
successful_pings = 0
rtt_list = []

for sequence_number in range(1, total_pings + 1):
    start_time = time.time()
    message = f'Ping {sequence_number} {start_time}'
    client_socket.sendto(message.encode(), (server_host, server_port))
    
    try:
        response, server_address = client_socket.recvfrom(1024)
        end_time = time.time()
        rtt = end_time - start_time
        rtt_list.append(rtt)
        print(f'Response from {server_host}: {response.decode()}, RTT = {rtt} seconds')
        successful_pings += 1
    except timeout:
        print('Request timed out')

client_socket.close()

if successful_pings > 0:
    min_rtt = min(rtt_list)
    max_rtt = max(rtt_list)
    avg_rtt = sum(rtt_list) / successful_pings
    packet_loss_rate = (total_pings - successful_pings) / total_pings * 100
    print(f'\nPing statistics for {server_host}:')
    print(f'    Packets: Sent = {total_pings}, Received = {successful_pings}, Lost = {total_pings - successful_pings} ({packet_loss_rate:.2f}% loss)')
    print(f'Round trip times (RTT) in seconds:')
    print(f'    Minimum = {min_rtt:.6f} s, Maximum = {max_rtt:.6f} s, Average = {avg_rtt:.6f} s')
else:
    print(f'\nNo responses received. All pings lost.')