import os
from . import user,io,gear,ship

class Items(dict):
	def __init__(self,default=0,**kwargs):
		self.default = default
		self.owner = ""
		self.update(kwargs)
	def add(self,key,value):
		self[key] = self.get(key)+value
		if not self[key]:
			del self[key]
		write(self.owner)
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
pitems = {}
pgear = {}
def write(user):
	table = {}
	if user in pitems:
		table = pitems[user]
	io.write(os.path.join("user_items",user+".json"),table)
	table = {}
	if user in pgear:
		table = pgear[user]
	io.write(os.path.join("user_gear",user+".json"),table)
def init(user):
	pitems[user] = io.read(os.path.join("user_items",user+".json"),PItems)
	pitems[user].owner = user
	pgear[user] = io.read(os.path.join("user_gear",user+".json"),PItems)
	pgear[user].owner = user
for user in user.get_all():
	init(user)
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
from . import goods
def size(item):
	if item in goods.default:
		return 1
	if item in gear.types:
		return gear.types[item]["size"]
def space_used(user):
	used = 0
	for item,amount in pitems[user].items():
		size2 = size(item)
		used += size2*amount
	for item,amount in pgear[user].items():
		size2 = size(item)
		used += size2*amount
	return used