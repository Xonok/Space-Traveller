import copy,time,traceback,random
from . import Item,Entity,Skill,func

class Structure(dict):
	def __init__(self,**kwargs):
		super().__init__()
		self.update(kwargs)
		if "props" not in self:
			self["props"] = {}
	def init(self):
		self.get_room()
	def save(self):
		io.write2("structures",self["name"],self)
	def get_items(self):
		return self["items"]
	def get_gear(self):
		return self["gear"]
	def get_room(self):
		room = self["stats"]["room"]
		room["max"] = defs.ship_types[self["ship"]]["room"]
		for item,amount in self["gear"].items():
			if "props" not in defs.items[item]: continue
			if "room_max" in defs.items[item]["props"]:
				room["max"] += defs.items[item]["props"]["room_max"]*amount
		room["current"] = room["max"] - self["items"].size() - self["gear"].size()
		return room["current"]
	def get_industries(self):
		ind_defs = {}
		if "industries" not in self:
			return ind_defs
		for ind in self["industries"]:
			name = ind["name"]
			ind_defs[name] = defs.industries2[name]
		return ind_defs
	def next_tick(self):
		return tick.time_until_next("long")
	def transfer(self,cdata,data,server):
		Item.transfer(cdata,data,server=server)
		self.item_change()
		Item.industry.prepare(self)
	def item_change(self):
		def add(table,item,amount):
			if item not in table:
				table[item] = 0
			table[item] += amount
		change = {}
		produced = {}
		consumed = {}
		#machines
		sgear = self["gear"]
		for gear,count in sgear.items():
			if gear not in defs.machines: continue
			machine = defs.machines[gear]
			for item,amount in machine["input"].items():
				consumed[item] = True
				add(change,item,-amount*count)
			for item,amount in machine["output"].items():
				produced[item] = True
				add(change,item,amount*count)
		#industries
		for data in self.get("industries",[]):
			idata = defs.industries2[data["name"]]
			input = idata["input"]
			output = idata["output"]
			min = idata["min"]
			workers = data["workers"]
			if workers < min:
				for item,amount in input.items():
					consumed[item] = True
				for item,amount in output.items():
					produced[item] = True
			else:
				for item,amount in input.items():
					consumed[item] = True
					add(change,item,round(-amount*workers/1000))
				for item,amount in output.items():
					produced[item] = True
					add(change,item,round(amount*workers/1000))
		self["market"]["change"] = change
		self["market"]["balance"] = {"produced":produced,"consumed":consumed}
		self.save()
	def tick(self):
		cdata = defs.characters[self["owner"]]
		shipdef = defs.ship_types[self["ship"]]
		Item.transport.check(self)
		skill_station = cdata["skills"].get("station",0)
		skill_deficit_station = shipdef["tech"]-skill_station
		success_chance_station = 0.5**skill_deficit_station
		if self["name"] in defs.predefined_structures:
			success_chance_station = 1
		if "timestamp" in self:
			ticks = tick.ticks_since(self["timestamp"],"long")
			ticks = max(ticks,0)
			ind_max = Item.industry.prepare(self)
			for i in range(ticks):
				roll = random.random()
				if roll > success_chance_station:
					continue
				Item.industry.tick(self,ind_max)
				Item.transport.tick(self)
				reputation.tick(self)
				sgear = self["gear"]
				try:
					gathering.gather(self,None,reduce=False,user=False)
				except Exception as e:
					print("Structure.tick",self["name"])
					print(traceback.format_exc())
					raise
				for item,amount in sgear.items():
					if item in defs.machines:
						idata = defs.items[item]
						skill_factory = cdata["skills"].get("factory",0)
						skill_deficit_factory = idata["tech"]-skill_factory
						success_chance_factory = 0.5**skill_deficit_factory
						for j in range(amount):
							if skill_deficit_factory > 0:
								roll = random.random()
								if roll > success_chance_factory:
									continue
							if factory.use_machine(item,self):
								noob_factor = 1
								if cdata["level"] < 10:
									noob_factor += (9-cdata["level"])/2
								level_factor = 1/(cdata["level"]+1)
								xp_amount = func.f2ir((10+idata["tech"]*2)*noob_factor*level_factor)
								Skill.gain_xp_flat(cdata,xp_amount)
				build.update(self)
				Item.scrapyard.update(self)
				Item.research.update(self)
				self.make_ships()
				self.get_room()
			self["timestamp"] = time.time()
		else:
			self["timestamp"] = time.time()
		self.item_change()
		self.save()
	def make_ships(self):
		template = None
		if self["name"] in defs.predefined_structures:
			template = copy.deepcopy(defs.predefined_structures[self["name"]])
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
				if item in self["items"]:
					current = self["items"][item]
				need = amount-current
				if need > 0:
					for i in range(need):
						self["items"].add(item,1)
					self.save()
			else:
				raise Exception("Unknown item or ship type: "+item)
	def get_prices(self):
		template = None
		if self["name"] in defs.predefined_structures:
			template = copy.deepcopy(defs.predefined_structures[self["name"]])
		price_lists = types.get(self,template,[],"market","lists")
		price_overrides = types.get(self,template,{},"market","prices")
		balance = types.get(self,None,{},"market","balance")
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
				elif item_name in defs.ship_types:
					price = defs.ship_types[item_name]["price"]
				else:
					raise Exception("Unknown item: "+item_name)
				if not price:
					raise Exception("Price unset for item: "+item_name)
				consumed = 1
				produced = 1
				if len(balance) and item_name in balance["consumed"]:
					consumed = data["consumed"]
				elif len(balance) and item_name in balance["produced"]:
					produced = data["produced"]
				
				prices[item_name] = {
					"buy": round(price*down*consumed*produced),
					"sell": round(price*up*consumed*produced)
				}
		return prices
	def repair(self,server,ship_id,hull,armor,cdata):
		pship = ship.get(ship_id)
		ship_def = defs.ship_types[pship["type"]]
		sstats = pship["stats"]
		hull_lost = sstats["hull"]["max"]-sstats["hull"]["current"]
		armor_lost = sstats["armor"]["max"]-sstats["armor"]["current"]
		tech = ship_def["tech"]
		repair_fees = self.get_repair_fees()
		cost_per_hull = repair_fees["hull"]*(tech+1)
		cost_per_armor = repair_fees["armor"]*(tech+1)
		repair_cost = hull*cost_per_hull + armor*cost_per_armor
		if pship["owner"] != cdata["name"]: raise error.User("You don't own that ship.")
		if hull > hull_lost: raise error.User("Can't repair more hull than is broken.")
		if armor > armor_lost: raise error.User("Can't repair more armor than is broken.")
		if repair_cost > cdata["credits"]: raise error.User("Not enough money to repair this much.")
		if hull < 0 or armor < 0: raise error.User("Can't repair a negative amount of hull or armor.")
		sstats["hull"]["current"] += hull
		sstats["armor"]["current"] += armor
		cdata["credits"] -= repair_cost
		stats.update_ship(pship)
		server.add_message("Successful repair.")
		pship.save()
		cdata.save()
	def repair_all(self,server,cdata):
		total_cost = 0
		pships = ship.character_ships(cdata["name"])
		repair_fees = self.get_repair_fees()
		for name,pship in pships.items():
			sstats = pship["stats"]
			ship_def = defs.ship_types[pship["type"]]
			tech = ship_def["tech"]
			hull_lost = sstats["hull"]["max"]-sstats["hull"]["current"]
			armor_lost = sstats["armor"]["max"]-sstats["armor"]["current"]
			cost = (hull_lost*repair_fees["hull"] + armor_lost*repair_fees["armor"])*(tech+1)
			total_cost += cost
		if total_cost > cdata["credits"]:
			raise error.User("Not enough credits to repair all ships.")
		for name,pship in pships.items():
			sstats = pship["stats"]
			sstats["hull"]["current"] = sstats["hull"]["max"]
			sstats["armor"]["current"] = sstats["armor"]["max"]
			pship.save()
		cdata["credits"] -= total_cost
		cdata.save()
	def get_repair_fees(self):
		return {
			"hull": 100,
			"armor": 20
		}
	def update_trade(self,cdata,items):
		if cdata["name"] != self["owner"]: raise error.User("You don't own this structure.")
		for item,data in items.items():
			item2 = defs.name_to_iname.get(item)
			if not item2 or (item2 not in defs.items and item2 not in defs.ship_types): raise error.User("Unknown item or ship: "+item)
			prev = self["market"]["prices"].get(item2,{})
			buy = data.get("buy",prev.get("buy",0))
			sell = data.get("sell", prev.get("sell", 0))
			limit_buy = data.get("limit_buy", prev.get("limit_buy", 0))
			limit_sell = data.get("limit_sell", prev.get("limit_sell", 0))
			if type(buy) is not int or type(sell) is not int: raise error.User("Only ints allowed for prices.")
			if buy < 0 or sell < 0:
				raise error.User("Prices must not be negative.")
			if buy == 0 and sell == 0:
				if item2 in self["market"]["prices"]:
					del self["market"]["prices"][item2]
			else:
				self["market"]["prices"][item2] = {
					"buy": buy,
					"sell": sell,
					"limit_buy": limit_buy,
					"limit_sell": limit_sell
				}
				if not limit_buy:
					del self["market"]["prices"][item2]["limit_buy"]
				if not limit_sell:
					del self["market"]["prices"][item2]["limit_sell"]
		self.save()
	def force_next_tick(self,user):
		props = user.get("props",{})
		admin = "admin" in props
		if not admin:
			raise error.User("Admin only action.")
		if "timestamp" not in self:
			self["timestamp"] = time.time()
		self["timestamp"] = self["timestamp"]-60*60*3
		self.tick()
	def get_credits(self):
		cdata = defs.characters[self["owner"]]
		props = self.get("props",{})
		if "credits_sync" in props:
			return cdata["credits"]
		else:
			return self["credits"]
	def add_credits(self,amount):
		cdata = defs.characters[self["owner"]]
		props = self.get("props",{})
		if "credits_sync" in props:
			cdata["credits"] += amount
			cdata.save()
		else:
			self["credits"] += amount
			self.save()
	def set_home(self,cdata):
		if self["name"] not in defs.predefined_structures:
			raise error.User("This place isn't a valid home location.")
		cdata["home"] = self["name"]
		cdata.save()
	def donate_credits(self,server,cdata,amount):
		if self["name"] not in defs.predefined_structures: raise user.Error("Can only donate to planets and starbases, not player stations.")
		if type(amount) != int: raise error.User("Amount must be an integer.")
		if cdata["credits"] < amount: raise error.User("Not enough credits.")
		if amount < 0: raise error.User("Amount can't be negative.")
		cdata["credits"] -= amount
		self.add_credits(amount)
		reputation.add_rep_flat(cdata,self,amount/20)
		server.add_message("Thank you for your contribution.")
	def pack_ship(self,server,cdata,target):
		tship = ship.get(target)
		room_left = cdata.get_room()-tship.get_room()
		shipdef = defs.ship_types[tship["type"]]
		room_need = shipdef["size_item"]
		tship_gear = tship.get_gear()
		
		if tship["owner"] != cdata["name"]: raise error.User("Can't pack a ship you don't own.")
		if not map.pos_equal(self["pos"],tship["pos"]): raise error.User("Target ship is not here.")
		if tship["name"] in cdata["ships"] and len(cdata["ships"]) < 2: raise error.User("Can't pack your last active ship.")
		if len(tship_gear): raise error.User("The ship must be entirely empty.")
		if room_need > room_left: raise error.User("Not enough room. Need "+str(room_need - room_left)+" more.")
		
		if tship["name"] in cdata["ships"]:
			cdata["ships"].remove(tship["name"])
		map.remove_ship(tship)
		del defs.character_ships[tship["owner"]][tship["name"]]
		cdata.get_items().add(tship["type"],1)
		cdata.save()
		#remove from cdata
		#remove from tile
		#remove from character ships
		#add to inventory
		#save active ship
	def update_limits(self,limits,cdata):
		if self["owner"] != cdata["name"]: raise error.User("Can't change limits in a station you don't own.")
		for k,v in limits.items():
			if k not in defs.items:
				raise error.User("Unknown item: "+k)
			if type(v) != int:
				raise error.User("Limits must be of type integer.")
			if v < 0:
				raise error.User("Limits must not be negative.")
		if "props" not in self:
			self["props"] = {}
		self["props"]["limits"] = limits
		self.save()
		#permission?
		#valid?
		#do it
	def loc(self):
		pos = self.get("pos")
		psystem = pos.get("system")
		px = pos.get("x")
		py = pos.get("y")
		return psystem,px,py
