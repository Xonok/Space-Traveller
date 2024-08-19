from server import defs
import os

def init():
	delete_structure_files()
	check_premade()
	check_pos()
def delete_structure_files():
	if not os.path.isdir(os.path.join("data","structures")): return
	files = os.listdir(os.path.join("data","structures"))
	for f in files:
		original_f = f
		f = f.replace(".json","")
		if f not in defs.structures:
			path = os.path.join("data","structures",original_f)
			print("Deleting unused structure file:",path)
			os.remove(path)
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
