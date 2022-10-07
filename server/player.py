from . import io

data = io.read("players.data")

def add_item(pdata,name,amount):
	inv = pdata["items"]
	if name not in inv:
		inv[name] = 0
	amount = min(pdata["space_available"],amount)
	inv[name] += amount
	if inv[name] == 0:
		del inv[name]
	pdata["space_available"] -= amount
def remove_item(pdata,name,amount):
	inv = pdata["items"]
	if name not in inv:
		return 0
	amount = min(inv[name],amount)
	inv[name] -= amount
	if inv[name] == 0:
		del inv[name]
	pdata["space_available"] += amount
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
	return data[user]