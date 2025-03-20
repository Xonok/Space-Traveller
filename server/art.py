from server import defs

def get_all_images():
	items = {}
	ships = {}
	wormholes = {}
	badges = {}
	glyphs = {}
	quests = {}
	for name,data in defs.items.items():
		items[name] = data["img"]
	for name,data in defs.ship_types.items():
		ships[name] = data["img"]
	for name,data in defs.wormhole_types.items():
		if "img" in data:
			wormholes[name] = data["img"]
	for name,data in defs.factions.items():
		if "badge" in data:
			badges[name] = data["badge"]
		if "glyph" in data:
			glyphs[name] = data["glyph"]
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
		"badges": badges,
		"glyphs": glyphs,
		"quests": quests
	}
	return result