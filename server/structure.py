import copy,time
from . import items,io,defs,factory,ship,error,map,types,gathering,build

#in seconds
time_per_tick = 60*60*3 # 3 hours per tick.

class Structure(dict):
	def __init__(self,**kwargs):
		self.update(kwargs)
	def save(self):
		io.write2("structures",self["name"],self)
	def get_items(self):
		return self["inventory"]["items"]
	def get_gear(self):
		return self["inventory"]["gear"]
	def get_space(self):
		inv = self["inventory"]
		inv["space_max"] = defs.ship_types[self["ship"]]["space"]
		inv["space_extra"] = 0
		for item,amount in inv["gear"].items():
			if "props" not in defs.items[item]: continue
			if "space_max" in defs.items[item]["props"]:
				inv["space_extra"] += defs.items[item]["props"]["space_max"]*amount
		inv["space_left"] = inv["space_max"] + inv["space_extra"] - inv["items"].size() - inv["gear"].size()
		return inv["space_left"]
	def transfer(self,pdata,data):
		if self["owner"] != pdata["name"]: raise error.User("Can't transfer items with a structure that you don't own.")
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
			space = pship.get_space()
			idata = defs.items[item]
			net_size = items.net_size(item)
			max_unequip = 99999
			if net_size < 0:
				max_unequip = space//-net_size
			amount = min(max_unequip,amount)
			amount = max(amount,0)
			items.transfer(pgear,sgear,item,amount,equip=True)
		for item,amount in take_gear.items():
			space = self.get_space()
			idata = defs.items[item]
			net_size = items.net_size(item)
			max_unequip = 99999
			if net_size < 0:
				max_unequip = space//-net_size
			amount = min(max_unequip,amount)
			amount = max(amount,0)
			items.transfer(sgear,pgear,item,amount,equip=True)
	def equip(self,data):
		on = data["station-on"]
		off = data["station-off"]
		sitems = self["inventory"]["items"]
		sgear = self["inventory"]["gear"]
		for item,amount in off.items():
			space = self.get_space()
			idata = defs.items[item]
			extra_space = items.space_max(item)
			max_unequip = 99999
			if extra_space > 0:
				max_unequip = space//extra_space
			amount = min(max_unequip,amount)
			amount = max(amount,0)
			items.transfer(sgear,sitems,item,amount)
		for item,amount in on.items():
			items.transfer(sitems,sgear,item,amount,equip=True)
	def trade(self,pdata,data):
		pship = ship.get(pdata.ship())
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
				amount = max(amount,0)
				for i in range(amount):
					new_ship = ship.new(item,pdata["name"])
					new_ship["pos"] = copy.deepcopy(pship["pos"])
					pdata["ships"].append(new_ship["name"])
					ship.add_player_ship(pship)
					map.add_ship(new_ship,pship["pos"]["system"],pship["pos"]["x"],pship["pos"]["y"])
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
		pdata.save()
		self.save()
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
		self["market"]["change"] = items
		self.save()
		return items
	def item_change2(self):
		template = None
		if self["name"] in defs.premade_structures:
			template = copy.deepcopy(defs.premade_structures[self["name"]])
		items = self["market"]["change"]
		sgear = self["inventory"]["gear"]
		sindustries = types.get(self,template,[],"population","industries")
		workers = self["population"]["workers"]/1000
		if workers and self["type"] == "planet":
			industry = defs.industries["standard_drain"]
			for item,amount in industry["input"].items():
				if item not in items:
					items[item] = -round(amount*workers)
		self["market"]["change"] = items
		self.save()
		return items
	def get_max_pop(self):
		result = 0
		ship_max_pop = ship.prop(self["ship"],"max_pop")
		if ship_max_pop: result += ship_max_pop
		for gear,amount in self.get_gear().items():
			gear_max_pop = items.prop(gear,"max_pop")
			if gear_max_pop: result += gear_max_pop*amount
		self["population"]["max_pop"] = result
		return result
	def get_min_pop(self):
		result = 0
		ship_min_pop = ship.prop(self["ship"],"min_pop")
		if ship_min_pop: result += ship_min_pop
		for gear,amount in self.get_gear().items():
			gear_min_pop = items.prop(gear,"min_pop")
			if gear_min_pop: result += gear_min_pop*amount
		self["population"]["min_pop"] = result
		return result
	def tick(self):
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
				prev_items = copy.deepcopy(sitems)
				for item,amount in sgear.items():
					idata = defs.items[item]
					if "props" in idata and "station_mining" in idata["props"]:
						for i in range(amount):
							try:
								gathering.gather(self,False)
							except Exception as e:
								print(e)
				for item,amount in sgear.items():
					if item in defs.machines:
						for i in range(amount):
							factory.use_machine(item,sitems,self)
				if workers:
					after_items = copy.deepcopy(sitems)
					if not len(sindustries):
						if prev_items != after_items:
							self["population"]["workers"] = round(self["population"]["workers"]*1.05)
						else:
							self["population"]["workers"] = round(self["population"]["workers"]*0.98)
					for industry in sindustries:
						factory.use_industry(industry,sitems,workers,self)
					build.update(self)
					self.item_change()
					if self["type"] == "planet":
						factory.consume(self["market"]["change"],sitems,workers,self)
				max_pop = self.get_max_pop()
				min_pop = self.get_min_pop()
				if max_pop and self["population"]["workers"] > max_pop:
					self["population"]["workers"] = max_pop
				if min_pop and self["population"]["workers"] < min_pop:
					self["population"]["workers"] = min_pop
				self.item_change()
				self.item_change2()
				self.make_ships()
				self.get_space()
			if self["timestamp"]+time_per_tick < now:
				self.tick()
		else:
			self["timestamp"] = time.time()
		self.save()
	def make_ships(self):
		template = None
		if self["name"] in defs.premade_structures:
			template = copy.deepcopy(defs.premade_structures[self["name"]])
		demands = copy.deepcopy(types.get(self,template,{},"market","demands"))
		price_lists = types.get(self,template,[],"market","lists")
		for list_name in price_lists:
			price_list = defs.price_lists[list_name]
			if "generate_demand" in price_list:
				for item in price_list["items"]:
					if item not in demands:
						demands[item] = 10
		for item,amount in demands.items():
			if item in defs.ship_types or item in defs.items:
				current = 0
				if item in self["inventory"]["items"]:
					current = self["inventory"]["items"][item]
				need = amount-current
				if need > 0:
					for i in range(need):
						self["inventory"]["items"].add(item,1)
					self.save()
			else:
				raise Exception("Unknown item or ship type: "+item)
	def get_prices(self):
		template = None
		if self["name"] in defs.premade_structures:
			template = copy.deepcopy(defs.premade_structures[self["name"]])
		price_lists = types.get(self,template,[],"market","lists")
		price_overrides = types.get(self,template,{},"market","prices")
		self.item_change()
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
		self.item_change2()
		return prices
