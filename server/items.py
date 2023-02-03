class Items(dict):
	def __init__(self,default=0,**kwargs):
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
	def max_in(self,item,equip=False,check_space=True):
		space = self.parent.get_space()
		if not check_space:
			space = 999999
		isize = size(item)
		if equip:
			ship_type = None
			if "ship" in self.parent:
				ship_type = self.parent["ship"]
			elif "type" in self.parent:
				ship_type = self.parent["type"]
			slots = ship.slots_left(ship_type,slot(item),self)
		else:
			slots = 9999
		if isize:
			max_items = int(space/isize)
		else:
			max_items = 999999
		return min(max_items,slots)
	def save(self):
		if not self.parent: raise Exception("Parent for SaveItems not set.")
		self.parent.save()
import os,copy
from . import user,io,ship,defs,factory,structure,error
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
def slot(item):
	if "slot" in defs.items[item]:
		return defs.items[item]["slot"]
	return type(item)
def prop(item_name,prop_name):
	item_data = defs.items[item_name]
	if "props" not in item_data or prop_name not in item_data["props"]: return
	return item_data["props"][prop_name]
def transfer(source,target,item,amount,equip=False,validate=False):
	check_space = source.parent != target.parent
	max_t = min(target.max_in(item,equip,check_space),source.get(item),amount)
	max_t = max(max_t,0)
	if validate and amount != max_t: return
	amount = max_t
	target.add(item,amount)
	source.add(item,-amount)
	target.parent.get_space()
	source.parent.get_space()
	return True
def items_space(items):
	space = 0
	for item,amount in items.items():
		space += size(item)*amount
	return space
def has_items(inv,items):
	for item,amount in items.items():
		if inv.get(item) < amount: return
	return True
def transfer_list(source,target,items):
	for item,amount in items.items():
		target.add(item,amount)
		source.add(item,-amount)
	target.parent.get_space()
	source.parent.get_space()
def transaction(a,b,froma,fromb):
	a_space = a.parent.get_space()-items_space(fromb)
	b_space = b.parent.get_space()-items_space(froma)
	if a_space < 0: raise error.User("Source doesn't have enough space to accept all items.")
	if b_space < 0: raise error.User("Target doesn't have enough space to accept all items.")
	if not has_items(a,froma): raise error.User("Source can't provide all items asked.")
	if not has_items(b,fromb): raise error.User("Target can't provide all items asked.")
	transfer_list(a,b,froma)
	transfer_list(b,a,fromb)
def equipped(gtype,items):
	current = 0
	for item,amount in items.items():
		if slot(item) == gtype:
			current += amount
	return current
def drop(self,data,pitems):
	self.check(data,"items")
	drop_items = data["items"]
	for name,amount in drop_items.items():
		pitems.add(name,-amount)
def use(self,data,pdata):
	self.check(data,"item")
	pship = ship.get(pdata.ship())
	pitems = pship.get_items()
	psystem = pship.get_system()
	px,py = pship.get_coords()
	used_item = data["item"]
	if pitems.get(used_item):
		if used_item in defs.machines:
			factory.use_machine(used_item,pitems,pdata)
		if used_item in defs.station_kits:
			structure.build(used_item,pdata,psystem,px,py)
def itemlist_data(ilist):
	data = {}
	for name in ilist:
		if name in defs.items:
			data[name] = copy.deepcopy(defs.items[name])
			data[name]["usable"] = name in defs.machines or name in defs.station_kits
		if name in defs.ship_types:
			data[name] = copy.deepcopy(defs.ship_types[name])
	return data
def structure_item_names(tstructure):
	names = []
	for name in tstructure["market"]["prices"].keys():
		names.append(name)
	for name in tstructure["inventory"]["items"].keys():
		names.append(name)
	for name in tstructure["inventory"]["gear"].keys():
		names.append(name)
	if "blueprints" in tstructure:	
		for name in tstructure["blueprints"]:
			names.append(name)
	return names
def player_item_names(pdata):
	pships = ship.gets(pdata["name"])
	names = []
	for pship in pships.values():
		for name in pship.get_items().keys():
			if name not in names:
				names.append(name)
		for name in pship.get_gear().keys():
			if name not in names:
				names.append(name)
	return names
def player_itemdata(pdata):
	return itemlist_data(player_item_names(pdata))
def structure_itemdata(tstructure,pdata):
	return itemlist_data(structure_item_names(tstructure))