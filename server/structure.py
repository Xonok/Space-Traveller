import copy,time
from . import Item,Entity

class Structure(dict):
	def __init__(self,**kwargs):
		self.update(kwargs)
		if "props" not in self:
			self["props"] = {}
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
	def next_tick(self):
		return tick.time_until_next("long")
	def transfer(self,cdata,data):
		Item.transfer(cdata,data)
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
		items = self["market"]["change"]
		workers = self["population"]["workers"]/1000
		if workers and self["type"] == "planet":
			industry = defs.industries["growth_boost"]
			for item,amount in industry["input"].items():
				if item not in items:
					items[item] = -round(amount*workers)
			industry = defs.industries["standard_drain"]
			for item,amount in industry["input"].items():
				if item not in items:
					items[item] = -round(amount*workers)
		self["market"]["change"] = items
		self["market"]["balance"] = Item.industry.get_balance(self)
		self.save()
		return items
	def get_pop(self):
		return self["population"]["workers"]
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
		Entity.tick(self)
		
		if "timestamp" in self:
			ticks = tick.ticks_since(self["timestamp"],"long")
			ticks = max(ticks,0)
			for i in range(ticks):
				Item.industry.tick(self)
				template = None
				default_items = {}
				if self["name"] in defs.premade_structures:
					template = copy.deepcopy(defs.premade_structures[self["name"]])
					default_items = template["inventory"]["items"]
				sitems = self["inventory"]["items"]
				sgear = self["inventory"]["gear"]
				sindustries = types.get(self,template,[],"population","industries")
				workers = self["population"]["workers"]
				for item,amount in default_items.items():
					current = sitems.get(item)
					if current < amount:
						sitems.add(item,amount-current)
				prev_items = copy.deepcopy(sitems)
				for item,amount in sgear.items():
					idata = defs.items[item]
					if "props" in idata and "station_mining" in idata["props"]:
						for j in range(amount):
							try:
								gathering.gather(self,False)
							except Exception as e:
								print(e)
				for item,amount in sgear.items():
					if item in defs.machines:
						for j in range(amount):
							factory.use_machine(item,sitems,self)
				#if workers:
				#	after_items = copy.deepcopy(sitems)
				#	if not len(sindustries):
				#		if prev_items != after_items:
				#			self["population"]["workers"] = round(self["population"]["workers"]*1.03)
				#		else:
				#			self["population"]["workers"] = round(self["population"]["workers"]*0.98)
				#	for industry in sindustries:
				#		factory.use_industry(industry,sitems,workers,self)
				#	build.update(self)
				#	self.item_change()
				#	if self["type"] == "planet":
				#		factory.use_industry("growth_boost",sitems,workers,self)
				#		factory.consume(self["market"]["change"],sitems,workers,self)
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
			self["timestamp"] = time.time()
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
	def get_industries(self):
		template = None
		if self["name"] in defs.premade_structures:
			template = copy.deepcopy(defs.premade_structures[self["name"]])
		industries = types.get(self,template,[],"population","industries")
		table = {}
		for name in industries:
			table[name] = defs.industries[name]
		return table
	def repair(self,server,data,cdata):
		pship = ship.get(data["ship"])
		hull = data["hull"]
		armor = data["armor"]
		stats = pship["stats"]
		hull_lost = stats["hull"]["max"]-stats["hull"]["current"]
		armor_lost = stats["armor"]["max"]-stats["armor"]["current"]
		repair_fees = self.get_repair_fees()
		cost_per_hull = repair_fees["hull"]
		cost_per_armor = repair_fees["armor"]
		repair_cost = hull*cost_per_hull + armor*cost_per_armor
		if pship["owner"] != cdata["name"]: raise error.User("You don't own that ship.")
		if hull > hull_lost: raise error.User("Can't repair more hull than is broken.")
		if armor > armor_lost: raise error.User("Can't repair more armor than is broken.")
		if repair_cost > cdata["credits"]: raise error.User("Not enough money to repair this much.")
		stats["hull"]["current"] += hull
		stats["armor"]["current"] += armor
		cdata["credits"] -= repair_cost
		server.add_message("Successful repair.")
		pship.save()
		cdata.save()
	def get_repair_fees(self):
		return {
			"hull": 200,
			"armor": 50
		}
	def update_trade(self,cdata,data):
		price_list = data["items"]
		if cdata["name"] != self["owner"]: raise error.User("You don't own this structure.")
		for item,data in price_list.items():
			if item not in defs.items and item not in defs.ship_types: raise error.User("Unknown item or ship: "+item)
			prev = self["market"]["prices"].get(item,{})
			buy = data.get("buy",prev.get("buy",0))
			sell = data.get("sell", prev.get("sell", 0))
			if type(buy) is not int or type(sell) is not int: raise error.User("Only ints allowed for prices.")
			self["market"]["prices"][item] = {
				"buy": buy,
				"sell": sell
			}
		self.save()
def get(system,x,y):
	tiles = map.otiles(system)
	tile = tiles.get(x,y)
	if "structure" in tile:
		return defs.structures[tile["structure"]]
def from_pos(pos):
	return get(pos["system"],pos["x"],pos["y"])
def build_station(item_name,cdata,system,px,py):
	pship = ship.get(cdata.ship())
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
	station["owner"] = cdata["name"]
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
	otiles = map.otiles(system)
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
def give_credits(data,cdata,tstructure):
	amount = data["amount"]
	if cdata["name"] != tstructure["owner"]: raise error.User("You don't own this structure.")
	if cdata["credits"] < amount: raise error.User("Can't give more credits than you have.")
	cdata["credits"] -= amount
	tstructure["credits"] += amount
	cdata.save()
	tstructure.save()
def take_credits(data,cdata,tstructure):
	amount = data["amount"]
	if cdata["name"] != tstructure["owner"]: raise error.User("You don't own this structure.")
	if tstructure["credits"] < amount: raise error.User("Can't take more credits than the structure has.")
	tstructure["credits"] -= amount
	cdata["credits"] += amount
	cdata.save()
	tstructure.save()
def update_name(data,cdata):
	sname = data["structure"]
	name = data["name"]
	tstruct = defs.structures.get(sname)
	if not tstruct: raise error.User("There is no structure called: "+sname)
	if tstruct["owner"] != cdata["name"]: raise error.User("You don't own this structure.")
	if not isinstance(name,str): raise error.User("The name must be a string.")
	if len(name) > 20: raise error.User("The name must be fewer than 20 characters/bytes.")
	tstruct["custom_name"] = name
	tstruct.save()
def update_desc(data,cdata):
	sname = data["structure"]
	desc = data["desc"]
	tstruct = defs.structures.get(sname)
	if not tstruct: raise error.User("There is no structure called: "+sname)
	if tstruct["owner"] != cdata["name"]: raise error.User("You don't own this structure.")
	if not isinstance(desc,str): raise error.User("The description must be a string.")
	if len(desc) > 4000: raise error.User("The description must be fewer than 4000 characters/bytes.")
	tstruct["desc"] = desc
	tstruct.save()
from . import items,io,defs,factory,ship,error,map,types,gathering,build,tick
