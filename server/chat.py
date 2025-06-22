import time,json
import websocket #locally available
from server import error,defs

commands = {}
messages = []
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
		data = {
			"event": "auth-fail",
			"data": {
				"reason": "error-server",
				"txt": "A server error has occurred."
			}
		}
		client.send_msg(data)
def get_messages(client,server,idx=int):
	data = {
		"event": "msg-receive-multi",
		"data": messages
	}
	client.send_msg(data)
def send_message(client,server,txt=str):
	now = time.time()
	idx = len(messages)+1
	msg_data = {
		"txt": txt,
		"time": time.time(),
		"idx": idx,
		"sender": server.uname
	}
	messages.append(msg_data)
	data = {
		"event": "msg-receive",
		"data": msg_data
	}
	for c in clients:
		client.send_msg(data)
register_command("auth",do_auth)
register_command("get-messages",get_messages)
register_command("send-message",send_message)
def do_GET(server):
	ws = websocket.Handler(server,recv_handler)
	clients.append(ws)
	ws.start()
	clients.remove(ws)
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
		# for key in data:
			# if key not in cmd_data:
				# raise error.User("Unnecessary parameter "+key+" for command "+cmd_name)
		# for key,val in cmd_data.items():
			# if type(data[key]) != val:
				# if type(val) == str:
					# param_type = val
				# else:
					# param_type = val.__name__
				# raise error.User("Parameter "+key+" for command "+cmd_name+" must be of type "+param_type)
		commands[cmd_name](client,server,**data)
	except error.User as e:
		client.send_error(str(e))
	except Exception as e:
		client.send_error("Server error.")
		raise