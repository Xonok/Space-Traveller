import hashlib,base64,time,_thread,queue,json,struct,traceback

web_magic = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

class Handler():
	def __init__(self,server,recv_handler):
		self.handshake_done = False
		self.server = server
		self.to_send = queue.Queue()
		self.recv_handler = recv_handler
		_thread.start_new_thread(self.sender,())
	def start(self):
		if not self.handshake_done:
			raise Exception("Need to do handshake before running .start on the websocket handler.")
		self.receiver()
	def handshake(self):
		server = self.server
		web_key = server.headers.get("Sec-WebSocket-Key")
		key_hash = hashlib.sha1((web_key+web_magic).encode())
		response_key = base64.b64encode(key_hash.digest()).decode()
		server.send_response(101)
		server.send_header("Upgrade","websocket")
		server.send_header("Connection","Upgrade")
		server.send_header("Sec-WebSocket-Accept",response_key)
		server.send_header("Content-Length",0)
		server.end_headers()
		server.close_connection = False
		self.handshake_done = True
	def recv(self,server):
		#Notes:
		#*Doesn't support continuation frames.
		b1 = server.rfile.read(1)[0]
		b2 = server.rfile.read(1)[0]
		fin = (b1 >> 7) & 1 #leftmost bit
		op = b1 & 0x0F #last 4 bits
		size = b2 & 0x7F #last 7 bits(we're ignoring the one that says whether there is a mask)
		if size == 126:
			size_bytes = server.rfile.read(2)
			size = struct.unpack('>H', size_bytes)[0]
		elif size == 127:
			size_bytes = server.rfile.read(8)
			size = struct.unpack('>Q', size_bytes)[0]
		
		mask = server.rfile.read(4)
		data = server.rfile.read(size)
		msg = ""
		if op == 1 or op == 9:
			unmasked = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
		if op == 1:
			msg = unmasked.decode("utf-8")
		if op == 9:
			self.send_pong(server,unmasked)
		return msg,op
	def send_pong(self,server,payload=b''):
		if len(payload) > 125:
			raise ValueError("Pong payload must be 125 bytes or less")
		b1 = 0b10001010  # 0x8A
		b2 = len(payload)
		frame = bytearray([b1, b2])
		frame.extend(payload)
		server.wfile.write(frame)
	def send(self,msg):
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
		self.server.wfile.write(response_data)
	def send_msg(self,msg):
		data = json.dumps(msg)
		self.send(data)
	def send_error(self,msg):
		data = {
			"event": "error",
			"txt": msg
		}
		self.send_msg(data)
	def receiver(self):
		while True:
			try:
				msg,op = self.recv(self.server)
				#op 8 is close socket
				if op == 8: break
				#op 1 is text frame. Most common for us.
				if op == 1:
					self.recv_handler(self,self.server,msg)
					continue
				if op == 9:
					continue
				print(op)
				#if other opcodes show up, print them
			except Exception:
				print("Websocket error: ")
				print(traceback.format_exc())
				break
	def sender(self):
		while True:
			try:
				msg = self.to_send.get()
				self.send(c,msg)
			except:
				pass