from . import io

data = io.read("players.data")

def add_item(inv,name,amount):
	if name not in inv:
		inv[name] = 0
	inv[name] += amount
	if inv[name] == 0:
		del inv[name]
def remove_item(inv,name,amount):
	if name not in inv:
		return 0
	amount = min(inv[name],amount)
	inv[name] -= amount
	if inv[name] == 0:
		del inv[name]
	return amount
def write():
	io.write("players.data",data)
def check(user):
	if user not in data:
		data[user] = {
			"position":(1,0),
			"system":"Ska",
			"credits":10000,
			"items":{},
			"space_available":50,
			"space_total":50,
			"img":"img/clipart2908532.png",
			"rotation":0
		}