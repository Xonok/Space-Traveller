#CODE STATUS - too many responsibilities
#*This file should only set up the server and let other files handle the rest.
#*Sometimes the live server stops responding. Especially noticeable with websockets.
#Maybe we should write our own simplified implementation?

import os,gzip,traceback,time,math
from lib import dumb_http,Config
from urllib.parse import urlparse
from server import io,defs,error,Chat,html,cache,Command,Analysis,log,Init,tick,info

class MyHandler(dumb_http.DumbHandler):
	cname = None #this needs to go, but stuff will currently break without it.
	def do_POST(self):
		try:
			data = super().load_json()
		except dumb_http.INVALID_JSON as e:
			self.send_str(400,str(e))
		try:
			msg = Command.process(self,data)
			self.send_json(msg)
		except error.Auth:
			self.redirect(303,"login.html")
		except error.Char:
			self.change_view("characters")
		except error.Page:
			self.change_view("nav")
		except error.Battle:
			self.change_view("battle")
		except error.User as e:
			self.send_str(400,str(e))
		except error.Fine:
			return
		except Exception:
			io.clear_writes()
			error_txt = traceback.format_exc()
			log.log("error",error_txt)
			self.send_str(500,"Server error")
			print(error_txt)
	def do_GET(self):
		now = time.time()
		url_parts = urlparse(self.path)
		path = url_parts.path
		if path.startswith('/'):
			path = path[1:]
		if path == "chat_async":
			Chat.connect(self)
			return
		_,ftype = os.path.splitext(path)
		if ftype == "":
			ftype = ".html"
		fconf = Config.get("files").get(ftype)
		folder = fconf.get("folder")
		mime = fconf.get("mime")
		compress = fconf.get("compress",False)
		if folder:
			file = os.path.join(io.cwd,folder,*path.split('/'))
		else:
			file = os.path.join(io.cwd,*path.split('/'))
		if path == "":
			self.send_html(302,os.path.join(io.cwd,"html","main.html"))
		elif not os.path.exists(file) and file not in cache.cache:
			self.send_html(404,os.path.join(io.cwd,"html","404.html"))
		elif ftype == ".html":
			print(path)
			self.send_html(200,file)
			# self.send_file(200,"text/html",file,Config.get("server")["text_cache"])
		elif fconf:
			self.send_file(200,mime,file,compress=compress)
		else:
			self.send_html(404,os.path.join(io.cwd,"html","404.html"))
		later = time.time()
		d_t = later-now
		# print("GET",path,str(math.floor(d_t*1000))+"ms")
	def add_message(self,text):
		if not hasattr(self,"messages"):
			setattr(self,"messages",[])
		self.messages.append(text)
	def get_messages(self):
		if hasattr(self,"messages"):
			return self.messages
		return []
	def send_file(self,code,mime,path,compress=False):
		if path in cache.cache:
			data = cache.cache[path]
		else:
			data = io.get_file_data(path)
			if Config.get("server")["cache"]:
				cache.cache[path] = data
		if compress and len(data):
			self.send_response2(code=code,mime=mime,encoding="gzip",payload=data)
		else:
			self.send_response2(code=code,mime=mime,payload=data)
	def send_html(self,code,path):
		data = html.load(path)
		data2 = gzip.compress(data)
		encoding = "gzip"
		len_a = len(data)
		len_b = len(data2)
		mime = "text/html; charset=utf-8"
		self.send_response2(code=code,mime=mime,encoding=encoding)
		self.wfile.write(data2)
	def change_view(self,name):
		msg = {
			"event": "page-change",
			"page": name,
			"in_battle": name == "battle"
		}
		self.send_json(msg)

def main():
	init_game()
	init_net()
	print("Saving enabled.")
	io.init()
def init_game():
	print("Reading configs.")
	Config.no_omissions("server",use_defaults=True)
	Config.no_omissions("files",use_defaults=True)
	Config.read_all()
	print("Reading game data")
	defs.init()
	print("Running initializers.")
	Init.run()
	print("Calculating idata hash.")
	defs.init_idata()
	print("Starting tick timer.")
	tick.init()
	print("Loading done.")
	info.display()
	
	#Secondary tasks
	Analysis.itemcount.run()
def init_net():
	http_port = Config.get("server").get("http_port")
	httpd = dumb_http.DumbHTTP(("",http_port),MyHandler,start=True,new_thread=True)
	httpd.await_startup()
	print("Server successfully started.")

main()
