import os
from . import io,items,ship

data = io.read("","players")
def check(user):
	default = {
		"position":(1,0),
		"system":"Ska",
		"credits":10000,
		"ship": "harvester",
		"rotation":0
	}
	if user not in data:
		data[user] = default
	for key,value in default.items():
		if key not in data[user]:
			data[user][key] = value
	pship = ship.types[data[user]["ship"]]
	data[user]["space_total"] = pship["space"]
	data[user]["img"] = os.path.join("img",pship["img"])
	data[user]["space_available"] = data[user]["space_total"]-items.space_used(user)
	return data[user]
for name in data.keys():
	check(name)
def write():
	io.write("","players",data)