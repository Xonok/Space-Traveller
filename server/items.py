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
from . import defs
def size(item):
	if item in defs.goods:
		return 1
	if item in defs.gear_types:
		return defs.gear_types[item]["size"]