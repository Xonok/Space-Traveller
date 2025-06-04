#CODE STATUS - too many responsibilities
#*This file should only set up the server and let other files handle the rest.
#*Commands in particular should not depend on page and should be moved to the new system.
#*Sometimes the lives server stops responding. The reason has something to do with http.server
#Maybe we should write our own simplified implementation?

import http.server,os,ssl,json,gzip,_thread,traceback,time,math
import dumb_http
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from server import io,user,items,ship,defs,structure,map,quest,error,chat,hive,loot,gathering,build,archaeology,spawner,stats,Battle,config,lore,character,Item,art,Skill,Character,exploration,reputation,wiki,html,cache,Query,Command,Analysis,AI,log

new_server = True

baseclass = dumb_http.DumbHandler if new_server else BaseHTTPRequestHandler
class MyHandler(baseclass):
	def __init__(self,*args):
		if not config.config["logging"]:
			self.log_request = self.no_log
		super().__init__(*args)
	def do_POST(self):
		try:
			try:
				content_len = int(self.headers.get('Content-Length'))
				data = json.loads(self.rfile.read(content_len))
			except:
				raise error.User("Invalid JSON data.")
			msg = Command.process(self,data)
			self.send_msg(200,json.dumps(msg))
		except error.Auth:
			self.redirect(303,"text/html","login.html")
		except error.Char:
			self.change_view("characters")
		except error.Page:
			self.change_view("nav")
		except error.Battle:
			self.change_view("battle")
		except error.User as e:
			self.send_msg(400,str(e))
		except error.Fine:
			return
		except Exception:
			io.clear_writes()
			error_txt = traceback.format_exc()
			log.log("error",error_txt)
			self.send_msg(500,"Server error")
			print(error_txt)
	def do_GET(self):
		now = time.time()
		self.protocol_version = "HTTP/1.1"
		url_parts = urlparse(self.path)
		path = url_parts.path
		if path.startswith('/'):
			path = path[1:]
		if path == "chat_async":
			# chat.get(self)
			chat.do_GET(self)
			return
		_,ftype = os.path.splitext(path)
		ftypes = {
			".js": "",
			".css": "",
			".png": "",
			".webp": "",
			".jpg": "",
			".svg": "",
			".html": "html"
		}
		folder = ftypes.get(ftype)
		if folder:
			file = os.path.join(io.cwd,folder,*path.split('/'))
		else:
			file = os.path.join(io.cwd,*path.split('/'))
		if path == "robots.txt":
			self.send_file(200,"text/plain",file,True)
		elif path == '' or (not os.path.exists(file) and file not in cache.cache):
			if ftype == ".html" or ftype == '' or path == '':
				self.redirect(302,"text/html; charset=utf-8","/main.html")
			else:
				self.response(404,"text/plain")
		elif ftype == ".js":
			self.send_file(200,"text/javascript; charset=utf-8",file,True)
		elif ftype == ".css":
			self.send_file(200,"text/css; charset=utf-8",file,True)
		elif ftype == ".png":
			self.send_file(200,"image/png",file)
		elif ftype == ".webp":
			self.send_file(200,"image/webp",file)
		elif ftype == ".jpg":
			self.send_file(200,"image/jpeg",file)
		elif ftype == ".svg":
			self.send_file(200,"image/svg+xml",file,True)
		elif ftype == ".html":
			print(path)
			self.send_html(200,file)
			# self.send_file(200,"text/html",file,config.config["text_cache"])
		else:
			self.send_html(404,os.path.join(io.cwd,"html","404.html"))
		later = time.time()
		d_t = later-now
		# print("GET",path,str(math.floor(d_t*1000))+"ms")
	def no_log(self,*args):
		#This function is used to stop the server from logging.
		return
	def add_message(self,text):
		if not hasattr(self,"messages"):
			setattr(self,"messages",[])
		self.messages.append(text)
	def get_messages(self):
		if hasattr(self,"messages"):
			return self.messages
		return []
	def response(self,code,type,opt_type=None,opt_data=None,encoding=None):
		self.send_response(code)
		self.send_header("Content-Type",type)
		if encoding:
			self.send_header("Content-Encoding",encoding)
		self.send_header("Access-Control-Allow-Origin","*")
		if opt_type and opt_data:
			self.send_header(opt_type,opt_data)
		self.end_headers()
	def send_msg(self,code,msg):
		self.response(code,"text/plain",encoding="gzip")
		data = bytes(msg,"utf-8")
		data2 = gzip.compress(data)
		self.wfile.write(data2)
	def send_json(self,msg):
		self.send_msg(200,json.dumps(msg))
	def send_file(self,code,type,path,compress=False):
		if path in cache.cache:
			data = cache.cache[path]
		else:
			data = io.get_file_data(path)
			if config.config["cache"]:
				cache.cache[path] = data
		if compress and len(data):
			data2 = gzip.compress(data)
			self.response(code,type,encoding="gzip")
			self.wfile.write(data2)
		else:
			self.response(code,type)
			self.wfile.write(data)
	def send_html(self,code,path):
		data = html.load(path)
		data2 = gzip.compress(data)
		encoding = "gzip"
		len_a = len(data)
		len_b = len(data2)
		type = "text/html; charset=utf-8"
		self.response(code,type,encoding=encoding)
		self.wfile.write(data2)
	def redirect(self,code,type,target):
		self.response(code,type,"Location",target)
	def change_view(self,name):
		msg = {
			"event": "page-change",
			"page": name,
			"in_battle": name == "battle"
		}
		self.send_json(msg)
	def check(self,msg,*args):
		for arg in args:
			if not arg in msg:
				raise error.User("Missing required \""+arg+"\"")
