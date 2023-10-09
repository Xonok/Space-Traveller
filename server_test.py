import socket,gzip

addr = ("localhost",80)
s = socket.socket()
s.connect(addr)
s.send("GET /navbar.html\r\n\r\n".encode())
while True:
	data = s.recv(1024)
	incoming = data.decode(encoding='utf-8')
	if not incoming: break
	print(incoming)
