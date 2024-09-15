from server import defs,Item,config
import os

def init():
	delete_ship_files()
	starters()
	inventory()
	ships()
	do_init()
def delete_ship_files():
	if not os.path.isdir(os.path.join("data","ships")): return
	files = os.listdir(os.path.join("data","ships"))
	for f in files:
		f_initial = f
		f = f.replace(".json","")
		if f not in defs.ships:
			path = os.path.join("data","ships",f_initial)
			if config.config["saving"]:
				print("Deleting unused ship file:",path)
				os.remove(path)
			else:
				print("Want to delete unused ship file, but saving is off:",path)
def starters():
	for name,data in defs.starters.items():
		for entry in data["ships"]:
			for name2,data2 in entry.items():
				ship_type = defs.ship_types[name2]
				data2["img"] = ship_type["img"]
def inventory():
	for entry in defs.ships.values():
		cdata = defs.characters[entry["owner"]]
		to_unequip = {}
		for item,amount in entry["gear"].items():
			equipable = Item.query.equipable(item)
			if not equipable:
				to_unequip[item] = amount
		for item,amount in to_unequip.items():
			entry["gear"].add(item,-amount)
			cdata["items"].add(item,amount)
		entry.get_room()
def ships():
	for name,pship in defs.ships.items():
		pos = pship["pos"]
		x = pos["x"]
		y = pos["y"]
		system = pos["system"]
		tile = defs.systems[system]["tiles"].get(x,y)
		if not len(tile):
			pship["props"]["dead"] = True
def do_init():
	for pship in defs.ships.values():
		pship.init()