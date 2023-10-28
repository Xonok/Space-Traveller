from server import Update,validation,defs,info,spawner,itemdata,Item
from . import ships

def run():
	Update.run()
	
	itemdata.special2(defs.items,defs.weapons,defs.machines)
	itemdata.special2(defs.ship_types,defs.ship_types)
	validation.validate()
	
	for tstruct in defs.structures.values():
		tstruct.tick()
		
	ships.init()
	
	spawner.init()
	
	Item.obtainable.run()
	
	info.display()