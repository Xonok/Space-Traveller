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
	def max_in(self,item,equip=False):
		space = self.parent.get_space()
		isize = size(item)
		if equip:
			slots = ship.slots_left(self.parent["ship"],type(item),self)
		else:
			slots = 9999
		return min(int(space/isize),slots)
	def save(self):
		if not self.parent: raise Exception("Parent for SaveItems not set.")
		self.parent.save()
import os
from . import user,io,ship,defs,factory,structure
def size(item):
	if item in defs.items:
		return defs.items[item]["size"]
def type(item):
	if "type" in defs.items[item]:
		return defs.items[item]["type"]
	else:
		return "other"
def max_transfer(source,target,item,amount,equip):
	amount = min(target.max_in(item,equip),source.get(item),amount)
	amount = max(amount,0)
	return amount
def transfer(source,target,item,amount,equip=False,validate=False):
	max_t = max_transfer(source,target,item,amount,equip)
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
	if a_space < 0: return
	if b_space < 0: return
	if not has_items(a,froma): return
	if not has_items(b,fromb): return
	transfer_list(a,b,froma)
	transfer_list(b,a,fromb)
	return True
def equipped(gtype,items):
	current = 0
	for item,amount in items.items():
		if type(item) == gtype:
			current += amount
	return current
def drop(self,data,pitems):
	if not self.check(data,"items"):
		return
	drop_items = data["items"]
	for name,amount in drop_items.items():
		pitems.add(name,-amount)
def use(self,data,pdata):
	if not self.check(data,"item"):
		return
	pitems = pdata.get_items()
	psystem = pdata.get_system()
	px,py = pdata.get_coords()
	used_item = data["item"]
	if pitems.get(used_item):
		factory.use_machine(used_item,pitems,pdata)
		structure.build(used_item,pdata,psystem,px,py)
def itemlist_data(ilist):
	data = {}
	for name in ilist:
		if name not in defs.items: continue
		data[name] = defs.items[name]
	return data
def market_itemdata(tstructure):
	ilist = structure.market_item_names(tstructure)
	return itemlist_data(ilist)