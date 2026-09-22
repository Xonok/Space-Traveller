import _thread
from . import ships,structures,map,spawners,images
from server import defs,reputation,Chat,Entity,Tick,AI

def step_init(func,msg):
	print(msg)
	func()
def run():
	#TODO: use do_init
	print("Updating.")
	Update.run()
	print("Finished updating.")
	print("Setting up derived item data.")
	Item.init()
	print("Initializing ships.")
	ships.init()
	print("Initializing structures.")
	structures.init()
	print("Initializing maps.")
	map.init()
	print("Initializing spawners")
	spawners.init()
	print("Initializing reputation.")
	reputation.init()
	print("Initializing chat.")
	Chat.init()
	print("Initializing landmarks.")
	Entity.landmark.init()
	
	print("Initializing images.")
	images.init()
	
	print("Calculating room for characters.")
	for cdata in defs.characters.values():
		cdata.get_room()
	
	print("Ticking structures.")
	for tstruct in defs.structures.values():
		tstruct.tick()
	
	print("Calculating levels.")
	Skill.init()
	
	print("Initializing spawners.")
	spawner.init()
	print("Starting spawner loop.")
	_thread.start_new_thread(Tick.schedule_periodic,(5,spawner.tick))
	
	print("Starting AI loop.")
	_thread.start_new_thread(Tick.schedule_periodic,(5,AI.tick.run))
	
	print("Validating.")
	Validation.run()
	
	print("Generating list of obtainable items.")
	Item.obtainable.run()

from server import Update,defs,spawner,Item,Skill,Validation