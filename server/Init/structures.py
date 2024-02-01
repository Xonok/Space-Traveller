from server import defs
import os

def init():
	delete_structure_files()
	check_premade()
def delete_structure_files():
	files = os.listdir(os.path.join("data","structures"))
	for f in files:
		f = f.replace(".json","")
		if f not in defs.structures:
			path = os.path.join("data","structures",f)+".json"
			print("Deleting unused structure file:",path)
			os.remove(path)
def check_premade():
	for system,table in defs.objmaps.items():
		for x,column in table["tiles"].items():
			for y, data in column.items():
				if "structure" in data:
					name = data["structure"]
					if name in defs.premade_structures:
						tstruct = defs.structures.get(name)
						predef = defs.premade_structures[name]
			