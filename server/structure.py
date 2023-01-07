import copy,time
from . import items,io,defs,factory,ship,error,map,types

#in seconds
time_per_tick = 60*60 # 1 hour per tick.

class Structure(dict):
	def __init__(self,**kwargs):
		self.update(kwargs)
	def save(self):
		io.write2("structures",self["name"],self)
	def get_space(self):
		inv = self["inventory"]
		inv["space_extra"] = 0
		for item,amount in inv["gear"].items():
			if "props" not in defs.items[item]: continue
			if "space_max_station" not in defs.items[item]["props"]: continue
			inv["space_extra"] += defs.items[item]["props"]["space_max_station"]
		inv["space_left"] = inv["space_max"] + inv["space_extra"] - inv["items"].size() - inv["gear"].size()
		return inv["space_left"]
	def transfer(self,pdata,data):
		if self["owner"] != pdata["name"]: raise error.User("Can't transfer items with a structure that you don't own.")
		pship = ship.get(data["tship"])
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
		pship = ship.get(data["tship"])
		buy = data["buy"]
		sell = data["sell"]
		sitems = self["inventory"]["items"]
		pitems = pship.get_items()
		prices = self.get_prices()
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
			if item in defs.ship_types:
				amount = min(sitems.get(item),amount,limit)
				for i in range(amount):
					new_ship = ship.new(item,pdata["name"])
					new_ship["pos"] = copy.deepcopy[pship["pos"]]
					pdata["ships"][new_ship["name"]] = new_ship["name"]
					ship.add_player_ship(pship)
					pdata.save()
					sitems.add(item,-amount)
				pdata["credits"] -= amount*price
				self["credits"] += amount*price
				continue
			amount = min(pitems.max_in(item),sitems.get(item),amount,limit)
			amount = max(amount,0)
			pdata["credits"] -= amount*price
			self["credits"] += amount*price
			pitems.add(item,amount)
			sitems.add(item,-amount)
		pitems.parent.get_space()
		sitems.parent.get_space()
	def item_change(self):
		template = None
		if self["name"] in defs.premade_structures:
			template = copy.deepcopy(defs.premade_structures[self["name"]])
		items = {}
		sgear = self["inventory"]["gear"]
		sindustries = types.get(self,template,[],"population","industries")
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
		#Debug option. Uncomment to force ships to generate regardless of tick timing.
		#self.make_ships()
		if "timestamp" in self:
			now = time.time()
			if self["timestamp"]+time_per_tick < now:
				template = None
				if self["name"] in defs.premade_structures:
					template = copy.deepcopy(defs.premade_structures[self["name"]])
				self["timestamp"] += time_per_tick
				sitems = self["inventory"]["items"]
				sgear = self["inventory"]["gear"]
				sindustries = types.get(self,template,[],"population","industries")
				workers = self["population"]["workers"]
				for item,amount in sgear.items():
					if item not in defs.machines: continue
					for i in range(amount):
						factory.use_machine(item,sitems,self)
				if workers:
					for industry in sindustries:
						factory.use_industry(industry,sitems,workers)
					factory.use_industry("standard_drain",sitems,workers)
				self.make_ships()
			if self["timestamp"]+time_per_tick < now:
				self.tick()
		else:
			self["timestamp"] = time.time()
		self.save()
	def make_ships(self):
		for item,amount in self["market"]["demands"].items():
			if item in defs.ship_types:
				current = 0
				if item in self["inventory"]["items"]:
					current = self["inventory"]["items"][item]
				need = amount-current
				if need > 0:
					for i in range(need):
						self["inventory"]["items"].add(item,1)
					self.save()
	def buy_ship(self,data,pdata):
		oship = data["ship"]
		selected_offer = None
		for offer in self["ship_offers"]:
			if offer["ship"] == oship:
				selected_offer = offer
		if not selected_offer:
			raise error.User("This place doesn't sell a ship called "+oship)
		price = selected_offer["price"]
		credits = pdata["credits"]
		if price > credits:
			raise error.User("Too little money.")
		pship = ship.get(oship)
		ship.remove_player_ship(pship["owner"],pship["name"])
		pship["owner"] = pdata["name"]
		pdata["credits"] -= price
		self["ship_offers"].remove(selected_offer)
		system = self["pos"]["system"]
		x = self["pos"]["x"]
		y = self["pos"]["y"]
		pship.rename(pdata["name"]+","+pship["type"]+","+str(pship["id"]))
		ship.add_player_ship(pship)
		map.add_ship(pship,system,x,y)
		pship.save()
		pdata.save()
		self.save()
	def get_prices(self):
		template = None
		if self["name"] in defs.premade_structures:
			template = copy.deepcopy(defs.premade_structures[self["name"]])
		price_lists = types.get(self,template,[],"market","lists")
		price_overrides = types.get(self,template,{},"market","prices")
		change = types.get(self,None,{},"market","change")
		prices = {}
		for name,data in price_overrides.items():
			prices[name] = data
		for list_name in price_lists:
			data = defs.price_lists[list_name]
			up = data["price_up"]
			down = data["price_down"]
			for item_name in data["items"]:
				if item_name in prices: continue
				price = None
				if item_name in defs.items:
					price = defs.items[item_name]["price"]
				if item_name in defs.ship_types:
					price = defs.ship_types[item_name]["price"]
				if not price:
					raise Exception("Price unset for item: "+item_name)
				consumed = 1
				produced = 1
				if item_name in change:
					if change[item_name] > 0:
						produced = data["produced"]
					elif change[item_name] < 0:
						consumed = data["consumed"]
				prices[item_name] = {
					"buy": round(price*down*consumed*produced),
					"sell": round(price*up*consumed*produced)
				}
		return prices
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
	if item_name not in defs.station_kits: raise error.User("Item "+item_name+" is not a station kit.")
	if "structure" in tile: raise error.User("Can't build. There is already a structure on this tile.")
	if not pitems.get(item_name): raise error.User("You don't have a "+item_name+" in items.")
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
	