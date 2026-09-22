import _thread
from . import ships,structures,map,spawners,images
from server import defs,reputation,Chat,Entity,Tick,AI

def step_init(func,msg):
	print(msg)
	func()
def run():
	step_init(Update.run,"Updating.")
	print("Finished updating.")
	step_init(Item.init,"Setting up derived item data.")
	step_init(ships.init,"Initializing ships.")
	step_init(structures.init,"Initializing structures.")
	step_init(map.init,"Initializing maps.")
	step_init(spawners.init,"Initializing spawners")
	step_init(reputation.init,"Initializing reputation.")
	step_init(Chat.init,"Initializing chat.")
	step_init(Entity.landmark.init,"Initializing landmarks.")
	step_init(images.init,"Initializing images.")
	
	print("Calculating room for characters.")
	for cdata in defs.characters.values():
		cdata.get_room()
	
	print("Ticking structures.")
	for tstruct in defs.structures.values():
		tstruct.tick()
	
	step_init(Skill.init,"Calculating levels.")
	step_init(spawner.init,"Initializing spawners.")
	print("Starting spawner loop.")
	_thread.start_new_thread(Tick.schedule_periodic,(5,spawner.tick))
	
	print("Starting AI loop.")
	_thread.start_new_thread(Tick.schedule_periodic,(5,AI.tick.run))
	
	print("Starting landmark loop.")
	_thread.start_new_thread(Tick.schedule_periodic,(5,Entity.landmark.loop))
	
	step_init(Validation.run,"Validating.")
	step_init(Item.obtainable.run,"Generating list of obtainable items.")

from server import Update,defs,spawner,Item,Skill,Validation