from server import defs

def init():
	for sys_name,sys_data in defs.objmaps.items():
		for x,col in sys_data["tiles"].items():
			for y,tile in col.items():
				basetiles = defs.systems[sys_name]["tiles"]
				if x not in basetiles or y not in basetiles[x]:
					gathering.update_resources(sys_name,x,y)
					print("Illegal tile:",sys_name,x,y,tile)