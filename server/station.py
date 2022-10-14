import os
from . import io,grid,map,items,player

class SItems(items.Items):
	def __init__(self,default=0,system="",**kwargs):
		super().__init__(default,**kwargs)
		self.system = system
	def add(self,key,value):
		super().add(key,value)
		write(self.system)
	def remove(self,key):
		super().remove(key)
		write(self.system)
def get_space(station):
	space_used = 0
	for item,amount in station["items"].items():
		space_used += amount
	station["space"] = station["space_max"] - space_used
stations = {}
for system in map.get_all():
	stations[system] = io.read(os.path.join("station",system+".json"),grid.Grid)
	for station in stations[system].get_all():
		if "items" not in station:
			station["items"] = {}
		station["items"] = SItems(system=system,**station["items"])
		if "space_max" not in station:
			station["space_max"] = 100
		get_space(station)

def write(system):
	io.write(os.path.join("station",system+".json"),stations[system])
def get(system,x,y):
	return stations[system].get(x,y)
def add(system,x,y,img,owner):
	if len(stations[system].get(x,y)):
		return
	table = {
		"owner": owner,
		"image": img,
		"system": system,
		"x": x,
		"y": y,
		"items": SItems(system=system)
	}
	stations[system].set(x,y,table)
	write(system)
def transfer(username,pdata,data,tile_station):
	take = data["take"]
	give = data["give"]
	pitems = items.pitems[username]
	sitems = tile_station["items"]
	for item,amount in give.items():
		amount = min(amount,tile_station["space"],pitems.get(item))
		pitems.add(item,-amount)
		sitems.add(item,amount)
		pdata["space_available"] += amount
		tile_station["space"] -= amount
	for item,amount in take.items():
		amount = min(amount,pdata["space_available"],sitems.get(item))
		pitems.add(item,amount)
		sitems.add(item,-amount)
		pdata["space_available"] -= amount
		tile_station["space"] += amount
	player.write()
