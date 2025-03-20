from server import defs

def get_all_images():
	items = {}
	ships = {}
	wormholes = {}
	quests = {}
	for name,data in defs.items.items():
		items[name] = data["img"]
	for name,data in defs.ship_types.items():
		ships[name] = data["img"]
	for name,data in defs.wormhole_types.items():
		if "img" in data:
			wormholes[name] = data["img"]
	for name,data in defs.quests.items():
		quests[name] = []
		quests[name].append(data["icon"])
		for outcome in data["outcomes"]:
			if "end_img" in outcome:
				quests[name].append(outcome["end_img"])
	result = {
		"items": items,
		"ships": ships,
		"wormholes": wormholes,
		"quests": quests
	}
	return result