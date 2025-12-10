from server import defs,config
import os

def init():
	check_premade()
	check_pos()
	do_init()
def check_premade():
	for system,table in defs.objmaps.items():
		for x,column in table["tiles"].items():
			for y, data in column.items():
				if "structure" in data:
					name = data["structure"]
					if name in defs.predefined_structures:
						tstruct = defs.structures.get(name)
						predef = defs.predefined_structures[name]
						#???
def check_pos():
	for name,data in defs.structures.items():
		system = data["pos"]["system"]
		if system not in defs.objmaps: continue
		otiles = defs.objmaps[system]["tiles"]
		otile = otiles.get(data["pos"]["x"],data["pos"]["y"])
		tile_struct = otile.get("structure")
		if not tile_struct or name != tile_struct: print("Structure "+name+" should be at "+str(data["pos"])+" but isn't.")
def do_init():
	for data in defs.structures.values():
		data.init()