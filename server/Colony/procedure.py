from server import Entity,error,Item
#How to start a colony?
#*Pick a parent entity(structure/ship)
#*Fail if parent already has a colony.
#*Create default state of colony.
#*Apply equipment effects.
def start_colony(parent_name):
	parent = Entity.get(parent_name)
	if not parent: raise error.User("There is no ship or structure called "+parent_name)
	if parent.get("colony"): raise error.User("This ship or structure already has a colony.")
	colony = data.Colony()
	colony["name"] = parent_name+","+"colony"
	colony["parent"] = parent_name
	colony["pop"] = data.default_pop()
	colony["industries"] = []
	colony["props"] = {}
	apply_equipment(colony)
	parent["colony"] = colony["name"]
	parent.save()
	colony.save()
def apply_equipment(colony):
	parent = Entity.get(colony["parent"])
	pop = colony.get("pop")
	pop_details = data.default_pop()
	for item,amount in parent.get_gear().items():
		idata = Item.data(item)
		props = idata.get("props",{})
		for name in pop_details.keys():
			pop_details[name]["min"] += props.get("pop_min",0)
			pop_details[name]["max"] += props.get("pop_max",0)
	for name,data in pop_details.items():
		pop[name]["min"] = data["min"]
		pop[name]["max"] = data["max"]
		pop[name]["current"] = data.bound(pop[name]["current"],data["min"],data["max"])

#Notes
workers = ["food","water","energy"],["medicine"] #primary production
industry = ["energy","ore","metals"],["microchips","robots"] #secondary production
wealth = ["gas","gems"],["chemicals","plastics"] #tax income
prestige = ["liquor"],["exotic_matter"] #migration
science = ["scrap","optics"],["phase_dust"] #archaeology
biotech = ["jello","bioframe"],["living_armor"] #decreases pop inputs
#Max one industry per pop property(workers,industry,wealth,etc...)

##TODO
#Update max_pop,min_pop to pop_max,pop_min in json
#Redo industries
