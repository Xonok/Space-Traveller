import traceback,json
from lib import Config
from server import Analysis,Chat,Command,Init,Misc,defs
from xlib import xhttp_1_1_0 as xhttp

### Temporarily here, but belongs somewhere entirely different
def change_view(client,name):
	msg = {
		"event": "page-change",
		"page": name,
		"in_battle": name == "battle"
	}
	xhttp.send_json(client,200,msg)
###

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
		except Misc.error.Auth:
			xhttp.send_redirect(client,303,"login.html")
		except Misc.error.Char:
			change_view(client,"characters")
		except Misc.error.Page:
			change_view(client,"nav")
		except Misc.error.Battle:
			change_view(client,"battle")
		except Misc.error.User as e:
			xhttp.send_str(client,400,str(e))
		except Misc.error.Fine:
			return
		except Exception:
			Misc.io.clear_writes()
			error_txt = traceback.format_exc()
			Misc.log.log("error",error_txt)
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
		xhttp.serve_files(req,config)

def main():
	init_game()
	print("Saving enabled.")
	Misc.io.init()
	init_net()
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
	Misc.tick.init()
	print("Loading done.")
	Analysis.info.display()
	
	#Secondary tasks
	Analysis.itemcount.run()
def init_net():
	conf = Config.get("server")
	http_port = conf.get("http_port")
	https_port = conf.get("https_port")
	interactive = Config.get("server").get("interactive", True)
	if https_port is not None:
		ssl_keys = (".ssh/cert.pem",".ssh/key.pem")
		promise = xhttp.serve_forever(("",https_port),handler,(),ssl_keys=ssl_keys,new_thread=interactive,redirect_from=http_port)
	else:
		promise = xhttp.serve_forever(("",http_port),handler,(),new_thread=interactive)
	xhttp.await_startup(promise)
	print("Server successfully started.")

main()
