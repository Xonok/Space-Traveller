from server import defs,gathering

def init():
	to_update = []
	for sys_name,sys_data in defs.objmaps.items():
		for x,col in sys_data["tiles"].items():
			for y,tile in col.items():
				basetiles = defs.systems[sys_name]["tiles"]
				if x not in basetiles or y not in basetiles[x]:
					to_update.append((sys_name,x,y))
					print("Illegal tile:",sys_name,x,y,tile)
	for sys_name,x,y in to_update:
		gathering.update_resources(sys_name,x,y)