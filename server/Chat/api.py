import json
import websocket #locally available
from server import error,defs
from urllib.parse import urlparse,parse_qs

commands = {}
clients = {}

#TODO: validate command params before passing them to handler
def register_command(name,handler):
	if name in commands:
		raise Exception("Trying to register same command twice.")
	commands[name] = handler
def do_auth(client,server,key=str):
	try:
		uname = server.auth(key)
		udata = defs.users.get(uname)
		server.uname = uname
		server.cname = udata["active_character"]
		server.system = defs.characters[server.cname].get_system()
		clients[server.cname] = client
		data = {
			"event": "auth-done"
		}
		client.send_msg(data)
	except error.Auth as e:
		data = {
			"event": "auth-fail",
			"data": {
				"reason": "key-invalid",
				"txt": "Failed to log in: invalid or old key."
			}
		}
		client.send_msg(data)
		print(e)
	except Exception as e:
		client.send_error("Server error.")
		print(e)
register_command("auth",do_auth)
def connect(server):
	ws = websocket.Handler(server,recv_handler)
	ws.handshake()
	url_parts = urlparse(server.path)
	key = parse_qs(url_parts.query)["key"][0]
	do_auth(ws,server,key)
	ws.start()
	del clients[server.cname]
def recv_handler(client,server,msg):
	try:
		data = json.loads(msg)
		if "command" not in data:
			raise error.User("No command in message."+msg)
		if data["command"] not in commands:
			raise error.User("Unknown command: "+data["command"])
		cmd_name = data["command"]
		cmd_data = commands[cmd_name]
		del data["command"]
		commands[cmd_name](client,server,**data)
	except error.User as e:
		client.send_error(str(e))
		print(e)
	except Exception as e:
		client.send_error("Server error.")
		raise