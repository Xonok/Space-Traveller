import json
import websocket #locally available
from server import error,defs

commands = {}
clients = []

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
		data = {
			"event": "auth-done"
		}
		client.send_msg(data)
	except error.Auth:
		data = {
			"event": "auth-fail",
			"data": {
				"reason": "key-invalid",
				"txt": "Failed to log in: invalid or old key."
			}
		}
		client.send_msg(data)
	except Exception:
		client.send_error("Server error.")
register_command("auth",do_auth)
def connect(server):
	ws = websocket.Handler(server,recv_handler)
	clients.append(ws)
	print("append")
	ws.start()
	print("remove")
	clients.remove(ws)
	print(len(clients))
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
	except Exception as e:
		client.send_error("Server error.")
		raise