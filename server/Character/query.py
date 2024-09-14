from server import defs

def get_tile_characters(tile):
	chars = {}
	if "ships" in tile:
		for cname in tile["ships"].keys():
			cdata = defs.characters[cname]
			room = cdata["stats"]["room"]
			chars[cname] = {
				"name": cdata["name"],
				"stats": {
					"room": {
						"current": room["current"],
						"max": room["max"]
					}
				}
			}
	return chars
