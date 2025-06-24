import time
from . import api
from server import defs,io

class Channel(dict):
	def __init__(self,**kwargs):
		#consists of 2 parts:
		#1: metadata(dict,json)
		#2: messages(list,csv)
		#reading the metadata automatically reads messages too.
		super().__init__()
		self.update(kwargs)
		self.messages = []
		if self["idx"] != -1:
			self.load_csv()
	def load_csv(self):
		self.messages = io.read_csv("data","channels",self["id"])
	def add_msg(self,user,char,txt):
		self["idx"] += 1
		idx = self["idx"]
		now = time.time()
		data = (idx,now,user,char,txt)
		self.messages.append(data)
		#if csv is appended continually, perhaps there is no need for a method that writes n lines?
		io.csv_append("channels",self["id"],data)
		self.save()
		return data
	def get_msg(self,idx):
		result = []
		for i in range(idx,self["idx"]):
			result.append(self.messages[i+1])
		return result
	def save(self):
		io.write2("channels",self["id"],self)
def init():
	print("Initializing chat channels.")
	if "all" not in defs.channels:
		create("all","All")
	if "trade" not in defs.channels:
		create("trade","Trade")
def create(id,name):
	print("Added channel: "+name)
	channel = Channel(id=id,name=name,idx=-1)
	defs.channels[id] = channel
	return channel
def get_channels(client,server):
	data = {
		"event": "channels-receive",
		"data": list(defs.channels.keys())
	}
	client.send_msg(data)
def get_messages(client,server,channel=str,idx=int):
	if channel not in defs.channels:
		print(channel)
		client.send_error("No channel called "+channel)
		return
	data = {
		"event": "msg-receive-multi",
		"channel": channel,
		"idx": defs.channels[channel]["idx"],
		"data": defs.channels[channel].get_msg(idx)
	}
	client.send_msg(data)
def validate_txt(txt,client):
	max_length = 300
	if not txt:
		client.send_error("Message empty.")
		return False
	if len(txt) > max_length:
		client.send_error("Message too long. Max: 300 characters.")
		return False
	forbidden = "<>&"
	for char in txt:
		if not char.isprintable():
			client.send_error("Unprintable character: "+char)
		if char in forbidden:
			client.send_error("Forbidden character: "+char)
			return False
	return True
def send_message(client,server,channel=str,txt=str):
	if channel not in defs.channels:
		client.send_error("No channel called "+channel)
		return
	txt = txt.strip()
	if not validate_txt(txt,client):
		return
	char = defs.users[server.uname]["active_character"]
	msg_data = defs.channels[channel].add_msg(server.uname,char,txt)
	data = {
		"event": "msg-receive",
		"channel": channel,
		"idx": defs.channels[channel]["idx"],
		"data": msg_data
	}
	for c in api.clients:
		client.send_msg(data)
api.register_command("get-channels",get_channels)
api.register_command("get-messages",get_messages)
api.register_command("send-message",send_message)

from server import defs