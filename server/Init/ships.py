from server import defs
import os

def init():
	delete_ship_files()
	starters()
def delete_ship_files():
	files = os.listdir(os.path.join("server","data","ships"))
	for f in files:
		f = f.replace(".json","")
		if f not in defs.ships:
			path = os.path.join("server","data","ships",f+".json")
			print("Deleting unused ship file:",path)
			os.remove(path)
def starters():
	for name,data in defs.starters.items():
		for data2 in data["ships"]:
			for name in list(data2.keys()):
				ship_type = defs.ship_types[name]
				data2["img"] = ship_type["img"]