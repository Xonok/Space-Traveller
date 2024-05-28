from server import defs

def get_all_images():
	items = {}
	ships = {}
	for name,data in defs.items.items():
		items[name] = data["img"]
	for name,data in defs.ship_types.items():
		ships[name] = data["img"]
	result = {
		"items": items,
		"ships": ships
	}
	return result