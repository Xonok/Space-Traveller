import os,copy,time
from . import io,player,market,goods,items,factory

io.check_dir("pop")

#in seconds
time_per_tick = 300

pops = {}
pops["Skara"] = io.read(os.path.join("pop","Skara.json"))

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
		now = time.time()
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
	stock = tile_market["items"]
	for iname in pop["industries"]:
		industry = factory.industries[iname]
		func = industry["func"]
		input = factory.tmult(industry["input"],workers)
		output = factory.tmult(industry["output"],workers)
		func(stock,input,output)
def consume(pop,tile_market):
	workers = pop["workers"]/1000
	stock = tile_market["items"]
	drain = factory.standard_drain
	func = drain["func"]
	input = factory.tmult(drain["input"],workers)
	credits = func(stock,input)
	if credits:
		tile_market["credits"] += credits
def tick(name,tile_market):
	check_pop(name)
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
	produce(pop,tile_market)
	consume(pop,tile_market)
	write(name)
	market.write(tile_market["system"])
		
verify("Skara")
