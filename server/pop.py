import os,copy
from . import io,player

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

def table_add(table,item,amount):
	if not item in table:
		table[item] = 0
	table[item] += amount
def get_consumed(name):
	check_pop(name)
	pop = pops[name]
	table = {}
	workers = pop["workers"]
	for iname in pop["industries"]:
		check_industry(iname)
		industry = industries[iname]
		for input,amount in industry["input"].items():
			table_add(table,input,int(amount*workers/1000))
	for input,data in pop["drains"].items():
		table_add(table,input,int(data["max"]*workers/1000))
	return table
def get_produced(name):
	check_pop(name)
	pop = pops[name]
	table = {}
	workers = pop["workers"]
	for iname in pop["industries"]:
		check_industry(iname)
		industry = industries[iname]
		for input,amount in industry["output"].items():
			table_add(table,input,int(amount*workers/1000))
	for input,data in pop["drains"].items():
		table_add(table,"credits",int(data["profit"]*workers/1000))
	return table
verify("Ska")
print(get_consumed("Ska"))
print(get_produced("Ska"))
