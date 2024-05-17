from server import error,ship,defs,map,character,types,quest,stats,Name
from . import query
import copy

def transfer(cdata,data):
	potential(cdata,data)
	do_transfer(data)
def potential(cdata,data):
	check_params(data)
	check_armor(data)
	check_pos(data)
	check_owner(cdata,data)
	check_price(data)
	check_items(data)
	check_room(data)
	check_equip(data)
	check_slots(data)
	check_credits(data)
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
		self = get_entity(entry.get("self"))
		other = get_entity(entry.get("other"))
		sgear = entry.get("sgear")
		ogear = entry.get("ogear")
		source = None
		#figure out which ship/structure the items are being taken from
		#and whether it's from the gear part.
		if action == "give" and sgear:
			source = self
		elif action == "take" and ogear:
			source = other
		elif action == "sell" and sgear:
			source = self
		if not source: continue
		if source["stats"]["armor"]["current"] == source["stats"]["armor"]["max"]: continue
		for item in entry["items"].keys():
			if is_armor(item):
				raise error.User("Can't unequip armor item "+item+" because armor is not fully repaired.")
def check_pos(data):
	for entry in data:
		self = get_entity(entry["self"])
		other = get_entity(entry["other"])
		if not map.pos_equal(self["pos"],other["pos"]):
			raise error.User(Name.get(self)+" and "+Name.get(other)+" are not in the same place.")
def check_owner(cdata,data):
	name = cdata["name"]
	def check(*entities):
		for entity in entities:
			if entity["owner"] != name:
				raise error.User("Can't access "+Name.get(entity)+".")
	for entry in data:
		action = entry["action"]
		self = get_entity(entry["self"])
		other = get_entity(entry["other"])
		ogear = entry.get("ogear")
		match action:
			case "give" | "buy" | "buy-ship" | "sell":
				check(self)
			case "take":
				check(self,other)
		if ogear:
			check(other)
def check_price(data):
	for entry in data:
		action = entry["action"]
		if action in ["give","take"]: continue
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
	for entry in data:
		action = entry["action"]
		self = get_entity(entry["self"])
		other = get_entity(entry["other"])
		sgear = entry.get("sgear")
		ogear = entry.get("ogear")
		sname = self["name"]
		oname = other["name"]
		names[sname] = Name.get(self)
		names[oname] = Name.get(other)
		if sname not in items:
			items[sname] = types.copy(self.get_items(),"items_nosave")
		if oname not in items:
			items[oname] = types.copy(other.get_items(),"items_nosave")
		if sname not in gear:
			gear[sname] = types.copy(self.get_gear(),"items_nosave")
		if oname not in gear:
			gear[oname] = types.copy(other.get_gear(),"items_nosave")
		for item,amount in entry["items"].items():
			if amount < 0:
				raise error.User("Amount can't be negative: "+item)
			sinv = gear[sname] if sgear else items[sname]
			oinv = gear[oname] if ogear else items[oname]
			match action:
				case "give" | "sell":
					sinv.add(item,-amount)
					oinv.add(item,amount)
				case "take" | "buy":
					sinv.add(item,amount)
					oinv.add(item,-amount)
				case "buy-ship":
					oinv.add(item,-amount)
					if item not in defs.ship_types:
						raise error.User("Not a ship: "+item)
	for name,inv in items.items():
		for item,amount in inv.items():
			if amount < 0:
				raise error.User("Not enough "+item+" in "+names[name]+"(items)")
	for name,inv in gear.items():
		for item,amount in inv.items():
			if amount < 0:
				raise error.User("Not enough "+item+" in "+names[name]+"(gear)")
def check_room(data):
	room = {}
	names = {}
	for entry in data:
		action = entry["action"]
		self = get_entity(entry["self"])
		other = get_entity(entry["other"])
		sgear = entry.get("sgear")
		ogear = entry.get("ogear") #Need to consider expanders
		sname = self["name"]
		oname = other["name"]
		names[sname] = Name.get(self)
		names[oname] = Name.get(other)
		if sname not in room:
			room[sname] = self.get_room()
		if oname not in room:
			room[oname] = other.get_room()
		for item,amount in entry["items"].items():
			ssize = query.net_size(item) if sgear else query.size(item)
			osize = query.net_size(item) if ogear else query.size(item)
			match action:
				case "give" | "sell":
					room[sname] += ssize*amount
					room[oname] -= osize*amount
				case "take" | "buy":
					room[sname] -= ssize*amount
					room[oname] += osize*amount
				case "buy-ship":
					room[oname] += ssize*amount
	for name,left in room.items():
		if left < 0:
			raise error.User("Not enough room in "+names[name])