def get(system,x,y):
	tiles = defs.objmaps[system]["tiles"]
	tile = tiles.get(x,y)
	if "structure" in tile:
		return defs.structures[tile["structure"]]
def build_station(item_name,pdata,system,px,py):
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
	station["pos"] = copy.deepcopy(pship["pos"])
	tile["structure"] = station["name"]
	stiles.set(px,py,tile)
	defs.structures[station["name"]] = station
	station.get_space()
	pitems.add(item_name,-1)
	pship.save()
	stiles.save()
	station.save()
	print("Built "+station["name"])
def pick_up(pship):
	x = pship["pos"]["x"]
	y = pship["pos"]["y"]
	system = pship["pos"]["system"]
	otiles = map.objmap(system)
	otile = otiles.get(x,y)
	tstruct = get(system,x,y)
	if not tstruct: raise error.User("There is no station on this tile.")
	if tstruct["type"] != "station": raise error.User("Can't pick up a "+tstruct["type"])
	if tstruct["owner"] != pship["owner"]: raise error.User("Can't pick up a station you don't own.")
	if len(tstruct["inventory"]["items"]) or len(tstruct["inventory"]["gear"]): raise error.User("The station still contains items.")
	if tstruct["credits"] != 0: raise error.User("The station still contains credits.")
	kit_name = None
	for name,data in defs.station_kits.items():
		print(name,data)
		if data["ship"] == tstruct["ship"]:
			kit_name = name
			break
	pship.get_items().add(kit_name,1)
	del defs.structures[tstruct["name"]]
	del otile["structure"]
	otiles.set(x,y,otile)
	otiles.save()
	pship.get_space()
	pship.save()
	print(items.size(kit_name),pship.get_space())