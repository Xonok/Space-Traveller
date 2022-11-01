import os,time
from . import io,grid,map,items,player,factory,ship,defs

#in seconds
time_per_tick = 60*60 # 1 hour per tick.

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
