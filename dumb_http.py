import socket,_thread,email,sys,time,ssl,types
from http import HTTPStatus

def wwrite(wfile,*args):
	try:
		wfile._write(*args)
	except ssl.SSLEOFError:
		print("SSL EOF error. Doesn't matter.(DumbHandler)")
	except ssl.SSLError:
		print("SSL error. Doesn't matter. (DumbHandler)")
	except ConnectionResetError:
		print("Connection reset error. Doesn't matter.(DumbHandler)")
	except ConnectionAbortedError:
		print("Connection aborted error. Doesn't matter.(DumbHandler)")

class DumbHandler:
	server_version = "DumbHTTP/1.0"
	sys_version = "Python/" + sys.version.split()[0]
	responses = {
		v: (v.phrase, v.description)
		for v in HTTPStatus.__members__.values()
	}
	def get_lines(self):
		lines = []
		while True:
			line = self.rfile.readline(10000).decode('utf-8')
			lines.append(line)
			if lines[-1] == "\r\n" and line == "\r\n":
				break
		return lines
	def __init__(self,request,client_address,server):
		self.request = request #socket apparently
		self.client_address = client_address #ip and port
		self.server = server #server object
		self.protocol_version = "HTTP/1.0"
		self.request_version = "HTTP/0.9"
		self.close_connection = True
		self.buffer = []
		wbufsize = 0
		rbufsize = -1
		self.wfile = request.makefile('wb',wbufsize)
		self.rfile = request.makefile('rb', rbufsize)
		self.wfile._write = self.wfile.write
		self.wfile.write = types.MethodType(wwrite,self.wfile)
		lines = self.get_lines()
		self.req = lines[0].split(" ")
		if len(self.req) >= 3:
			self.request_version = len(self.req[2])
		self.headers = {}
		for i,line in enumerate(lines):
			if i == 0: continue
			if line == "": continue
			args = line.split(":",1)
			if len(args) > 1:
				k,v = line.split(":",1)
				self.headers[k] = v
		self.path = self.req[1]
		match self.req[0]:
			case "GET":
				self.do_GET()
			case "POST":
				self.do_POST()
			case _:
				print("Unknown request type:",self.req)
		self.wfile.write(b"\r\n\r\n")
		self.wfile.flush()
		self.wfile.close()
		self.rfile.close()
		request.shutdown(socket.SHUT_WR)
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
			self.wfile.flush()
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
		self.socket.bind((self.addr))
		self.socket.listen()
		while True:
			try:
				s,c = self.socket.accept()
				_thread.start_new_thread(self.handler,(s,c,self))
			except ssl.SSLEOFError:
				print("SSL EOF error. Doesn't matter.(DumbHTTP)")
			except ssl.SSLError:
				print("SSL error. Doesn't matter. (DumbHTTP)")
			except ConnectionResetError:
				print("Connection reset error. Doesn't matter.(DumbHTTP)")
			except ConnectionAbortedError:
				print("Connection aborted error. Doesn't matter.(DumbHTTP)")
			except Exception as e:
				print("Ignoring unhandled exception for the sake of stability.(DumbHTTP)")
				print(e)
		print("Stopped serving forever. How?")