def get(system,x,y):
	tiles = map.otiles(system)
	tile = tiles.get(x,y)
	if "structure" in tile:
		return defs.structures[tile["structure"]]
def from_pos(pos):
	return get(pos["system"],pos["x"],pos["y"])
def build_station(item_name,cdata,system,px,py):
	pship = ship.get(cdata.ship())
	owner = cdata["name"]
	stiles = defs.systems[system]["tiles"]
	stile = stiles.get(px,py)
	otiles = defs.objmaps[system]["tiles"]
	otile = otiles.get(px,py)
	citems = cdata.get_items()
	kit_def = defs.station_kits.get(item_name)
	if not kit_def: raise error.User("Item "+item_name+" is not a station kit.")
	tile_limit = kit_def.get("tile")
	if "structure" in otile: raise error.User("Can't build. There is already a structure on this tile.")
	if tile_limit and stile["terrain"] not in tile_limit: raise error.User("This station type can't be built on this tile.")
	if not citems.get(item_name): raise error.User("You don't have a "+item_name+" in items.")
	kit_def = defs.station_kits[item_name]
	station = copy.deepcopy(defs.defaults["structure"])
	station["name"] = system+","+str(px)+","+str(py)
	station["type"] = "station"
	station["ship"] = kit_def["ship"]
	station["owner"] = owner
	station["pos"] = copy.deepcopy(pship["pos"])
	otile["structure"] = station["name"]
	otiles.set(px,py,otile)
	defs.structures[station["name"]] = station
	sys_structs = defs.system_data[system]["structures_by_owner"]
	if owner not in sys_structs:
		sys_structs[owner] = {}
	sys_structs[owner][station["name"]] = station
	if owner not in defs.character_structures:
		defs.character_structures[owner] = {}
	defs.character_structures[owner][station["name"]] = station["name"]
	stats.update_ship(station)
	station.get_room()
	citems.add(item_name,-1)
	station.tick()
	cdata.save()
	otiles.save()
	station.save()
