from socket import *
import ssl
import base64

subject = "Subject: Hello!\r\n"
msg = "\r\nI love computer networks!"
endmsg = "\r\n.\r\n"

msg = subject + msg + endmsg

# Mail server details
mailserver = 'smtp.gmail.com'  # Mail server (e.g., Google mail server)
mailserver_port = 587  # Mail server port

# Create socket called clientSocket and establish a TCP connection with mailserver
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((mailserver, mailserver_port))

recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '220':
    print('220 reply not received from server.')

# Send EHLO command and print server response.
heloCommand = 'EHLO Alice\r\n'
clientSocket.send(heloCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1)
if recv1[:3] != '250':
    print('250 reply not received from server.')

# Send STARTTLS command and print server response.
starttlsCommand = 'STARTTLS\r\n'
clientSocket.send(starttlsCommand.encode())
recv2 = clientSocket.recv(1024).decode()
print(recv2)
if recv2[:3] != '220':
    print('220 reply not received from server.')

# Wrap the socket with SSL/TLS using SSLContext
context = ssl.create_default_context()
ssl_clientSocket = context.wrap_socket(clientSocket, server_hostname=mailserver)

# Send EHLO again after STARTTLS
ssl_clientSocket.send(heloCommand.encode())
recv3 = ssl_clientSocket.recv(1024).decode()
print(recv3)
if recv3[:3] != '250':
    print('250 reply not received from server.')

# Send AUTH LOGIN command and print server response.
authCommand = 'AUTH LOGIN\r\n'
ssl_clientSocket.send(authCommand.encode())
recv4 = ssl_clientSocket.recv(1024).decode()
print(recv4)
if recv4[:3] != '334':
    print('334 reply not received from server.')

# Send username in base64 encoding
username = 'jean99lopezfernandez@gmail.com'
base64_user = base64.b64encode(username.encode()) + b'\r\n'
ssl_clientSocket.send(base64_user)
recv5 = ssl_clientSocket.recv(1024).decode()
print(recv5)
if recv5[:3] != '334':
    print('334 reply not received from server.')

# Send password in base64 encoding
password = 'vvbo mror vmjj vpzi'
base64_pwd = base64.b64encode(password.encode()) + b'\r\n'
ssl_clientSocket.send(base64_pwd)
recv6 = ssl_clientSocket.recv(1024).decode()
print(recv6)
if recv6[:3] != '235':
    print('235 Authentication failed')

# Send MAIL FROM command and print server response.
mail_from = 'MAIL FROM: <jean99lopezfernandez@gmail.com>\r\n'
ssl_clientSocket.send(mail_from.encode())
recv7 = ssl_clientSocket.recv(1024).decode()
print(recv7)
if recv7[:3] != '250':
    print('250 reply not received from server.')

# Send RCPT TO command and print server response.
rcpt_to = 'RCPT TO: <laragovantes@gmail.com>\r\n'  # Replace with the recipient's email address
ssl_clientSocket.send(rcpt_to.encode())
recv8 = ssl_clientSocket.recv(1024).decode()
print(recv8)
if recv8[:3] != '250':
    print('250 reply not received from server.')

# Send DATA command and print server response.
data = 'DATA\r\n'
ssl_clientSocket.send(data.encode())
recv9 = ssl_clientSocket.recv(1024).decode()
print(recv9)
if recv9[:3] != '354':
    print('354 reply not received from server.')

# Send message data.
ssl_clientSocket.send((msg + endmsg).encode())

# End the email with a period on a new line
end_email = '\r\n.\r\n'
ssl_clientSocket.send(end_email.encode())
recv10 = ssl_clientSocket.recv(1024).decode()
print(recv10)
if recv10[:3] != '250':
    print('250 reply not received from server.')

# Send QUIT command and get server response.
ssl_clientSocket.close()