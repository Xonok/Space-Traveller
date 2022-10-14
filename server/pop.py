import os,copy,time
from . import io,player,market,goods,items

io.check_dir("pop")

#in seconds
time_per_tick = 300

pops = {}
pops["Skara"] = io.read(os.path.join("pop","Skara.json"))

industries = {
	"farming": {
		"input": {
			"energy": 7.5
		},
		"output":{
			"food": 3.5,
			"water": 4.5
		}
	}
}

standard_drain = {
	"gas": 2,
	"ore": 2,
	"metals": 0.5,
	"liquor": 1
}

#Note to future self - planets are NOT industrial.
#It's more interesting when players have to process goods instead of selling directly.
planet_types = {
	"Terran": {
		"workers": 5000,
		"industries": ["farming"]
	}
}
planet_type = {
	"Skara": "Terran"
}

def write(name):
	io.write(os.path.join("pop",name+".json"),pops[name])

def check_pop(name):
	if not name in planet_type:
		raise Exception("Population "+name+" does not have a type.")
	type = planet_type[name]
	if not type in planet_types:
		raise Exception("Planet type"+type+" does not exist.")
def check_industry(name):
	if not name in industries:
		raise Exception("There is no industry called "+name)
	return industries[name]
def verify(name):
	check_pop(name)
	pop = pops[name]
	type = planet_type[name]
	table = copy.deepcopy(planet_types[type])
	changed = False
	for key,value in table.items():
		if not key in pop:
			pop[key] = value
			changed = True
	if changed:
		write(name)
def can_tick(name):
	check_pop(name)
	pop = pops[name]
	if "timestamp" in pop:
		now = time.monotonic()
		prev = pop["timestamp"]
		delta = now-prev
		if delta < time_per_tick:
			return False
		else:
			return True
	else:
		return True
def produce(pop,tile_market):
	workers = pop["workers"]/1000
	tile_items = tile_market["items"]
	for iname in pop["industries"]:
		demand = items.Items()
		total_demand = 0
		supply = items.Items()
		total_supply = 0
		industry = check_industry(iname)
		for item,amount in industry["input"].items():
			demand.add(item,int(amount*workers))
			total_demand += int(amount*workers)
		for item,amount in demand.items():
			available = 0
			if item in tile_items:
				available = min(amount,tile_items.get(item))
			supply.add(item,available)
			total_supply += available
		ratio = total_supply/total_demand
		for item,amount in industry["output"].items():
			tile_items.add(item,int(workers*amount*ratio))
		for item,amount in industry["input"].items():
			tile_items.add(item,-int(workers*amount*ratio))
def consume(pop,tile_market):
	workers = pop["workers"]/1000
	tile_items = tile_market["items"]
	drained = items.Items()
	profit = 0
	for item,ratio in standard_drain.items():
		if item in tile_items:
			amount = min(round(workers*ratio),tile_items[item])
			drained[item] = amount
	for item,amount in drained.items():
		profit += amount*goods.default[item]
		tile_items.add(item,-amount)
	tile_market["credits"] += profit
def tick(name,tile_market):
	check_pop(name)
	pop = pops[name]
	if "timestamp" in pop:
		if can_tick(name):
			pop["timestamp"] += time_per_tick
		else:
			now = time.monotonic()
			prev = pop["timestamp"]
			delta = now-prev
			print("Can't tick again yet. Wait "+str(int(time_per_tick-delta))+" seconds.")
			return
	else:
		print("First timestamp for pop: "+name)
		pop["timestamp"] = time.monotonic()
	produce(pop,tile_market)
	consume(pop,tile_market)
	write(name)
	market.write(tile_market["system"])
		
verify("Skara")
