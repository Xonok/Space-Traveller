from server import error,ship,defs,map,character,types,quest,stats,Name,reputation,Skill
from . import query
import copy,math

def transfer(cdata,data,**kwargs):
	potential(cdata,data,**kwargs)
	xp = do_transfer(data)
	if xp and "server" in kwargs:
		xp = min(xp,510)
		Skill.gain_xp_flat(cdata,xp)
		kwargs["server"].add_message("Gained "+str(xp)+" xp.")
def potential(cdata,data,**kwargs):
	check_params(data)
	check_armor(data)
	if "ignore_pos" not in kwargs:
		check_pos(data)
	check_owner(cdata,data)
	check_entity(data)
	check_price(data)
	check_items(data)
	check_room(data)
	check_equip(data)
	check_slots(data)
	check_credits(data)
	check_limits(data)
#checks
def check_params(data):
	for entry in data:
		action = entry["action"]
		for param in action_params[action]:
			if param not in entry:
				raise error.User("Missing required \""+param+"\"")
		for param in entry:
			if param != "action" and param not in action_params[action]:
				raise error.User("Unnecessary param: "+param)
def check_armor(data):
	for entry in data:
		action = entry.get("action")
		if action != "unequip": continue
		other = get_entity(entry.get("other"))
		if other["stats"]["armor"]["current"] == other["stats"]["armor"]["max"]: continue
		for item in entry["items"].keys():
			if is_armor(item):
				raise error.User("Can't unequip armor item "+item+" because armor is not fully repaired.")
def check_pos(data):
	for entry in data:
		self = get_entity(entry["self"])
		other = get_entity(entry["other"])
		self_pos = get_pos(self)
		other_pos = get_pos(other)
		if not map.pos_equal(self_pos,other_pos):
			raise error.User(Name.get(self)+" and "+Name.get(other)+" are not in the same place.")
def check_owner(cdata,data):
	for entry in data:
		action = entry["action"]
		self = get_entity(entry["self"])
		other = get_entity(entry["other"])
		self_owner = self["owner"] if "owner" in self else self["name"]
		other_owner = other["owner"] if "owner" in other else other["name"]
		if self_owner != other_owner and action in ["take","equip","unequip"]:
			raise error.User("Can't use that action on entities you don't own: "+action)
		if self_owner != cdata["name"]:
			raise error.User("Self must be your character or something you own.")
def check_entity(data):
	for entry in data:
		action = entry["action"]
		stype = entity_type(entry["self"])
		otype = entity_type(entry["other"])
		if action in ["give","take"]:
			if stype == "ship" or otype == "ship":
				raise error.User("Give and take actions must not be within ships.")
		if action in ["sell","buy"]:
			if stype == "ship":
				raise error.User("Self must not be a ship.("+action+")")
			if otype != "structure":
				raise error.User("Other must be a structure.("+action+")")
		if action in["equip","unequip"]:
			if stype == "ship":
				raise error.User("Self must not be a ship.("+action+")")
			if otype == "character":
				raise error.User("Characters can't equip or unequip items.")
def check_price(data):
	for entry in data:
		action = entry["action"]
		if action in ["give","take","equip","unequip"]: continue
		other = get_entity(entry["other"])
		for item,amount in entry["items"].items():
			match action:
				case "buy" | "buy-ship":
					price = get_price(other,item,"sell")
					if not price:
						raise error.User("Item "+item+" can't be bought from "+Name.get(other))
				case "sell":
					price = get_price(other,item,"buy")
					if not price:
						raise error.User("Item "+item+" can't be sold to "+Name.get(other))
			if price < 0:
				raise error.User("Price must not be negative.")
