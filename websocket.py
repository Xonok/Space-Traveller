import hashlib,base64,time,_thread,queue,json,struct,traceback

web_magic = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

class Handler():
	def __init__(self,recv_handler,drop_handler):
		self.clients = []
		self.to_send = queue.Queue()
		self.recv_handler = recv_handler
		self.drop_handler = drop_handler
		_thread.start_new_thread(self.sender,())
	def handshake(self,client):
		web_key = client.headers.get("Sec-WebSocket-Key")
		key_hash = hashlib.sha1((web_key+web_magic).encode())
		response_key = base64.b64encode(key_hash.digest()).decode()
		client.send_response(101)
		client.send_header("Upgrade","websocket")
		client.send_header("Connection","Upgrade")
		client.send_header("Sec-WebSocket-Accept",response_key)
		client.send_header("Content-Length",0)
		client.end_headers()
		client.close_connection = False
	def recv(self,client):
		time.sleep(0.1)
		client.headers.get('Content-Length')
		size = client.rfile.read(2)[1]-128
		mask = client.rfile.read(4)
		data = client.rfile.read(size)
		msg = ""
		for i,b in enumerate(data):
			msg += chr(b ^ mask[i%4])
		return msg
	def send(self,client,msg):
		response_bytes = bytearray()
		response_bytes.extend(map(ord,msg))
		msg_length = len(response_bytes)
		if msg_length <= 125:
			header = bytearray([0x81, msg_length])
		elif msg_length <= 65535:
			header = bytearray([0x81, 126]) + struct.pack('>H', msg_length)
		else:
			header = bytearray([0x81, 127]) + struct.pack('>Q', msg_length)
		response_data = bytearray(header)
		response_data.extend(response_bytes)
		client.wfile.write(response_data)
	def send_msg(self,client,msg):
		data = json.dumps(msg)
		self.send(client,data)
	def send_error(self,client,msg):
		data = {
			"type": "error",
			"text": msg
		}
		self.send_msg(client,data)
	def receiver(self,client):
		while True:
			try:
				msg = self.recv(client)
				self.recv_handler(self,client,msg)
				#to_send.put(msg)
			except Exception:
				print("Websocket error: ")
				print(traceback.format_exc())
				self.drop_handler(self,client)
				break
	def sender(self):
		while True:
			try:
				msg = self.to_send.get()
				for c in clients:
					self.send(c,msg)
			except:
				pass
	def add_client(self,client):
		self.clients.append(client)
		self.handshake(client)
		self.receiver(client)
		self.clients.remove(client)