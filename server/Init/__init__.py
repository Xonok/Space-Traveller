import _thread
from . import ships,structures,map,spawners,item,images
from server import defs,reputation,Chat,Entity,Tick

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
	Entity.landmark.init()
	
	itemdata.special2(defs.items,defs.weapons,defs.machines)
	itemdata.special2(defs.ship_types,defs.ship_types)
	itemdata.link_data()
	itemdata.init()
	
	images.init()
	
	for cdata in defs.characters.values():
		cdata.get_room()
	
	print("Ticking structures.")
	for tstruct in defs.structures.values():
		tstruct.tick()
	
	print("Calculating levels.")
	Skill.init()
	
	print("Initializing spawners.")
	spawner.init()
	_thread.start_new_thread(Tick.schedule_periodic,(5,spawner.tick))
	
	print("Validating.")
	Validation.run()
	
	print("Generating list of obtainable items.")
	Item.obtainable.run()

from server import Update,defs,spawner,itemdata,Item,Skill,Validation