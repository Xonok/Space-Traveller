import os
from . import user,io,gear,ship

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
class PItems(Items):
	def __init__(self,default=0,**kwargs):
		super().__init__(default,**kwargs)
		self.owner = ""
	def add(self,key,value):
		super().add(key,value)
		write(self.owner)
	def remove(self,key):
		super().remove(key)
		write(self.owner)
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
	def save(self):
		if not self.parent: raise Exception("Parent for SaveItems not set.")
		self.parent.save()
	def size(self):
		total = 0
		for key,value in self.items():
			total += size(key)*value
		return total
def equip(pdata,on,off,items,pgear):
	for item,amount in off.items():
		x = min(pgear.get(item),amount)
		pgear.add(item,-x)
		items.add(item,x)
	for item,amount in on.items():
		slots = ship.slots_left(pdata["ship"],gear.type(item),pgear)
		x = min(items.get(item),amount,slots)
		pgear.add(item,x)
		items.add(item,-x)
from . import defs
def size(item):
	if item in defs.goods:
		return 1
	if item in defs.gear_types:
		return defs.gear_types[item]["size"]
def space_used(user):
	used = 0
	for item,amount in pitems[user].items():
		size2 = size(item)
		used += size2*amount
	for item,amount in pgear[user].items():
		size2 = size(item)
		used += size2*amount
	return used