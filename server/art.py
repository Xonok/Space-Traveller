from server import defs

def get_all_images():
	items = {}
	ships = {}
	quests = {}
	for name,data in defs.items.items():
		items[name] = data["img"]
	for name,data in defs.ship_types.items():
		ships[name] = data["img"]
	for name,data in defs.quests.items():
		quests[name] = []
		quests[name].append(data["icon"])
		for outcome in data["outcomes"]:
			if "end_img" in outcome:
				quests[name].append(outcome["end_img"])
	result = {
		"items": items,
		"ships": ships,
		"quests": quests
	}
	return result