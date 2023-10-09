import socket,_thread,email,sys,time
from http import HTTPStatus

class DumbHandler:
	server_version = "DumbHTTP/1.0"
	sys_version = "Python/" + sys.version.split()[0]
	responses = {
		v: (v.phrase, v.description)
		for v in HTTPStatus.__members__.values()
	}
	def __init__(self,s,client):
		self.protocol_version = "HTTP/1.0"
		self.request_version = "HTTP/0.9"
		self.buffer = []
		raw_msg = s.recv(1024).decode('utf-8')
		lines = raw_msg.split("\r\n")
		self.req = lines[0].split(" ")
		if len(self.req) >= 3:
			self.request_version = len(self.req[2])
		self.headers = {}
		for i,line in enumerate(lines):
			if i == 0: continue
			if line == "": continue
			k,v = line.split(":",1)
			self.headers[k] = v
		wbufsize = 0
		self.wfile = s.makefile('wb',wbufsize)
		self.path = self.req[1]
		match self.req[0]:
			case "GET":
				self.do_GET()
			case "POST":
				self.do_POST()
			case _:
				print("Unknown request type:",self.req)
		print(lines[0])
		#print(self.headers)
		#response = "Post "+self.req[1]
		#s.send(response.encode())
	def do_GET(self):
		print("Implement do_GET plez")
	def do_POST(self):
		print("Implement do_POST plez")
	def send_response(self,code,message=None):
		if message is None:
			if code in self.responses:
				message = self.responses[code][0]
			else:
				message = ''
		self.buffer.append(("%s %d %s\r\n" % (self.protocol_version, code, message)).encode('latin-1','strict'))
		self.send_header('Server', self.version_string())
		self.send_header('Date', self.date_time_string())
	def send_header(self,keyword,value):
		if self.request_version != 'HTTP/0.9':
			self.buffer.append(("%s: %s\r\n" % (keyword, value)).encode('latin-1', 'strict'))
	def end_headers(self):
		if self.request_version != 'HTTP/0.9':
			self.buffer.append(b"\r\n")
			self.wfile.write(b"".join(self.buffer))
	def version_string(self):
		return self.server_version + ' ' + self.sys_version
	def date_time_string(self, timestamp=None):
		if timestamp is None:
			timestamp = time.time()
		return email.utils.formatdate(timestamp, usegmt=True)
class DumbHTTP:
	def __init__(self,addr,handler):
		self.socket = socket.socket()
		self.addr = addr
		self.handler = handler
	def serve_forever(self):
		_thread.start_new_thread(self.serve_forever2,(self.socket,self.addr,self.handler))
		#_thread.start_new_thread(self.serve_forever2,(socket.socket(),(self.addr[0],80),self.handler))
	def serve_forever2(self,sock,addr,handler):
		sock.bind((addr))
		sock.listen()
		while True:
			_thread.start_new_thread(handler,sock.accept())
		print("Stopped serving forever. How?")


#addr = ('localhost',80)
#httpd = DumbHTTP(addr,DumbHandler)
#httpd.serve_forever()