def pick_up(pship,cdata):
	x = pship["pos"]["x"]
	y = pship["pos"]["y"]
	system = pship["pos"]["system"]
	otiles = map.otiles(system)
	otile = otiles.get(x,y)
	tstruct = get(system,x,y)
	if not tstruct: raise error.User("There is no station on this tile.")
	if tstruct["type"] != "station": raise error.User("Can't pick up a "+tstruct["type"])
	if tstruct["owner"] != pship["owner"]: raise error.User("Can't pick up a station you don't own.")
	if len(tstruct["items"]) or len(tstruct["gear"]): raise error.User("The station still contains items.")
	if tstruct["credits"] != 0: raise error.User("The station still contains credits.")
	owner = tstruct["owner"]
	kit_name = None
	for name,data in defs.station_kits.items():
		if data["ship"] == tstruct["ship"]:
			kit_name = name
			break
	kit_data = defs.items[kit_name]
	kit_size = kit_data["size"]
	if kit_size > cdata.get_room(): raise error.User("Not enough space, need at least "+str(kit_size)+" free space.")
	cdata.get_items().add(kit_name,1)
	del defs.structures[tstruct["name"]]
	del otile["structure"]
	sys_structs = defs.system_data[system]["structures_by_owner"]
	del sys_structs[owner][tstruct["name"]]
	if not len(sys_structs[owner]):
		del sys_structs[owner]
	del defs.character_structures[owner][tstruct["name"]]
	if not len(defs.character_structures[owner]):
		del defs.character_structures[owner]
	otiles.set(x,y,otile)
	otiles.save()
	cdata.get_room()
	cdata.save()
