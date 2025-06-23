from . import ships,structures,map,spawners,item
from server import defs,reputation,Chat

def run():
	print("Updating.")
	Update.run()
	print("Finished updating.")
	item.station_kits()
	item.blueprints()
	ships.init()
	structures.init()
	map.init()
	spawners.init()
	reputation.init()
	Chat.init()
	
	itemdata.special2(defs.items,defs.weapons,defs.machines)
	itemdata.special2(defs.ship_types,defs.ship_types)
	itemdata.init()
	
	for cdata in defs.characters.values():
		cdata.get_room()
	
	print("Ticking structures.")
	for tstruct in defs.structures.values():
		tstruct.tick()
	
	print("Calculating levels.")
	Skill.init()
	
	print("Initializing spawners.")
	spawner.init()
	
	print("Validating.")
	Validation.run()
	
	print("Generating list of obtainable items.")
	Item.obtainable.run()

from server import Update,defs,spawner,itemdata,Item,Skill,Validation