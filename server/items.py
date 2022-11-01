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
from . import user,io,ship,defs
def size(item):
	if item in defs.items:
		return defs.items[item]["size"]
def type(item):
	if "type" in defs.items[item]:
		return defs.items[item]["type"]
	else:
		return "other"
def transfer(source,target,item,amount,equip=False):
	amount = min(target.max_in(item,equip),source.get(item),amount)
	amount = max(amount,0)
	target.add(item,amount)
	source.add(item,-amount)
	target.parent.get_space()
	source.parent.get_space()
def equipped(gtype,items):
	current = 0
	for item,amount in items.items():
		if type(item) == gtype:
			current += amount
	return current