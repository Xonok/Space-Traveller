import socket,_thread,email,sys,time,ssl,types,errno,traceback
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
	def __init__(self,request,client_address,server):
		self.request = request #socket apparently, but called request for compatibility with http.server
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
		lines = []
		while True:
			raw = self.rfile.readline()
			line = raw.decode('utf-8')
			if not line:
				break # connection closed
			if line == "\r\n":
				break # headers ended
			lines.append(line)
		if not len(lines):
			return
		self.req_line = lines[0].strip()
		self.req = lines[0].split(" ")
		if len(self.req) >= 3:
			self.request_version = len(self.req[2])
		if len(self.req) < 2:
			self.wfile.write(b"\r\n\r\n")
			self.wfile.flush()
			self.wfile.close()
			self.rfile.close()
			request.shutdown(socket.SHUT_WR)
			return
		self.headers = {}
		for i,line in enumerate(lines):
			if i == 0: continue
			if line == "": continue
			args = line.split(":",1)
			if len(args) > 1:
				k,v = line.split(":",1)
				self.headers[k.strip()] = v.strip()
		self.path = self.req[1]
		time_string = self.log_date_time_string()
		print(self.client_address[0]+" "+time_string+" "+self.req_line+" \r\n",sep='',end='')
		#self.log_message('"%s" %s %s',self.requestline, str(code), str(size))
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
	def log_date_time_string(self):
		"""Return the current time formatted for logging."""
		now = time.time()
		year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
		s = "%02d/%3s/%04d %02d:%02d:%02d" % (day, self.monthname[month], year, hh, mm, ss)
		return s
	monthname = [None,'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
class DumbHTTP:
	def __init__(self,addr,handler):
		self.socket = socket.socket()
		self.addr = addr
		self.handler = handler
		self.startup_success = False
	def handler_wrapper(self,s,c):
		try:
			s = self.socket.context.wrap_socket(s,
				do_handshake_on_connect=self.socket.do_handshake_on_connect,
				suppress_ragged_eofs=self.socket.suppress_ragged_eofs,
				server_side=True)
			self.handler(s,c,self)
		except ssl.SSLEOFError:
			pass
			#print("SSL EOF error. Doesn't matter.(DumbHTTP)")
		except ssl.SSLError:
			pass
			#print("SSL error. Doesn't matter. (DumbHTTP)")
		except ConnectionResetError:
			pass
			#print("Connection reset error. Doesn't matter.(DumbHTTP)")
		except ConnectionAbortedError:
			pass
			#print("Connection aborted error. Doesn't matter.(DumbHTTP)")
		except socket.error as e:
			if e.args[0] == errno.EWOULDBLOCK:
				pass
				#print("Socket would block. Doesn't matter.")
		except Exception as e:
			print("Ignoring unhandled exception for the sake of stability.(DumbHTTP)")
			print(traceback.format_exc())
	def serve_forever(self):
		print("Serving you forever:",self.addr)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind((self.addr))
		self.socket.listen()
		self.socket.settimeout(1)
		self.startup_success = True
		while True:
			try:
				if type(self.socket) == socket.socket:
					s,c = self.socket.accept()
					_thread.start_new_thread(self.handler,(s,c,self))
				elif type(self.socket) == ssl.SSLSocket:
					s,c = super(type(self.socket),self.socket).accept()
					_thread.start_new_thread(self.handler_wrapper,(s,c))
					#self.handler_wrapper(s,c)
				else:
					print(type(self.socket))
					raise Exception("Unknown socket type.")
			except ssl.SSLEOFError:
				pass
				#print("SSL EOF error. Doesn't matter.(DumbHTTP)")
			except ssl.SSLError:
				pass
				#print("SSL error. Doesn't matter. (DumbHTTP)")
			except ConnectionResetError:
				pass
				#print("Connection reset error. Doesn't matter.(DumbHTTP)")
			except ConnectionAbortedError:
				pass
				#print("Connection aborted error. Doesn't matter.(DumbHTTP)")
			except socket.error as e:
				if e.args[0] == errno.EWOULDBLOCK:
					pass
					#print("Socket would block. Doesn't matter.")
			except Exception:
				print("Ignoring unhandled exception for the sake of stability.(DumbHTTP)")
				print(traceback.format_exc())
		self.socket.close()
		print("Stopped serving forever. How?")
