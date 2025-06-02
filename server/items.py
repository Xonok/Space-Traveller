class Items(dict):
	def __init__(self,default=0,**kwargs):
		super().__init__()
		self.default = default
		self.update(kwargs)
	def add(self,key,value):
		self[key] = self.get(key)+value
		if not self[key]:
			del self[key]
	def get(self,key):
		if key in self:
			return self[key]
		else:
			return self.default
	def remove(self,key):
		if key in self:
			del self[key]
do_check = False
class SaveItems(Items):
	def __init__(self,default=0,**kwargs):
		super().__init__(default,**kwargs)
		self.parent = None
	def __setattr__(self, key, value):
		super().__setattr__(key,value)
	def add(self,key,value):
		super().add(key,value)
		if do_check or "stats" in self.parent:
			isize = Item.query.size(key)
			self.parent["stats"]["room"]["current"] -= isize*value
		self.save()
	def remove(self,key):
		super().remove(key)
		self.save()
	def size(self):
		total = 0
		for key,value in self.items():
			total += size(key)*value
		return total
	def save(self):
		if not self.parent: raise Exception("Parent for SaveItems not set.")
		self.parent.save()
import copy
from . import ship,defs,factory,structure,map,Item,error,Skill,func
def size(item):
	if item in defs.items:
		return defs.items[item]["size"]
	if item in defs.ship_types:
		if "size_item" in defs.ship_types[item]:
			return defs.ship_types[item]["size_item"]
		else:
			return defs.ship_types[item]["size"]
def type(item):
	if item in defs.items:
		if "type" in defs.items[item]:
			return defs.items[item]["type"]
		return "other"
	if item in defs.ship_types:
		return "ship"
	raise Exception("Unknown kind of item: "+item)
def prop(item_name,prop_name):
	item_data = defs.items[item_name]
	if "props" not in item_data or prop_name not in item_data["props"]: return
	return item_data["props"][prop_name]
def drop(drop_items,cdata,pship):
	citems = cdata.get_items()
	pos = pship["pos"]
	objmap = map.otiles(pos["system"])
	objtile = objmap.get(pos["x"],pos["y"])
	for name,amount in drop_items.items():
		if amount < 0:
			raise error.User("Can't drop a negative amount of items.")
		if amount > citems.get(name):
			raise error.User("Can't drop more than you have.")
	if "items" not in objtile:
		objtile["items"] = {}
	for name,amount in drop_items.items():
		if not amount: continue
		if name not in objtile["items"]:
			objtile["items"][name] = 0
		objtile["items"][name] += amount
		citems.add(name,-amount)
	objmap.set(pos["x"],pos["y"],objtile)
	objmap.save()
	pship.save()
def use(self,cdata,used_item):
	pship = ship.get(cdata.ship())
	citems = cdata.get_items()
	pgear = pship.get_gear()
	psystem = pship.get_system()
	px,py = pship.get_coords()
	if used_item in defs.items:
		idata = defs.items[used_item]
	elif used_item in defs.ship_types:
		idata = defs.ship_types[used_item]
	props = idata.get("props",{})
	consumable = props.get("consumable",False)
	skill_factory = cdata["skills"].get("factory",0)
	if citems.get(used_item) or pgear.get(used_item):
		if used_item in defs.station_kits:
			structure.build_station(used_item,cdata,psystem,px,py)
		if used_item in defs.machines:
			idata = defs.items[used_item]
			if idata["tech"] > skill_factory:
				raise error.User("Can't use this factory. Factory skill "+str(idata["tech"])+" needed.")
			if "manual" in props:
				result = factory.use_machine(used_item,cdata,True)
			else:
				result = factory.ship_use_machine(pship,used_item)
			if result:
				noob_factor = 1
				if cdata["level"] < 10:
					noob_factor += (9-cdata["level"])/2
				level_factor = 1/(cdata["level"]+1)
				xp_amount = func.f2ir((10+idata["tech"]*2)*noob_factor*level_factor)
				if xp_amount > 0:
					Skill.gain_xp_flat(cdata,xp_amount)
					self.add_message("Factory used successfully. Gained "+str(xp_amount)+"xp, "+str(1000-cdata["xp"])+" until next level.")
				else:
					self.add_message("Factory used successfully.")
	if citems.get(used_item):
		if consumable:
			Item.consumable(used_item,citems,pship)
		if used_item in defs.ship_types and used_item in citems:
			owner = cdata["name"]
			new_ship = ship.new(used_item,owner)
			new_ship["pos"] = copy.deepcopy(pship["pos"])
			cdata["ships"].append(new_ship["name"])
			ship.add_character_ship(new_ship)
			map.add_ship(new_ship,new_ship["pos"]["system"],new_ship["pos"]["x"],new_ship["pos"]["y"])
			citems.add(used_item,-1)
	cdata.save()
