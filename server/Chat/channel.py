import time
from . import api

channels = {
	"all": [],
	"trade": []
}
def get_channels(client,server):
	data = {
		"event": "channels-receive",
		"data": list(channels.keys())
	}
	client.send_msg(data)
def get_messages(client,server,channel=str,idx=int):
	if channel not in channels:
		client.send_error("No channel called "+channel)
		return
	data = {
		"event": "msg-receive-multi",
		"channel": channel,
		"data": channels[channel]
	}
	client.send_msg(data)
def send_message(client,server,channel=str,txt=str):
	if channel not in channels:
		client.send_error("No channel called "+channel)
		return
	now = time.time()
	idx = len(channels[channel])+1
	msg_data = {
		"txt": txt,
		"time": time.time(),
		"idx": idx,
		"sender": server.uname
	}
	channels[channel].append(msg_data)
	data = {
		"event": "msg-receive",
		"channel": channel,
		"data": msg_data
	}
	for c in api.clients:
		client.send_msg(data)
api.register_command("get-channels",get_channels)
api.register_command("get-messages",get_messages)
api.register_command("send-message",send_message)