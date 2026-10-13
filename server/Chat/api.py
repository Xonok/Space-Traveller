import json
from server import error,defs,user
from urllib.parse import urlparse,parse_qs

commands = {}
clients = {}

#TODO: validate command params before passing them to handler
def register_command(name,handler):
	if name in commands:
		raise Exception("Trying to register same command twice.")
	commands[name] = handler
def do_auth(ctx,client,key=str):
	try:
		uname = user.check_key(key)
		udata = defs.users.get(uname)
		ctx["uname"] = uname
		ctx["cname"] = udata["active_character"]
		ctx["system"] = defs.characters[ctx["cname"]].get_system()
		clients[ctx["cname"]] = ctx
		data = {
			"event": "auth-done"
		}
		ctx["send_msg"](data)
	except error.Auth as e:
		data = {
			"event": "auth-fail",
			"data": {
				"reason": "key-invalid",
				"txt": "Failed to log in: invalid or old key."
			}
		}
		ctx["send_msg"](data)
		print(e)
	except Exception as e:
		ctx["send_error"]("Server error.")
		print(e)
		raise
register_command("auth",do_auth)
def on_message(client,ctx,msg):
	recv_handler(ctx,msg)
def on_open(client,ctx):
	target = ctx["req"]["target"]
	url_parts = urlparse(target)
	key = parse_qs(url_parts.query)["key"][0]
	def send_error(msg):
		data = {
			"event": "error",
			"txt": msg
		}
		ctx["send_msg"](data)
	def send_msg(msg):
		ctx["send_ws"](json.dumps(msg))
	ctx["send_error"] = send_error
	ctx["send_msg"] = send_msg
	do_auth(ctx,client,key)
def on_close(client,ctx):
	print("Dropped client",ctx.get("cname"))
	if clients.get(ctx.get("cname")) == ctx:
		del clients[ctx["cname"]]
def recv_handler(ctx,msg):
	try:
		data = json.loads(msg)
		if "command" not in data:
			raise error.User("No command in message."+msg)
		if data["command"] not in commands:
			raise error.User("Unknown command: "+data["command"])
		cmd_name = data["command"]
		cmd_data = commands[cmd_name]
		del data["command"]
		commands[cmd_name](ctx,**data)
	except error.User as e:
		ctx["send_error"](str(e))
		print(e)
	except Exception as e:
		ctx["send_error"]("Server error.")
def send_to_system(event,system,**kwargs):
	data = {
		"event": event,
		"data": kwargs
	}
	for cname,ctx in clients.items():
		if ctx["system"] == system:
			ctx["send_msg"](data)
def send_to_client(event,client,**kwargs):
	data = {
		"event": event,
		"data": kwargs
	}
	client["send_msg"](data)
def send_to_character(event,cname,**kwargs):
	if cname in clients:
		send_to_client(event,clients[cname],**kwargs)
def send_to_tile(event,system,x,y,**kwargs):
	pass