def itemlist_data(ilist):
	data = {}
	for name in ilist:
		if name in defs.items:
			idata = defs.items[name]
			props = idata.get("props",{})
			itype = Item.query.type(name)
			category_usable = "use" in defs.item_categories.get(itype)
			usable = True if itype == "factory" or "consumable" in props else False
			data[name] = copy.deepcopy(defs.items[name])
		if name in defs.ship_types:
			category_usable = True
			data[name] = copy.deepcopy(defs.ship_types[name])
			data[name]["type"] = "ship"
		data[name]["usable"] = category_usable or usable
	return data
def structure_item_names(tstructure):
	names = []
	for name in tstructure["market"]["prices"].keys():
		names.append(name)
	for name in tstructure["market"]["change"].keys():
		names.append(name)
	for name in tstructure["items"].keys():
		names.append(name)
		if name in defs.items:
			idata = defs.items[name]
			props = idata.get("props",{})
			for k,v in props.items():
				if "mining_bonus_" in k:
					for name2 in v.keys():
						names.append(name2)
	for name in tstructure["gear"].keys():
		names.append(name)
		if name in defs.items:
			idata = defs.items[name]
			props = idata.get("props",{})
			for k,v in props.items():
				if "mining_bonus_" in k:
					for name2 in v.keys():
						names.append(name2)
	props = tstructure.get("props",{})
	if "limits" in props:
		for k in props["limits"].keys():
			names.append(k)
	if "industries" in tstructure:
		for ind in tstructure["industries"]:
			ind_def = defs.industries2[ind["name"]]
			for name in ind_def["input"].keys():
				names.append(name)
			for name in ind_def["output"].keys():
				names.append(name)
	if "blueprints" in tstructure:
		for name in tstructure["blueprints"]:
			names.append(name)
			bp_data = defs.blueprints[name]
			for item in bp_data["inputs"].keys():
				names.append(item)
			for item in bp_data["outputs"].keys():
				names.append(item)
	skill_loc = Skill.get_location(tstructure["name"])
	if skill_loc:
		for skill,data in skill_loc.items():
			if "item_req" in data:
				for item in data["item_req"].keys():
					names.append(item)
	if "quests" in tstructure:
		for name in tstructure["quests"]:
			qdata = defs.quests[name]
			for outcome in qdata["outcomes"]:
				objective_items = outcome["objectives"].get("items",{})
				reward_items = outcome["rewards"].get("items",{})
				for item in objective_items.keys():
					names.append(item)
				for item in reward_items.keys():
					names.append(item)
	return names
def character_item_names(cdata):
	pships = ship.gets(cdata["name"])
	names = []
	for name in cdata.get_items().keys():
		if name not in names:
			names.append(name)
	for pship in pships.values():
		for name in pship.get_gear().keys():
			if name not in names:
				names.append(name)
	pship = ship.get(cdata.ship())
	pos = pship.get("pos")
	stiles = defs.systems[pos["system"]]["tiles"]
	tile = copy.deepcopy(stiles.get(pos["x"],pos["y"]))
	res = map.terrain_to_resource(tile["terrain"])
	if res:
		names.append(res)
	otiles = defs.objmaps[pos["system"]]["tiles"]
	otile = copy.deepcopy(otiles.get(pos["x"],pos["y"]))
	if "items" in otile:
		for item in otile["items"].keys():
			names.append(item)
	if "ships" in otile:
		if cdata["name"] in otile["ships"]:
			for sname in otile["ships"][cdata["name"]]:
				pship = ship.get(sname)
				gear = pship.get_gear()
				for name in gear.keys():
					names.append(name)
	return names
def character_itemdata(cdata):
	return itemlist_data(character_item_names(cdata))
def structure_itemdata(tstructure):
	return itemlist_data(structure_item_names(tstructure))