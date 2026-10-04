#CODE STATUS - too many responsibilities
#*This file should only set up the server and let other files handle the rest.
#*Sometimes the live server stops responding. Especially noticeable with websockets.
#Maybe we should write our own simplified implementation?

import os,traceback,time,math
from lib import dumb_http,Config
from urllib.parse import urlparse
from server import io,defs,error,Chat,cache,Command,Analysis,log,Init,tick,info

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
		path = self.filepath
		if path == "chat_async":
			Chat.connect(self)
			return
		if path == "":
			self.redirect(302,"main.html")
			return
		_,ftype = os.path.splitext(path)
		if ftype == "":
			ftype = ".html"
		fconf = Config.get("files").get(ftype)
		if not fconf:
			fconf = Config.get("files").get(".html")
		folder = fconf.get("folder")
		mime = fconf.get("mime")
		compress = fconf.get("compress",False)
		if folder:
			file = os.path.join(io.cwd,folder,*path.split('/'))
		else:
			file = os.path.join(io.cwd,*path.split('/'))
		if not os.path.exists(file):
			#TODO: stop inlining 404 page name, add a standard 404 that can be overriden.
			file = os.path.join(io.cwd,"_cache","404.html")
			mime = "text/html; charset=utf-8"
			self.send_file(404,mime,file,compress=True)
		else:
			self.send_file(200,mime,file,compress=compress)
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
