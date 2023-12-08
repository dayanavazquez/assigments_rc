from socket import *
import sys

if len(sys.argv) <= 1:
    print('Usage: "python server.py server_ip"\n[server_ip: IP Address Of Proxy Server')
    sys.exit(2)
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind((sys.argv[1], 8081))
tcpSerSock.listen(5)

while True:
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)

    try:
        message = tcpCliSock.recv(1024)
        if not message:
            continue
        message = message.decode('utf-8', 'ignore')
        print(message)
        first_line = message.split('\n')[0].strip()

        if first_line.startswith('CONNECT'):
            # Handle CONNECT method for HTTPS
            print('Handling CONNECT method (HTTPS)')
            host_port = first_line.split()[1]
            host, port = host_port.split(':')
            remote_sock = socket(AF_INET, SOCK_STREAM)
            remote_sock.connect((host, int(port)))
            tcpCliSock.send("HTTP/1.1 200 Connection established\r\n\r\n".encode())
            while True:
                data = tcpCliSock.recv(4096)
                if not data:
                    break
                remote_sock.sendall(data)

        elif first_line.startswith('GET'):
            filename = first_line.split()[1].partition("/")[2]
            print(first_line.split())
            print(first_line.split()[1].partition("/"))
            print(f'FILENAME: {filename}')
            fileExist = "false"

            filetouse = "./cache/" + filename.replace('/', '')

            try:
                with open(filetouse, "r") as f:
                    outputdata = f.readlines()
                    fileExist = "true"
                    tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode())
                    tcpCliSock.send("Content-Type:text/html\r\n".encode())

                    resp = "\r\n".join(outputdata)
                    tcpCliSock.sendall(resp.encode())

                    print('Read from cache')
            except FileNotFoundError:
                if fileExist == "false":
                    c = socket(AF_INET, SOCK_STREAM)
                    print(filename)

                    try:
                        c.connect((filename, 80))
                        fileobj = c.makefile("wb", 0)
                        fileobj.write(f"GET http://{filename} HTTP/1.0\r\n".encode())
                        fileobj.write("\r\n".encode())
                        with open(filetouse, "wb") as tmpFile:
                            while True:
                                resp = c.recv(1024)
                                if not resp:
                                    tcpCliSock.close()
                                    break
                                tmpFile.write(resp)
                                tcpCliSock.send(resp)

                    except Exception as e:
                        print("Illegal request")
                        print(e)
                    finally:
                        c.close()

    except Exception as e:
        print("Error:", e)

    finally:
        tcpCliSock.close()

tcpSerSock.close()