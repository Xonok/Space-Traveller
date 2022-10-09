import os,copy
from . import io,player,func

io.check_dir("pop")

pops = {}
pops["Ska"] = io.read(os.path.join("pop","Ska.json"))

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
	"Ska": "Terran"
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
	pop = pops[name]
	type = planet_type[name]
	check_pop(name)
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
def tick(name,market):
	check_pop(name)
	pop = pops[name]
	workers = pop["workers"]
	items = market["items"]
	for iname in pop("industries"):
		demand = {}
		total_demand = 0
		supply = {}
		total_supply = 0
		industry = check_industry(iname)
		for item,amount in industry["input"].items():
			func.add(demand,item,amount)
			total_demand += amount
		for item,amount in demand.items():
			available = 0
			if item in items.items():
				available = min(amount,items[item]["amount"])
			total_supply += available
		ratio = total_supply/total_demand
		for item,amount in industry["output"].items():
			items[item] += int(amount*ratio)
		
verify("Ska")
print(get_consumed("Ska"))
print(get_produced("Ska"))
print(get_drained("Ska"))
print(get_profit("Ska"))
