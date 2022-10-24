from . import items,io,ship,gear
class Structure(dict):
	def __init__(self,**kwargs):
		self.update(kwargs)
	def save(self):
		io.write2("structures",self["name"],self)
	def get_space(self):
		inv = self["inventory"]
		inv["space_left"] = inv["space_max"] + inv["space_extra"] - inv["items"].size() - inv["gear"].size()
		return inv["space_left"]
	def transfer(self,pdata,data):
		pinv = pdata["inventory"]
		sinv = self["inventory"]
		take = data["take"]
		give = data["give"]
		take_gear = data["take_gear"]
		give_gear = data["give_gear"]
		pitems = pinv["items"]
		pgear = pinv["gear"]
		sitems = sinv["items"]
		sgear = sinv["gear"]
		for item,amount in give.items():
			items.transfer(pitems,sitems,item,amount)
		for item,amount in take.items():
			items.transfer(sitems,pitems,item,amount)
		for item,amount in give_gear.items():
			items.transfer(pgear,sgear,item,amount,equip=True)
		for item,amount in take_gear.items():
			items.transfer(sgear,pgear,item,amount,equip=True)
	def equip(self,data):
		on = data["station-on"]
		off = data["station-off"]
		sitems = self["inventory"]["items"]
		sgear = self["inventory"]["gear"]
		for item,amount in off.items():
			items.transfer(sgear,sitems,item,amount)
		for item,amount in on.items():
			items.transfer(sitems,sgear,item,amount,equip=True)
		