from server import Update,validation,defs,info,spawner,itemdata

def run():
	Update.run()
	
	itemdata.special2(defs.items,defs.weapons,defs.machines)
	itemdata.special2(defs.ship_types,defs.ship_types)
	validation.validate()
	
	spawner.init()
	
	info.display()