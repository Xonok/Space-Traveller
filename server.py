import traceback,json
from lib import Config
from urllib.parse import urlparse
from server import io,defs,error,Chat,cache,Command,Analysis,log,Init,tick,info

### Temporarily here, but belongs somewhere entirely different
def change_view(client,name):
	msg = {
		"event": "page-change",
		"page": name,
		"in_battle": name == "battle"
	}
	xhttp.send_json(client,200,msg)
###

from xlib_dev import xhttp
def handler(req):
	client = req["client"]
	method = req["method"]
	payload = req["payload"]
	
	if method == "GET":
		do_get(req)
	if method == "POST":
		try:
			data = json.loads(payload)
		except json.JSONDecodeError as e:
			xhttp.send_str(client,400,str(e))
			return
		except Exception as e:
			xhttp.send_str(client,500,"Server error")
			return
		
		try:
			msg = Command.process(client,data,req,xhttp.send_str)
			xhttp.send_json(client,200,msg)
		except error.Auth:
			xhttp.send_redirect(client,303,"login.html")
		except error.Char:
			change_view(client,"characters")
		except error.Page:
			change_view(client,"nav")
		except error.Battle:
			change_view(client,"battle")
		except error.User as e:
			xhttp.send_str(client,400,str(e))
		except error.Fine:
			return
		except Exception:
			io.clear_writes()
			error_txt = traceback.format_exc()
			log.log("error",error_txt)
			xhttp.send_str(client,500,"Server error")
			print(error_txt)
def do_get(req):
	config = Config.get("files")
	
	if req["filepath"] == "":
		req["filepath"] = "main.html"
	
	success = False
	if req["filepath"] == "chat_async":
		methods = {
			"on_message": Chat.api.on_message,
			"on_open": Chat.api.on_open,
			"on_close": Chat.api.on_close
		}
		success = xhttp.serve_websocket(req,**methods)
	if not success:
		success = xhttp.serve_files(req,config)

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
	promise = xhttp.serve_forever(("",http_port),handler,(),new_thread=True)
	xhttp.await_startup(promise)
	print("Server successfully started.")

main()
