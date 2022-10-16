import os,time
from . import io,grid,map,items,player,factory

#in seconds
time_per_tick = 300

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
		size2 = items.size(item)
		space_used += amount*size2
	for item,amount in station["gear"].items():
		size2 = items.size(item)
		space_used += amount*size2
	station["space"] = station["space_max"] - space_used
stations = {}
for system in map.get_all():
	stations[system] = io.read(os.path.join("station",system+".json"),grid.Grid)
	for station in stations[system].get_all():
		if "items" not in station:
			station["items"] = {}
		station["items"] = SItems(system=system,**station["items"])
		if "gear" not in station:
			station["gear"] = {}
		station["gear"] = SItems(system=system,**station["gear"])
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
		"items": SItems(system=system),
		"gear": SItems(system=system),
		"space_max": 100
	}
	stations[system].set(x,y,table)
	get_space(table)
	write(system)
def transfer(username,pdata,data,tile_station):
	take = data["take"]
	give = data["give"]
	pitems = items.pitems[username]
	sitems = tile_station["items"]
	for item,amount in give.items():
		space = tile_station["space"]
		size = items.size(item)
		limit = int(space/size)
		amount = min(amount,limit,pitems.get(item))
		pitems.add(item,-amount)
		sitems.add(item,amount)
		pdata["space_available"] += amount*size
		tile_station["space"] -= amount*size
	for item,amount in take.items():
		space = pdata["space_available"]
		size = items.size(item)
		limit = int(space/size)
		amount = min(amount,limit,sitems.get(item))
		pitems.add(item,amount)
		sitems.add(item,-amount)
		pdata["space_available"] -= amount*size
		tile_station["space"] += amount*size
	player.write()
def can_tick(station):
	if "timestamp" in station:
		now = time.time()
		prev = station["timestamp"]
		delta = now-prev
		if delta < time_per_tick:
			return False
		else:
			return True
	else:
		return True
def produce(station):
	stock = station["items"]
	for item,amount in station["gear"].items():
		if item not in factory.machines:
			continue
		machine = factory.machines[item]
		func = machine["func"]
		input = machine["input"]
		output = machine["output"]
		for i in range(amount):
			func(stock,input,output)
def tick(station):
	if "timestamp" in station:
		if can_tick(station):
			station["timestamp"] += time_per_tick
		else:
			now = time.time()
			prev = station["timestamp"]
			delta = now-prev
			print("Can't tick again yet. Wait "+str(int(time_per_tick-delta))+" seconds.")
			return
	else:
		print("First timestamp for station: "+station["system"]+":"+str(station["x"])+","+str(station["y"]))
		station["timestamp"] = time.time()
	produce(station)
	get_space(station)
	write(station["system"])