def check_items(data):
	items = {}
	gear = {}
	names = {}
	min_equipped = {}
	for entry in data:
		action = entry["action"]
		self = get_entity(entry["self"])
		other = get_entity(entry["other"])
		sname = self["name"]
		oname = other["name"]
		names[sname] = Name.get(self)
		names[oname] = Name.get(other)
		gear_action = action == "equip" or action == "unequip"
		otype = entity_type(entry["other"])
		if action == "unequip" and otype == "ship":	
			min_equipped[oname] = {}
			factories = other["stats"]["factories"]
			for item,data in factories.items():
				idata = defs.items[item]
				props = idata.get("props",{})
				max = props.get("factory_max",4)*8
				min_equipped[oname][item] = math.ceil((data["max"]-data["cur"])/max)
		if sname not in items:
			items[sname] = types.copy(self.get_items(),"items_nosave")
		if oname not in items and (oname in defs.structures or oname in defs.characters):
			items[oname] = types.copy(other.get_items(),"items_nosave")
		if oname not in gear and gear_action:
			gear[oname] = types.copy(other.get_gear(),"items_nosave")
		for item,amount in entry["items"].items():
			if amount < 0:
				raise error.User("Amount can't be negative: "+item)
			match action:
				case "give" | "sell":
					items[sname].add(item,-amount)
					items[oname].add(item,amount)
				case "take" | "buy":
					items[sname].add(item,amount)
					items[oname].add(item,-amount)
				case "buy-ship":
					items[oname].add(item,-amount)
					if item not in defs.ship_types:
						raise error.User("Not a ship: "+item)
				case "equip":
					items[sname].add(item,-amount)
					gear[oname].add(item,amount)
				case "unequip":
					items[sname].add(item,amount)
					gear[oname].add(item,-amount)
	for name,inv in items.items():
		for item,amount in inv.items():
			if amount < 0:
				raise error.User("Not enough "+item+" in "+names[name]+"(items)")
	for name,inv in gear.items():
		for item,amount in inv.items():
			if amount < 0:
				raise error.User("Not enough "+item+" in "+names[name]+"(gear)")
	for name,inv in min_equipped.items():
		for item,amount in inv.items():
			gear_items = gear.get(name,{})
			item_amount = gear_items.get(item) #items_nosave defaults to 0
			if item_amount < amount:
				idata = defs.items[item]
				raise error.User("At least "+str(min_equipped[name][item])+" "+idata["name"]+" must remain equipped.")
def check_room(data):
	room = {}
	names = {}
	for entry in data:
		action = entry["action"]
		self = get_entity(entry["self"])
		other = get_entity(entry["other"])
		sname = self["name"]
		oname = other["name"]
		stype = entity_type(sname)
		names[sname] = Name.get(self)
		names[oname] = Name.get(other)
		if sname not in room:
			room[sname] = self.get_room()
		if oname not in room:
			room[oname] = other.get_room()
		for item,amount in entry["items"].items():
			ssize = query.net_size(item) if action == "unequip" else query.size(item)
			osize = query.net_size(item) if action == "equip" else query.size(item)
			match action:
				case "give" | "sell":
					room[sname] += ssize*amount
					room[oname] -= osize*amount
				case "take" | "buy":
					room[sname] -= ssize*amount
					room[oname] += osize*amount
				case "buy-ship":
					room[oname] += ssize*amount
				case "equip":
					room[oname] -= osize*amount
				case "unequip":
					if stype == "character" and oname not in self["ships"]:
						room[sname] -= ssize*amount
					room[oname] += osize*amount
	for name,left in room.items():
		entity = get_entity(name)
		cur_room = entity.get_room()
		if left < 0 and left < cur_room:
			raise error.User("Not enough room in "+names[name])
def check_equip(data):
	for entry in data:
		action = entry["action"]
		if action != "equip" and action != "unequip": continue
		for item,amount in entry["items"].items():
			itype = query.type(item)
			can_equip = query.equipable(item)
			if not can_equip:
				raise error.User("Can't equip items of type "+itype)
