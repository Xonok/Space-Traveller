import copy,time
from . import items,io,defs,factory,ship

#in seconds
time_per_tick = 60*60 # 1 hour per tick.

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
		if self["owner"] != pdata["name"]:
			return
		pship = ship.get(pdata.ship())
		sinv = self["inventory"]
		take = data["take"]
		give = data["give"]
		take_gear = data["take_gear"]
		give_gear = data["give_gear"]
		pitems = pship.get_items()
		pgear = pship.get_gear()
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
	def trade(self,pdata,data):
		pship = ship.get(pdata.ship())
		buy = data["buy"]
		sell = data["sell"]
		sitems = self["inventory"]["items"]
		pitems = pship.get_items()
		prices = self["market"]["prices"]
		for item,amount in sell.items():
			if item not in prices:
				continue
			price = prices[item]["buy"]
			limit = int(self["credits"]/price)
			amount = min(sitems.max_in(item),pitems.get(item),amount,limit)
			amount = max(amount,0)
			self["credits"] -= amount*price
			pdata["credits"] += amount*price
			sitems.add(item,amount)
			pitems.add(item,-amount)
		for item,amount in buy.items():
			if item not in prices:
				continue
			price = prices[item]["sell"]
			limit = int(pdata["credits"]/price)
			amount = min(pitems.max_in(item),sitems.get(item),amount,limit)
			amount = max(amount,0)
			pdata["credits"] -= amount*price
			self["credits"] += amount*price
			pitems.add(item,amount)
			sitems.add(item,-amount)
		pitems.parent.get_space()
		sitems.parent.get_space()
	def item_change(self):
		items = {}
		sgear = self["inventory"]["gear"]
		sindustries = self["population"]["industries"]
		workers = self["population"]["workers"]/1000
		for gear,count in sgear.items():
			if gear not in defs.machines: continue
			machine = defs.machines[gear]
			for item,amount in machine["input"].items():
				if item not in items:
					items[item] = 0
				items[item] -= amount*count
			for item,amount in machine["output"].items():
				if item not in items:
					items[item] = 0
				items[item] += amount*count
		if workers:
			for pindustry in sindustries:
				if pindustry not in defs.industries: continue
				industry = defs.industries[pindustry]
				for item,amount in industry["input"].items():
					if item not in items:
						items[item] = 0
					items[item] -= round(amount*workers)
				for item,amount in industry["output"].items():
					if item not in items:
						items[item] = 0
					items[item] += round(amount*workers)
			industry = defs.industries["standard_drain"]
			for item,amount in industry["input"].items():
				if item not in items:
					items[item] = 0
				items[item] -= round(amount*workers)
		self["market"]["change"] = items
		self.save()
		return items
	def tick(self):
		if "timestamp" in self:
			now = time.time()
			if self["timestamp"]+time_per_tick < now:
				self["timestamp"] += time_per_tick
				sitems = self["inventory"]["items"]
				sgear = self["inventory"]["gear"] 
				sindustries = self["population"]["industries"]
				workers = self["population"]["workers"]
				for item,amount in sgear.items():
					if item not in defs.machines: continue
					for i in range(amount):
						factory.use_machine(item,sitems,self)
				if workers:
					for industry in sindustries:
						factory.use_industry(industry,sitems,workers)
					factory.use_industry("standard_drain",sitems,workers)
			if self["timestamp"]+time_per_tick < now:
				self.tick()
		else:
			self["timestamp"] = time.time()
		self.save()
	def make_ships(self):
		for item,amount in self["market"]["demands"].items():
			if item in defs.ship_types:
				current = 0
				for offer in self["ship_offers"]:
					oship = offer["ship"]
					pship = ship.get(oship)
					if pship["type"] == item:
						current += 1
				need = amount-current
				if need > 0:
					for i in range(need):
						new_ship = ship.new(item,"")
						offer = {}
						offer["ship"] = new_ship["name"]
						offer["price"] = defs.ship_types[item]["price"]
						self["ship_offers"].append(offer)
					self.save()
def get(system,x,y):
	tiles = defs.objmaps[system]["tiles"]
	tile = tiles.get(x,y)
	if "structure" in tile:
		return defs.structures[tile["structure"]]
def build(item_name,pdata,system,px,py):
	pship = ship.get(pdata.ship())
	stiles = defs.objmaps[system]["tiles"]
	tile = stiles.get(px,py)
	pitems = pship.get_items()
	if item_name not in defs.station_kits: return
	if "structure" in tile: return
	if not pitems.get(item_name): return
	kit_def = defs.station_kits[item_name]
	station = copy.deepcopy(defs.defaults["structure"])
	station["name"] = system+","+str(px)+","+str(py)
	station["type"] = "station"
	station["ship"] = kit_def["ship"]
	station["owner"] = pdata["name"]
	tile["structure"] = station["name"]
	stiles.set(px,py,tile)
	defs.structures[station["name"]] = station
	pitems.add(item_name,-1)
	stiles.save()
	station.save()
	print("Built "+station["name"])
def pick_up(pdata,system,px,py):
	pass
	