def check_equip(data):
	for entry in data:
		action = entry["action"]
		sgear = entry.get("sgear")
		ogear = entry.get("ogear")
		give = action in ["give"]
		take = action in ["take","buy","sell"]
		if not sgear and not ogear: continue
		for item,amount in entry["items"].items():
			itype = query.type(item)
			can_equip = query.equippable(item)
			if give and ogear or take and sgear:
				if not can_equip:
					raise error.User("Can't equip items of type "+itype)
def check_slots(data):
	slots = {}
	names = {}
	for entry in data:
		action = entry["action"]
		self = get_entity(entry["self"])
		other = get_entity(entry["other"])
		sgear = entry.get("sgear")
		ogear = entry.get("ogear")
		give = action in ["give"]
		take = action in ["take","buy","sell"]
		sname = self["name"]
		oname = other["name"]
		names[sname] = Name.get(self)
		names[oname] = Name.get(other)
		if sgear and sname not in slots:
			slots[sname] = get_slots(self)
		if ogear and oname not in slots:
			slots[oname] = get_slots(other)
		if not sgear and not ogear: continue
		if (not give and not take) or (give and take): raise Exception("Logic error in check_slots.")
		for item,amount in entry["items"].items():
			slot = query.slot(item)
			if slot not in slots[sname]:
				slots[sname][slot] = 0
			if slot not in slots[oname]:
				slots[oname][slot] = 0
			if give:
				if sgear:
					slots[sname][slot] += amount
				if ogear:
					slots[oname][slot] -= amount
			else:
				if sgear:
					slots[sname][slot] -= amount
				if ogear:
					slots[oname][slot] += amount
	for name,entry in slots.items():
		for slot,amount in entry.items():
			if amount < 0:
				raise error.User("Not enough "+slot+" slots in "+names[name])
def check_credits(data):
	credits = {}
	def owner(entity):
		if "credits" in entity:
			return entity
		else:
			return character.data(entity["owner"])
	for entry in data:
		action = entry["action"]
		if action in ["give","take"]: continue
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
def do_transfer(data):
	ships = {}
	for entry in data:
		action = entry["action"]
		self = get_entity(entry["self"])
		other = get_entity(entry["other"])
		sgear = entry.get("sgear")
		ogear = entry.get("ogear")
		sname = self["name"]
		oname = other["name"]
		sinv = self.get_gear() if sgear else self.get_items()
		oinv = other.get_gear() if ogear else other.get_items()
		if sname not in ships:
			ships[sname] = self
		if oname not in ships:
			ships[oname] = other
		for item,amount in entry["items"].items():
			match action:
				case "give":
					sinv.add(item,-amount)
					oinv.add(item,amount)
				case "take":
					sinv.add(item,amount)
					oinv.add(item,-amount)
				case "buy":
					price = get_price(other,item,"sell")
					sinv.add(item,amount)
					oinv.add(item,-amount)
					add_credits(self,-price*amount)
					add_credits(other,price*amount)
				case "buy-ship":
					price = get_price(other,item,"sell")
					oinv.add(item,-amount)
					add_credits(self,-price*amount)
					add_credits(other,price*amount)
					for i in range(amount):
						give_ship(self,item)
				case "sell":
					price = get_price(other,item,"buy")
					sinv.add(item,-amount)
					oinv.add(item,amount)
					add_credits(self,price*amount)
					add_credits(other,-price*amount)
					cdata = character.data(self["owner"])
					quest.update_items_sold(cdata,item,amount,other)
	for pship in ships.values():
		pship.get_room()
		stats.update_ship(pship)
#data
action_params = {
	"give": ["self","other","sgear","ogear","items"],
	"take": ["self","other","sgear","ogear","items"],
	"buy": ["self","other","sgear","items"],
	"buy-ship": ["self","other","items"],
	"sell": ["self","other","sgear","items"]
}
def get_entity(name):
	if name in defs.ships:
		return defs.ships[name]
	if name in defs.structures:
		return defs.structures[name]
	raise Exception("Unknown entity: "+name)
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
	owner = character.data(entity["owner"])
	new_ship = ship.new(ship_type,owner["name"])
	new_ship["pos"] = copy.deepcopy(entity["pos"])
	owner["ships"].append(new_ship["name"])
	ship.add_character_ship(new_ship)
	map.add_ship(new_ship,new_ship["pos"]["system"],new_ship["pos"]["x"],new_ship["pos"]["y"])
	owner.save()
def is_armor(item):
	return query.prop(item,"armor_max")