class HTTP_to_HTTPS(MyHandler):
	def do_POST(self):
		url_parts = urlparse(self.path)
		path = url_parts.path
		self.redirect(301,"text/html","https://"+self.headers["Host"]+path)
	def do_GET(self):
		url_parts = urlparse(self.path)
		path = url_parts.path
		self.redirect(301,"text/html","https://"+self.headers["Host"]+path)
server_type = dumb_http.DumbHTTP if new_server else http.server.ThreadingHTTPServer

# context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
# context.load_cert_chain(".ssh/certificate.pem",".ssh/key.pem")
# httpd = server_type(("", 443), MyHandler)
# httpd.socket = context.wrap_socket(httpd.socket,server_side=True)

# httpd2 = server_type(("", 80), HTTP_to_HTTPS)

def run(httpd):
	httpd.serve_forever()
	print("Server has stopped for some reason.")
print("Acquiring ports...")
httpd = None
httpd2 = None
if config.config["backend"]:
	httpd = server_type(("",8200),MyHandler)
	_thread.start_new_thread(run,(httpd,))
else:
	if config.config["ssl"]:
		context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
		context.load_cert_chain(".ssh/certificate.pem",".ssh/key.pem")
		httpd = server_type(("", 443), MyHandler)
		httpd.socket = context.wrap_socket(httpd.socket,server_side=True)

		httpd2 = server_type(("", 80), HTTP_to_HTTPS)
		_thread.start_new_thread(run,(httpd,))
		_thread.start_new_thread(run,(httpd2,))
	else:
		httpd = server_type(("", 80), MyHandler)
		_thread.start_new_thread(run,(httpd,))

MAX_TIMEOUT = 5 #seconds
start_time = time.time()
while True:
	if time.time()-start_time > MAX_TIMEOUT:
		print("Failed to acquire ports.")
		break
	if (httpd is None or httpd.startup_success) and (httpd2 is None or httpd2.startup_success):
	# if httpd3.startup_success:
	# if httpd.startup_success and httpd2.startup_success and httpd3.startup_success:
		print("Ports successfully acquired.")
		io.init()
		break
	time.sleep(0.1)