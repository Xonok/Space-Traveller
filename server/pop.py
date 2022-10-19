import os,copy,time
from . import io,player,market,items,factory,defs

#in seconds
time_per_tick = 60*60 # 1 hour per tick.

pops = {}
pops["Skara"] = io.read("pop","Skara")

def write(name):
	io.write("pop",name,pops[name])

def verify(name):
	pop = pops[name]
	table = {
		"name": name,
		"workers": 5000
	}
	changed = False
	for key,value in table.items():
		if not key in pop:
			pop[key] = value
			changed = True
def can_tick(name):
	pop = pops[name]
	if "timestamp" in pop:
		now = time.time()
		prev = pop["timestamp"]
		delta = now-prev
		if delta < time_per_tick:
			return False
		else:
			return True
	else:
		return True
def produce(name,tile_market):
	workers = pops[name]["workers"]/1000
	stock = tile_market["items"]
	for iname in defs.planets[name]["industries"]:
		factory.use_industry(iname,stock,pops[name]["workers"])
def consume(name,tile_market):
	workers = pops[name]["workers"]/1000
	stock = tile_market["items"]
	drain = factory.standard_drain
	func = drain["func"]
	input = factory.tmult(drain["input"],workers)
	credits = func(stock,input)
	if credits:
		tile_market["credits"] += credits
def tick(name,tile_market):
	pop = pops[name]
	if "timestamp" in pop:
		if can_tick(name):
			pop["timestamp"] += time_per_tick
		else:
			now = time.time()
			prev = pop["timestamp"]
			delta = now-prev
			print("Can't tick again yet. Wait "+str(int(time_per_tick-delta))+" seconds.")
			return
	else:
		print("First timestamp for pop: "+name)
		pop["timestamp"] = time.time()
	produce(name,tile_market)
	consume(name,tile_market)
	write(name)
	market.write(tile_market["system"])
		
verify("Skara")
