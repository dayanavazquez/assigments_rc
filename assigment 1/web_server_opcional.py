import socket
import threading

def handle_client(client_socket):
    request = client_socket.recv(1024).decode()  # Receive data from the client (HTTP request)
    
    # Process the request, e.g., by serving a file or generating a response
    if request:
        # Split the request into lines and extract the requested file path
        request_lines = request.split('\r\n')
        if len(request_lines) > 0:
            request_line = request_lines[0]
            _, file_path, _ = request_line.split(' ')

            if file_path == "/":
                file_path = "/index.html"  # Default file to serve

            try:
                with open("www" + file_path, "rb") as file:
                    content = file.read()
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode() + content
            except FileNotFoundError:
                response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n".encode() + b"404 Not Found"

            client_socket.send(response)
    
    client_socket.close()  # Close the client socket

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8080))  # Bind the server to a specific address and port
    server.listen(5)  # Listen for incoming connections

    print("Server listening on port 8080...")

    while True:
        client, addr = server.accept()  # Accept client connections
        print(f"Accepted connection from {addr[0]}:{addr[1]}")

        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

if __name__ == "__main__":
    main()
