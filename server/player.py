from . import io,items

data = io.read("players.data")

def write():
	io.write("players.data",data)
def check(user):
	default = {
		"position":(1,0),
		"system":"Ska",
		"credits":10000,
		"space_available":50,
		"space_total":50,
		"img":"img/clipart2908532.png",
		"rotation":0
	}
	if user not in data:
		data[user] = default
	for key,value in default.items():
		if key not in data[user]:
			data[user][key] = value
	data[user]["space_available"] = data[user]["space_total"]-items.space_used(user)
	return data[user]