def check_slots(data):
	slots = {}
	names = {}
	for entry in data:
		action = entry["action"]
		if action != "equip" and action != "unequip": continue
		self = get_entity(entry["self"])
		other = get_entity(entry["other"])
		sname = self["name"]
		oname = other["name"]
		names[sname] = Name.get(self)
		names[oname] = Name.get(other)
		if oname not in slots:
			slots[oname] = get_slots(other)
		for item,amount in entry["items"].items():
			slot = query.slot(item)
			if slot not in slots[oname]:
				slots[oname][slot] = 0
			if action == "equip":
				slots[oname][slot] -= amount
			if action == "unequip":
				slots[oname][slot] += amount
	for name,entry in slots.items():
		for slot,amount in entry.items():
			if amount < 0:
				raise error.User("Not enough "+slot+" slots in "+names[name])
def check_credits(data):
	credits = {}
	def owner(entity):
		if "credits" in entity: return entity
		return defs.character[entity["owner"]]
	for entry in data:
		action = entry["action"]
		if action in ["give","take","equip","unequip"]: continue
		self = get_entity(entry["self"])
		other = get_entity(entry["other"])
		sowner = owner(self)
		oowner = owner(other)
		sname = sowner["name"]
		oname = oowner["name"]
		if sname not in credits: credits[sname] = sowner["credits"]
		if oname not in credits: credits[oname] = oowner["credits"]
		for item,amount in entry["items"].items():
			match action:
				case "buy" | "buy-ship":
					price = get_price(other,item,"sell")
					credits[sname] -= price*amount
					credits[oname] += price*amount
				case "sell":
					price = get_price(other,item,"buy")
					credits[sname] += price*amount
					credits[oname] -= price*amount
	for name,amount in credits.items():
		if amount < 0:
			raise error.User(name+" doesn't have enough credits.")
def check_limits(data):
	items = {}
	for entry in data:
		action = entry["action"]
		if action in ["give","take","equip","unequip"]: continue
		self = get_entity(entry["self"])
		other = get_entity(entry["other"])
		if entry["self"] not in items:
			items[entry["self"]] = types.copy(self.get_items(),"items_nosave")
		if entry["other"] not in items:
			items[entry["other"]] = types.copy(other.get_items(),"items_nosave")
		self_entry = items[entry["self"]]
		other_entry = items[entry["other"]]
		self_prices = {}
		other_prices = {}
		if "market" not in self and "market" not in other: continue
		if "market" in self:
			self_prices = self.get_prices()
		if "market" in other:
			other_prices = other.get_prices()
		for item,amount in entry["items"].items():
			if item not in self_prices and item not in other_prices: continue
			limit_buy = 0
			limit_sell = 0
			match action:
				case "buy" | "buy-ship":
					if (item in self_prices and "limit_buy" in self_prices[item]) or (item in other_prices and "limit_sell" in other_prices[item]):
						if item not in self_entry:
							self_entry[item] = 0
						self_entry[item] += amount
						other_entry[item] -= amount
				case "sell":
					if (item in self_prices and "limit_sell" in self_prices[item]) or (item in other_prices and "limit_buy" in other_prices[item]):
						if item not in other_entry:
							other_entry[item] = 0
						self_entry[item] -= amount
						other_entry[item] += amount
	for name,inv in items.items():
		entity = get_entity(name)
		items2 = entity.get_items()
		if "market" not in entity: continue
		prices = entity.get_prices()
		for item,amount in inv.items():
			if item not in prices: continue
			limit_buy = prices[item].get("limit_buy")
			limit_sell = prices[item].get("limit_sell")
			if limit_buy is not None:
				if amount > items2.get(item) and amount > limit_buy:
					raise error.User(Name.get(entity)+" won't buy this much "+defs.items[item]["name"])
			if limit_sell is not None:
				if amount < items2.get(item) and amount < limit_sell:
					raise error.User(Name.get(entity)+" won't sell this much "+defs.items[item]["name"])
