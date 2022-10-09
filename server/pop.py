import os,copy,time
from . import io,player,func,market

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
	"gas": {
		"max": 2,
		"profit": 150
	}
}

#Note to future self - planets are NOT industrial.
#It's more interesting when players have to process goods instead of selling directly.
planet_types = {
	"Terran": {
		"workers": 5000,
		"industries": ["farming"],
		"drains": standard_drain
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
def get_consumed(name,table={}):
	check_pop(name)
	pop = pops[name]
	workers = pop["workers"]
	for iname in pop["industries"]:
		check_industry(iname)
		industry = industries[iname]
		for item,amount in industry["input"].items():
			func.add(table,item,int(amount*workers/1000))
	return table
def get_drained(name,table={}):
	check_pop(name)
	pop = pops[name]
	workers = pop["workers"]
	for item,data in pop["drains"].items():
		func.add(table,item,int(data["max"]*workers/1000))
	return table
def get_produced(name,table={}):
	check_pop(name)
	pop = pops[name]
	workers = pop["workers"]
	for iname in pop["industries"]:
		industry = check_industry(iname)
		for item,amount in industry["output"].items():
			func.add(table,item,int(amount*workers/1000))
	return table
def get_profit(name,table={}):
	check_pop(name)
	pop = pops[name]
	workers = pop["workers"]
	for item,data in pop["drains"].items():
		func.add(table,"credits",int(data["profit"]*workers/1000))
	return table
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
	workers = pop["workers"]/1000
	items = tile_market["items"]
	for iname in pop["industries"]:
		demand = {}
		total_demand = 0
		supply = {}
		total_supply = 0
		industry = check_industry(iname)
		for item,amount in industry["input"].items():
			func.add(demand,item,int(amount*workers))
			total_demand += int(amount*workers)
		for item,amount in demand.items():
			available = 0
			if item in items:
				available = min(amount,items[item])
			func.add(supply,item,available)
			total_supply += available
		ratio = total_supply/total_demand
		for item,amount in industry["output"].items():
			func.add(items,item,int(workers*amount*ratio))
		for item,amount in industry["input"].items():
			func.remove(items,item,int(workers*amount*ratio))
	write(name)
	market.write(tile_market["system"])
		
verify("Skara")
print(get_consumed("Skara"))
print(get_produced("Skara"))
print(get_drained("Skara"))
print(get_profit("Skara"))
