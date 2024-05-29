from server import Update,validation,defs,spawner,itemdata,Item
from . import ships,structures,map,spawners,items

def run():
	ships.init()
	structures.init()
	map.init()
	spawners.init()
	items.init()
	print("Updating.")
	Update.run()
	print("Finished updating.")
	
	itemdata.special2(defs.items,defs.weapons,defs.machines)
	itemdata.special2(defs.ship_types,defs.ship_types)
	itemdata.init()
	
	print("Ticking structures.")
	for tstruct in defs.structures.values():
		tstruct.tick()
	
	print("Initializing spawners.")
	spawner.init()
	
	print("Validating.")
	validation.validate()
	
	print("Generating list of obtainable items.")
	Item.obtainable.run()