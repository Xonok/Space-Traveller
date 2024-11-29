import time,json
import websocket #locally available
from server import error


def validate_msg(msg):
	pass
def do_GET(self):
	ws.add_client(self)
def recv_handler(self,client,msg):
	try:
		data = json.loads(msg)
		if "command" not in data:
			raise error.User("No command in message."+msg)
		# if data["command"] not in commands:
			# raise error.User("Unknown command: "+data["command"])
		# commands[data["command"]](self,client,data)
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
	print("dropped client",client)
ws = websocket.Handler(recv_handler,drop_handler)