from server import Update,validation,defs,info,spawner,itemdata,Item
from . import ships,structures

def run():
	ships.init()
	structures.init()
	Update.run()
	
	itemdata.special2(defs.items,defs.weapons,defs.machines)
	itemdata.special2(defs.ship_types,defs.ship_types)
	itemdata.init()
	
	validation.validate()
	
	for tstruct in defs.structures.values():
		tstruct.tick()
	
	spawner.init()
	
	Item.obtainable.run()
	
	info.display()