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
		"population": 5000,
		"industries": "farming",
		"drains": standard_drain
	}
}
planet_type = {
	"Ska": "Terran"
}

def write(name):
	io.write(os.path.join("pop",name+".json"),pops[name])

def verify(name):
	pop = pops[name]
	if not name in planet_type:
		raise Exception("Population "+name+" does not have a type.")
	type = planet_type[name]
	if not type in planet_types:
		raise Exception("Planet type"+type+" does not exist.")
	table = copy.deepcopy(planet_types[type])
	changed = False
	for key,value in table.items():
		if not key in pop:
			pop[key] = value
			changed = True
	if changed:
		write(name)

verify("Ska")
