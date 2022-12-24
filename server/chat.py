import hashlib,base64,time,gzip

web_magic = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

#Automatically join general channel.
#When chat is open, automatically receive any new messages
def get(self):
	print("ASYNC")
	print(self.request_version)
	web_key = self.headers.get("Sec-WebSocket-Key")
	key_hash = hashlib.sha1((web_key+web_magic).encode())
	response_key = base64.b64encode(key_hash.digest()).decode()
	for a,b in vars(self).items():
		print(a,b)
	self.send_response(101)
	self.send_header("Upgrade","websocket")
	self.send_header("Connection","Upgrade")
	self.send_header("Sec-WebSocket-Accept",response_key)
	self.send_header("Content-Length",0)
	self.end_headers()
	self.close_connection = False
	while True:
		time.sleep(0.1)
		self.headers.get('Content-Length')
		size = self.rfile.read(2)[1]-128
		print(size)
		mask = self.rfile.read(4)
		print(mask)
		data = self.rfile.read(size)
		print(data)
		msg = ""
		for i,b in enumerate(data):
			msg += chr(b ^ mask[i%4])
			print(i,b,mask[i%4])
		print(msg)
		response_msg = "world"
		response_bytes = bytearray()
		response_bytes.extend(map(ord,response_msg))
		print(response_bytes)
		new_size = len(response_bytes)
		response_data = bytearray([129,new_size])
		response_data.extend(response_bytes)
		print(response_data)
		self.wfile.write(response_data)
		#print((data ^ mask).to_bytes(size,"big"))
		#print(data.to_bytes(size,"big"))
		#size = self.rfile.read(2)[1]
		#print("A",str(size))
		#if size < 126:
		#	size = self.rfile.read(2)
		#	print("B",str(size))
		#elif size == 127:
		#	size = self.rfile.read(4)
		#	print("C",str(size))
		#data = self.rfile.read(size)
		#print(data)
		#size = int.from_bytes(self.rfile.read(4),"little")
		#print(size)
		#blah = self.rfile.read(size)
		#print(size,blah)