def do_transfer(data):
	entities = {}
	xp = 0
	for entry in data:
		action = entry["action"]
		self = get_entity(entry["self"])
		other = get_entity(entry["other"])
		if self["name"] not in entities:
			entities[self["name"]] = self
		if other["name"] not in entities:
			entities[other["name"]] = other
		for item,amount in entry["items"].items():
			match action:
				case "give":
					self["items"].add(item,-amount)
					other["items"].add(item,amount)
				case "take":
					self["items"].add(item,amount)
					other["items"].add(item,-amount)
				case "buy":
					price = get_price(other,item,"sell")
					self["items"].add(item,amount)
					other["items"].add(item,-amount)
					add_credits(self,-price*amount)
					add_credits(other,price*amount)
					cdata = get_owner(self)
					xp += reputation.add_rep(cdata,other,item,-amount)
				case "buy-ship":
					price = get_price(other,item,"sell")
					other["items"].add(item,-amount)
					add_credits(self,-price*amount)
					add_credits(other,price*amount)
					for i in range(amount):
						give_ship(self,item)
				case "sell":
					price = get_price(other,item,"buy")
					self["items"].add(item,-amount)
					other["items"].add(item,amount)
					add_credits(self,price*amount)
					add_credits(other,-price*amount)
					cdata = get_owner(self)
					quest.update_items_sold(cdata,item,amount,other)
					xp += reputation.add_rep(cdata,other,item,amount)
				case "equip":
					self["items"].add(item,-amount)
					other["gear"].add(item,amount)
				case "unequip":
					self["items"].add(item,amount)
					other["gear"].add(item,-amount)
	for name,entity in entities.items():
		entity.get_room() #necessary, but only because equipping stuff affects max room.
		if name in defs.ships or name in defs.structures:
			stats.update_ship(entity)
	return xp
#data
action_params = {
	"give": ["self","other","items"],
	"take": ["self","other","items"],
	"buy": ["self","other","items"],
	"buy-ship": ["self","other","items"],
	"sell": ["self","other","items"],
	"equip": ["self","other","items"],
	"unequip": ["self","other","items"]
	#the whole equip/unequip thing needs to be turned into a separate action
	#that way, no sgear/ogear anywhere else
	#self and other should support characters and structures, but not ships
	#recheck everything
}
def get_entity(name):
	if name in defs.characters:
		return defs.characters[name]
	if name in defs.ships:
		return defs.ships[name]
	if name in defs.structures:
		return defs.structures[name]
	raise Exception("Unknown entity: "+name)
def get_pos(entity):
	if "ships" in entity:
		return get_entity(entity["ships"][0])["pos"]
	return entity["pos"]
def get_price(entity,item,action):
	prices = entity.get_prices()
	entry = prices.get(item)
	if entry:
		return entry[action]
	return 0
def get_slots(entity):
	shiptype = get_shiptype(entity)
	slots = copy.deepcopy(shiptype["slots"])
	for name,amount in slots.items():
		if amount == -1:
			slots[name] = 999
	for item,amount in entity.get_gear().items():
		slot = query.slot(item)
		slots[slot] -= amount
	return slots
def get_shiptype(entity):
	if "ship" in entity:
		return defs.ship_types[entity["ship"]]
	elif "type" in entity:
		return defs.ship_types[entity["type"]]
	else:
		raise Exception("Unknown shiptype for entity "+Name.get(entity))
def add_credits(entity,amount):
	if "credits" in entity:
		entity["credits"] += amount
	else:
		owner = character.data(entity["owner"])
		owner["credits"] += amount
def give_ship(entity,ship_type):
	if "owner" in entity:
		owner = defs.characters[entity["owner"]]
	owner = entity
	pos = defs.ships[owner["ships"][0]]["pos"]
	new_ship = ship.new(ship_type,owner["name"])
	new_ship["pos"] = copy.deepcopy(pos)
	owner["ships"].append(new_ship["name"])
	ship.add_character_ship(new_ship)
	map.add_ship(new_ship,new_ship["pos"]["system"],new_ship["pos"]["x"],new_ship["pos"]["y"])
	new_ship.init()
	owner.save()
def is_armor(item):
	return query.prop(item,"armor_max")
def get_owner(entity):
	if entity["name"] in defs.characters:
		return entity
	return defs.characters[entity["owner"]]
def entity_type(name):
	if name in defs.structures:
		return "structure"
	if name in defs.characters:
		return "character"
	if name in defs.ships:
		return "ship"
	raise Exception("Item.transfer: Unknown entity type.")