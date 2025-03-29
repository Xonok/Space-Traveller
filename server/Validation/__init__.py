from . import items,stars,predefs,prices

def run():
	items.init()
	predefs.init()
	prices.init()
	validate()


#TODO: fix this mess
from server import defs,map,ship
def validate():
	item_data()
	factories()
	objects() #wormholes
	weapons()
	blueprints()
	stars.validate()
checked_item_categories = []
def item_data():
	for item,data in defs.items.items():
		if "type" not in data: print("Item",item,"has no type.")
		if not data["desc"]: print("Item",item,"has no description.")
		if data.get("type") in ["common","produced","rare","artifact","blueprint"]: continue
		if "tech" not in data: print("Item",item,"has no tech level.")
		if item in defs.ship_types: print("Item and ship_type are identical: "+item)
		#print(item,data)
def factories():
	for name,data in defs.machines.items():
		if name not in defs.items:
			print("Factory entry for missing item: "+name)
	for name,data in defs.items.items():
		if data.get("type") in ["factory","farm"]:
			if name not in defs.machines:
				print("Missing factory entry for item: "+name)
def objects():
	for name,data in defs.objects.items():
		reqs = data.get("reqs",{})
		for key,value in reqs.items():
			if key == "quests_completed":
				if type(value) != int:
					raise Exception("Wrong type for wormhole req: "+type(value).__name__)
			else:
				raise Exception("Unknown requirement for passing through wormhole: "+key)
def weapons():
	for name,data in defs.weapons.items():
		if data["type"] == "drone":
			if "ship_predef" not in data:
				raise Exception("The drone(weapon) "+name+" needs to have a ship_predef.")
		if "ship_predef" in data and data["ship_predef"] not in defs.premade_ships:
			print("The drone(weapon) "+name+" has a ship predef that matches no premade ship: "+data["ship_predef"])
def blueprints():
	for name,data in defs.blueprints.items():
		item_name = name.removeprefix("bp_")
		if item_name not in data["outputs"]:
			print("Blueprint name and item produced don't match in blueprint: "+name+", expected output: "+item_name)