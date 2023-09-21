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
class SaveItems(Items):
	def __init__(self,default=0,**kwargs):
		super().__init__(default,**kwargs)
		self.parent = None
	def add(self,key,value):
		super().add(key,value)
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
from . import ship,defs,factory,structure,map,Item
def size(item):
	if item in defs.items:
		return defs.items[item]["size"]
	if item in defs.ship_types:
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
def drop(self,data,pship):
	self.check(data,"items")
	drop_items = data["items"]
	pitems = pship["inventory"]["items"]
	pos = pship["pos"]
	objmap = map.otiles(pos["system"])
	objtile = objmap.get(pos["x"],pos["y"])
	if "items" not in objtile:
		objtile["items"] = {}
	for name,amount in drop_items.items():
		if name not in objtile["items"]:
			objtile["items"][name] = 0
		objtile["items"][name] += amount
		pitems.add(name,-amount)
	objmap.set(pos["x"],pos["y"],objtile)
	objmap.save()
	pship.save()
def use(self,data,cdata):
	self.check(data,"item")
	pship = ship.get(cdata.ship())
	pitems = pship.get_items()
	pgear = pship.get_items()
	psystem = pship.get_system()
	px,py = pship.get_coords()
	used_item = data["item"]
	if used_item in defs.items:
		idata = defs.items[used_item]
	elif used_item in defs.ship_types:
		idata = defs.ship_types[used_item]
	props = idata.get("props",{})
	manual = props.get("manual",False)
	consumable = props.get("consumable",False)
	if pitems.get(used_item):
		if used_item in defs.station_kits:
			structure.build_station(used_item,cdata,psystem,px,py)
		if manual and used_item in defs.machines:
			factory.use_machine(used_item,pitems)
		if consumable:
			Item.consumable(used_item,pitems,pship)
		if used_item in defs.ship_types and used_item in pitems:
			owner = cdata["name"]
			new_ship = ship.new(used_item,owner)
			new_ship["pos"] = copy.deepcopy(pship["pos"])
			cdata["ships"].append(new_ship["name"])
			ship.add_character_ship(new_ship)
			map.add_ship(new_ship,new_ship["pos"]["system"],new_ship["pos"]["x"],new_ship["pos"]["y"])
			pitems.add(used_item,-1)
	if pgear.get(used_item):
		if used_item in defs.station_kits:
			structure.build_station(used_item,cdata,psystem,px,py)
		if manual and used_item in defs.machines:
			factory.use_machine(used_item,pitems)
		if used_item in defs.ship_types and used_item in pgear:
			owner = cdata["name"]
			new_ship = ship.new(used_item,owner)
			new_ship["pos"] = copy.deepcopy(pship["pos"])
			cdata["ships"].append(new_ship["name"])
			ship.add_character_ship(new_ship)
			map.add_ship(new_ship,new_ship["pos"]["system"],new_ship["pos"]["x"],new_ship["pos"]["y"])
			pgear.add(used_item,-1)
	cdata.save()
def itemlist_data(ilist):
	data = {}
	for name in ilist:
		if name in defs.items:
			idata = defs.items[name]
			props = idata.get("props",{})
			category_usable = "use" in defs.item_categories.get(idata["type"])
			usable = True if "manual" in props or "consumable" in props else False
			data[name] = copy.deepcopy(defs.items[name])
		if name in defs.ship_types:
			category_usable = True
			data[name] = copy.deepcopy(defs.ship_types[name])
		data[name]["usable"] = category_usable or usable
	return data
def structure_item_names(tstructure):
	names = []
	for name in tstructure["market"]["prices"].keys():
		names.append(name)
	for name in tstructure["inventory"]["items"].keys():
		names.append(name)
	for name in tstructure["inventory"]["gear"].keys():
		names.append(name)
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
	return names
def character_item_names(cdata):
	pships = ship.gets(cdata["name"])
	names = []
	for pship in pships.values():
		for name in pship.get_items().keys():
			if name not in names:
				names.append(name)
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
	return names
def character_itemdata(cdata):
	return itemlist_data(character_item_names(cdata))
def structure_itemdata(tstructure):
	return itemlist_data(structure_item_names(tstructure))