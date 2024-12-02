import time,json
import websocket #locally available
from server import error

commands = {}
messages = []
clients = []
#TODO: validate command params before passing them to handler
def register_command(name,handler):
	if name in commands:
		raise Exception("Trying to register same command twice.")
	commands[name] = handler
def get_messages(self,client,idx=int):
	data = {
		"event": "msg-receive-multi",
		"data": messages
	}
	ws.send_msg(client,data)
def send_message(self,client,txt=str):
	now = time.time()
	idx = len(messages)+1
	msg_data = {
		"txt": txt,
		"time": time.time(),
		"idx": idx,
		"sender": "???"
	}
	messages.append(msg_data)
	data = {
		"event": "msg-receive",
		"data": msg_data
	}
	for c in clients:
		ws.send_msg(client,data)
register_command("get-messages",get_messages)
register_command("send-message",send_message)
def do_GET(client):
	clients.append(client)
	ws.add_client(client)
def recv_handler(self,client,msg):
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
		commands[cmd_name](self,client,**data)
	except error.User as e:
		ws.send_error(client,str(e))
	except Exception as e:
		ws.send_error(client,"Server error.")
		raise
def drop_handler(self,client):
	# if not client.uname: return
	# if client.uname not in world_players[client.world]: return
	# if client not in world_players[client.world][client.uname]: return
	# world_players[client.world][client.uname].remove(client)
	clients.remove(client)
	print("dropped client",client)
ws = websocket.Handler(recv_handler,drop_handler)