from server import Update,validation,defs,info,spawner,itemdata,Item
from . import ships

def run():
	ships.init()
	Update.run()
	
	itemdata.special2(defs.items,defs.weapons,defs.machines)
	itemdata.special2(defs.ship_types,defs.ship_types)
	validation.validate()
	
	for tstruct in defs.structures.values():
		tstruct.tick()
	
	spawner.init()
	
	Item.obtainable.run()
	
	info.display()