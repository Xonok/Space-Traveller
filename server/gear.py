types = {
	"mining_laser": {
		"type": "gun",
		"name": "Mining Laser",
		"desc": "Allows mining of ore from asteroids.",
		"size": 5,
		"price": 5000
	},
	"mini_smelter": {
		"name": "Mini Smelter",
		"desc": "Converts 6 ore into 2 metals per use.",
		"size": 20,
		"price": 25000
	},
	"mini_brewery": {
		"name": "Mini Brewery",
		"desc": "Converts 4 gas to 2 liquor per use.",
		"size": 10,
		"price": 12000
	},
	"station_kit": {
		"name": "Station Kit",
		"desc": "Used for building your very own space station.",
		"size": 40,
		"price": 50000
	},
	"station_expander": {
		"name": "Station Expander",
		"desc": "A section for increasing station capacity by 100.",
		"size": 10,
		"price": 10000,
		"space_max_station": 100
	}
}
def type(name):
	if not name in types or "type" not in types[name]:
		return ""
	return types[name]["type"]
def equipped(gtype,items):
	current = 0
	for item,amount in items.items():
		if type(item) == gtype:
			current += amount
	return current