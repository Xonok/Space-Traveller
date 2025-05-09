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
		path = urlparse(self.path).path
		
		#GOAL FOR NOW
		#Remove all references to path.
		#Path is used to determine what commands are valid and what information to send back.
		#Minimally, it's necessary to remove all message-response-related code.
		#Then each command could be allowed on any page.
		#Commands don't necessarily have to be in the command system (yet).
		#However, what happens to special cases like battle and login?
		#When not logged in, all commands except account creation and login need to be rejected.
		#Battle makes a large swathe of commands invalid too.
		#-Movement, jumping, hwr
		#-Gathering, item transfer, factories, looting, dropping items
		#Some commands are fine to allow though.
		#-Looking at the map. (including nav)
		#-Profile, wiki, etc.
		
		#STEPS
		#1. Move authentication into the command system. 
		#Make a special flag that allows some commands to work without authentication.
		#E.g, making an account and logging in
		#2. Make commands that need cdata/udata specifically ask for it.
		#- If they can't be provided, send an error to the user.
		#3. Block certain commands if in battle. Move, jump, hwr, gather, build, transfer
		#- If a command is blocked, provide a link that leads to the battle or something.
		#4. Start moving commands over.
		#- Some commands return data. Those might need special effort to move to the command system.
		#5. Minor things: timing
		
		#How to handle stuff that should run for many commands?
		#- add it to the system
		#How to handle notifying the server of currently active character and ship?
		#- optional params that must not be required by any command.
		
		try:
			try:
				content_len = int(self.headers.get('Content-Length'))
				data = json.loads(self.rfile.read(content_len))
			except:
				raise error.User("Invalid JSON data.")
			#TEMP: command system deletes the command and key parameters, so need to check them earlier.
			self.check(data,"command")
			command = data["command"]
			username = None
			if "key" in data:
				username = user.check_key(data["key"])
			#generic command system
			response = Command.process(self,data)
			
			udata = defs.users.get(username)
			cdata = defs.characters.get(udata["active_character"])
			msg = {}
			if cdata:
				cname = cdata["name"]
				pship = ship.get(cdata.ship())
				psystem = pship.get_system()
				px,py = pship.get_coords()
				tstructure = structure.get(psystem,px,py)
				pbattle = Battle.get(cdata)
				if not pbattle and path == "/battle.html":
					raise error.Page()
			if path == "/lore.html":
				msg = {"lore_entries":lore.entries()}
				if command == "request-lore":
					self.check(data,"name")
					msg["request_name"] = data["name"]
					msg["request_data"] = lore.request(data["name"])
			elif path == "/map.html":
				msg = {}
				if command == "get-map-data":
					self.check(data,"star")
					msg["star_data"] = map.get_star_data(data)
			elif path == "/art.html":
				msg = {}
				msg["images"] = art.get_all_images()
			elif path == "/profile.html":
				msg = {}
				msg["achievements"] = exploration.get_achievements(cdata)
				msg["net_worth"] = Item.query.net_worth(cdata)
				msg["pships"] = ship.character_ships(cdata["name"])
				msg["structures"] = structure.character_structures(cdata["name"])
				msg["reputation"] = reputation.get_total(cdata["name"])
				msg["skills"] = Skill.get_character_skills(cdata)
			elif path == "/user.html":
				msg = {}
				self.send_msg(200,json.dumps(msg))
			elif path == "/wiki.html":
				msg = {}
				if command == "get-wiki-page":
					self.check(data,"page")
					wiki.get_page(data,msg,cdata)
			msg = msg | response
			msgs = self.get_messages()
			msg["messages"] = msgs
			Query.process_command(command,msg,udata,cdata)
			self.send_msg(200,json.dumps(msg))
		except error.Auth:
			self.redirect(303,"text/html","login.html")
		except error.Char:
			self.redirect(303,"text/html","characters.html")
		except error.Page:
			self.redirect(303,"text/html","nav.html")
		except error.Battle:
			self.redirect(303,"text/html","battle.html")
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
		if compress:
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