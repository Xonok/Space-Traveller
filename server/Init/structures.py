from server import defs,config
import os

def init():
	check_premade()
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
def do_init():
	for data in defs.structures.values():
		data.init()