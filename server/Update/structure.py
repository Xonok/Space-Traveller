def pop(entity):
	if "pop" in entity: return
	table = {}
	for name in ["workers","industry","wealth","prestige","science"]:
		table[name] = details()
	if entity["population"]:
		table["workers"]["current"] = entity["population"]["workers"]
	entity["pop"] = table
def details():
	return {
		"current": 1000,
		"min": 100,
		"max": 0,
		"change": 0
	}
