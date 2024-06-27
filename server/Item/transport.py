#TODO
#Also update stats when gear changes? LATER


#API
def tick(entity):
	check(entity)
	update_stats(entity)
	do_tick(entity)
def update_actions(entity,entries,next_action):
	#need to check owner
	update_stats(entity)
	tp = entity["transport"]
	max_power = tp["capacity"]+tp["power"]
	for e in entries:
		error_keys = []
		for k in e.keys():
			if k not in ["target","action","item","amount","limit","dist","cost","error"]:
				error_keys.append(k)
		if len(error_keys):
			raise error.User("Unnecessary keys: "+",".join(error_keys))
		target = defs.structures.get(e["target"])
		if not e["target"]:
			e["error"] = "No target."
			continue
		if e["target"] == entity["name"]:
			e["error"] = "Source and target are the same."
			continue
		if e["target"] not in defs.structures:
			e["error"] = "Target doesn't exist."
			continue
		if target["pos"]["system"] != entity["pos"]["system"]:
			e["error"] = "Target in a different system."
			continue
		if not e["action"]:
			e["error"] = "No action."
			continue
		if(e["action"] == "give" or e["action"] == "take") and entity["owner"] != target["owner"]:
			e["error"] = "Can only give or take if you own the target."
			continue
		if not e["item"]:
			e["error"] = "No item name."
			continue
		if e["item"] not in defs.name_to_iname:
			e["error"] = "Unknown item."
			continue
		if e["amount"] <= 0:
			e["error"] = "Amount can't be 0 or negative."
			continue
		pos_e = entity["pos"]
		pos_t = target["pos"]
		e["dist"] = dist(pos_e["x"],pos_e["y"],pos_t["x"],pos_t["y"])
		e["cost"] = e["dist"]*2 + e["amount"]
		if e["cost"] > max_power:
			e["error"] = "There will never be enough power."
			continue
		
		if "error" in e:
			del e["error"]
	if next_action >= len(entries):
		next_action = 0
	tp["next_action"] = next_action
	tp["entries"] = entries
	entity.save()
#INTERNAL
def check(entity):
	if "transport" not in entity:
		entity["transport"] = {
			"capacity": 0,
			"power": 0,
			"stored_power": 0,
			"next_action": 0,
			"entries": []
		}
def update_stats(entity):
	ship_type = entity.get("ship",entity["type"])
	type_def = defs.ship_types[ship_type]
	props = type_def.get("props",{})
	capacity_mod = props.get("transport_capacity_mod",1)
	power_mod = props.get("transport_power_mod",1)
	capacity = 0
	power = 0
	for item,amount in entity["inventory"]["gear"].items():
		idata = defs.items[item]
		props = idata.get("props",{})
		if "transport_capacity" in props:
			capacity += props["transport_capacity"]*amount
		if "transport_power" in props:
			power += props["transport_power"]*amount
	capacity = int(capacity*capacity_mod)
	power = int(power*power_mod)
	entity["transport"]["capacity"] = capacity
	entity["transport"]["power"] = power
	if entity["transport"]["stored_power"] > capacity:
		entity["transport"]["stored_power"] = capacity
ticking_entities = {}
def do_tick(entity):
	tp = entity["transport"]
	if not len(tp["entries"]): return
	cdata = defs.characters[entity["owner"]]
	power_available = tp["stored_power"] + tp["power"]
	credits_available = entity.get_credits()
	entries_len = len(tp["entries"])
	finished = {}
	finished_len = 0
	print("starting transport tick: "+entity["name"])
	idx = tp["next_action"]
	for entry in tp["entries"]:
		target = entry["target"]
		if target in defs.structures:
			if target in ticking_entities: continue
			ticking_entities[target] = True
			target_entity = defs.structures[target]
			target_entity.tick()
			del ticking_entities[target]
	while power_available:
		if idx >= entries_len:
			print("loop back")
			idx = 0
		if finished_len >= entries_len:
			print("break")
			break
		if idx in finished:
			print("skip finished("+str(idx)+")")
			idx += 1
			continue
		entry = tp["entries"][idx]
		if "error" in entry:
			print("skip error("+str(idx)+")")
			finished[idx] = True
			finished_len += 1
			continue
		target = entry["target"]
		action = entry["action"]
		item = defs.name_to_iname[entry["item"]]
		print(item)
		amount = entry["amount"]
		cost = entry["cost"]
		limit = entry["limit"]
		self_room = entity.get_room()
		self_items = entity.get_items()
		target_entity = defs.structures[target]
		target_room = target_entity.get_room()
		target_items = target_entity.get_items()
		item_size = query.size(item)
		space_needed = item_size*amount
		limit_breached = False
		if action == "take" or action == "buy":
			if limit != 0 and self_items.get(item)+amount > limit:
				limit_breached = True
		if action == "give" or action == "sell":
			if self_items.get(item)-amount < limit:
				limit_breached = True
		if cost > power_available or cost > credits_available:
			print("finish, no power or credits")
			finished[idx] = True
			finished_len += 1
			continue
		elif limit_breached:
			print("finish, limit")
			finished[idx] = True
			finished_len += 1
			continue
		else:
			if action == "take" or action == "buy":
				if target_items.get(item) < amount:
					print("target lacking item")
					finished[idx] = True
					finished_len += 1
					continue
				if self_room < space_needed:
					print("self lacking space")
					finished[idx] = True
					finished_len += 1
					continue
			if action == "give" or action == "sell":
				if self_items.get(item) < amount:
					print("self lacking item")
					finished[idx] = True
					finished_len += 1
					continue
				if target_room < space_needed:
					print("target lacking space")
					finished[idx] = True
					finished_len += 1
					continue
			if action == "buy" and item not in target_entity.get_prices():
				print("target not selling "+item)
				finished[idx] = True
				finished_len += 1
				continue
			if action == "sell" and item not in target_entity.get_prices():
				print("target not buying "+item)
				finished[idx] = True
				finished_len += 1
				continue
			data = [
				{
					"action": action,
					"self": entity["name"],
					"other": target,
					"sgear": False,
					"items": {
						item: amount
					}
				}
			]
			if action == "give" or action == "take":
				data[0]["ogear"] = False
			Item.transfer(cdata,data,ignore_pos=True)
			credits_available -= cost
			power_available -= cost
			entity.add_credits(-cost)
		idx += 1
	tp["next_action"] = idx
	tp["stored_power"] = min(power_available,tp["capacity"])
	#credit cost is power cost
	#loop through operations until power runs out
	#... or have considered and rejected every action in the list
	#maybe actions can be tagged as "max once per tick" LATER
def dist(x1,y1,x2,y2):
	dist_x = x2 - x1
	dist_y = y2 - y1
	dist = round((dist_x**2+dist_y**2)**0.5)
	return dist

from server import defs,Item,error
from . import query