def give_credits(amount,cdata,tstructure):
	if cdata["name"] != tstructure["owner"]: raise error.User("You don't own this structure.")
	if cdata["credits"] < amount: raise error.User("Can't give more credits than you have.")
	if amount < 0: raise error.User("Amount must not be negative.")
	cdata["credits"] -= amount
	tstructure["credits"] += amount
	cdata.save()
	tstructure.save()
def take_credits(amount,cdata,tstructure):
	if cdata["name"] != tstructure["owner"]: raise error.User("You don't own this structure.")
	if tstructure["credits"] < amount: raise error.User("Can't take more credits than the structure has.")
	if amount < 0: raise error.User("Amount must not be negative.")
	tstructure["credits"] -= amount
	cdata["credits"] += amount
	cdata.save()
	tstructure.save()
def update_name(struct_id,name,cdata):
	tstruct = defs.structures.get(struct_id)
	if not tstruct: raise error.User("There is no structure called: "+struct_id)
	if tstruct["owner"] != cdata["name"]: raise error.User("You don't own this structure.")
	if not isinstance(name,str): raise error.User("The name must be a string.")
	if len(name) > 20: raise error.User("The name must be fewer than 20 characters/bytes.")
	allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567891-' "
	for c in name:
		if c not in allowed: raise error.User("Only ASCII, numbers, spacebar, -, ' are allowed in station name.")
	tstruct["custom_name"] = name
	tstruct.save()
def update_desc(struct_id,desc,cdata):
	tstruct = defs.structures.get(struct_id)
	if not tstruct: raise error.User("There is no structure called: "+struct_id)
	if tstruct["owner"] != cdata["name"]: raise error.User("You don't own this structure.")
	if not isinstance(desc,str): raise error.User("The description must be a string.")
	if len(desc) > 4000: raise error.User("The description must be fewer than 4000 characters/bytes.")
	forbidden = "<>"
	for c in desc:
		if c in forbidden: raise error.User("The following signs are forbidden in station descriptions: "+forbidden)
	tstruct["desc"] = desc
	tstruct.save()
def character_structures(name):
	if name not in defs.character_structures: return {}
	table = {}
	for name in defs.character_structures[name]:
		table[name] = defs.structures[name]
		table[name].tick()
	return table
from . import items,io,defs,factory,ship,error,map,types,gathering,build,tick,stats,reputation
