import copy,time
from . import defs,ship,structure,error

def get_data(name):
	return defs.quests.get(name)
def accepted(cdata,name):
	qdata = get_data(name)
	return qdata["name"] in cdata["quests"]
def completed(cdata,name):
	qdata = get_data(name)
	if "quests_completed" not in cdata:
		cdata["quests_completed"] = {}
	return qdata["name"] in cdata["quests_completed"]
def potential(cdata,name):
	qdata = get_data(name)
	result = True
	if "quests_completed" not in cdata:
		cdata["quests_completed"] = {}
		cdata.save()
	if name in cdata["quests_completed"]: return False
	if "completed_quests" in qdata["potential"]:
		for q in qdata["potential"]["completed_quests"]:
			if q not in cdata["quests_completed"]:
				result = False
				break
	return result
def visible(cdata,name):
	return accepted(cdata,name) or potential(cdata,name)
def local(cdata,name):
	pship = ship.get(cdata.ship())
	tstructure = structure.from_pos(pship["pos"])
	names = tstructure.get("quests",[])
	return name in names
def get_outcome(cdata,qdata):
	name = qdata["name"]
	outcomes = qdata["outcomes"]
	if not accepted(cdata,name) and not completed(cdata,name):
		return outcomes[0]
	if completed(cdata,name):
		return outcomes[0]	#placeholder for now
	for outcome in outcomes:
		potentials = outcome.get("potential",{})
		before = potentials.get("before")
		quests_completed = potentials.get("quests_completed",[])
		started = cdata["quests"][name]["started"]
		moved = potentials.get("moved")
		if before and time.time() > started+before: continue
		if "moved" in potentials and moved != (cdata["quests"][name]["props"]["last_moved"] != cdata["last_moved"]): continue
		all_completed = True
		for qname in quests_completed:
			if not completed(cdata,qname):
				all_completed = False
				break
		if not all_completed: continue
		return outcome
	raise Exception("No possible outcome for quest: "+qdata["name"])
def objectives(cdata,qdata):
	array = []
	entry = cdata["quests"].get(qdata["name"],{})
	entry_props = entry.get("props",{})
	entry["props"] = entry_props
	outcome = get_outcome(cdata,qdata)
	objs = outcome["objectives"]
	pship = ship.get(cdata.ship())
	citems = cdata.get_items()
	tstruct = structure.from_pos(pship["pos"])
	if "potential" in outcome:
		if "before" in outcome["potential"]:
			total_s = outcome["potential"]["before"]
			h = ""
			m = ""
			s = ""
			if total_s >= 3600:
				h = str(total_s//3600)+"h"
				total_s -= (total_s//3600) * 3600
			if total_s >= 60:
				m = str(total_s//60)+"m"
				total_s -= (total_s//60) * 60
			if total_s >= 1:
				s = str(total_s)+"s"
			timestring = h+m+s
			table = {}
			table["completed"] = True
			table["desc"] = "Complete within "+timestring
			table["status"] = "possible"
			array.append(table)
	if "location" in objs:
		loc = objs["location"]
		table = {}
		table["desc"] = "Be at "+objs["location"]
		if tstruct and loc == tstruct["name"]:
			table["completed"] = True
			table["status"] = "yes"
		else:
			table["completed"] = False
			table["status"] = "no"
		array.append(table)
	if "items" in objs:
		for item,amount in objs["items"].items():
			table = {}
			table["completed"] = False
			table["desc"] = "Have "+str(amount)+" "+item
			done = citems.get(item)
			goal = amount
			table["status"] = str(done)+"/"+str(goal)
			if done >= goal:
				table["completed"] = True
			array.append(table)
	if "items_sold" in objs:
		sold_entry = entry_props.get("items_sold",{})
		entry_props["items_sold"] = sold_entry
		for obj in objs["items_sold"]:
			item_sold_entry = sold_entry.get(obj["item"],{})
			sold_entry[obj["item"]] = item_sold_entry
			loc = obj.get("location")
			table = {}
			table["completed"] = False
			table["desc"] = "Sell "+str(obj["amount"])+" "+obj["item"]
			if loc:
				table["desc"] += " at "+loc
				item_sold_entry["location"] = loc
			done = item_sold_entry.get("amount",0)
			item_sold_entry["amount"] = done
			goal = obj["amount"]
			table["status"] = str(done)+"/"+str(goal)
			if done >= goal:
				table["completed"] = True
			array.append(table)
	if "targets_killed" in objs:
		killed_entry = entry_props.get("targets_killed",{})
		entry_props["targets_killed"] = killed_entry
		for obj in objs["targets_killed"]:
			table = {}
			table["completed"] = False
			table["desc"] = "Kill "+str(obj["amount"])+" "+obj["name"]
			done = killed_entry.get(obj["name"],0)
			killed_entry[obj["name"]] = done
			goal = obj["amount"]
			table["status"] = str(done)+"/"+str(goal)
			if done >= goal:
				table["completed"] = True
			array.append(table)
	cdata.save()
	return array
def get_sanitized(name,cdata):
	qdata = copy.deepcopy(get_data(name))
	qdata["outcome"] = get_outcome(cdata,qdata)
	qdata["objectives"] = objectives(cdata,qdata)
	del qdata["outcomes"]
	del qdata["potential"]
	return qdata
def get_local(cdata):
	pship = ship.get(cdata.ship())
	tstruct = structure.from_pos(pship["pos"])
	names = tstruct.get("quests",[])
	data = {}
	for name in names:
		if visible(cdata,name):
			qdata = get_sanitized(name,cdata)
			data[qdata["name"]] = qdata
	for name in cdata["quests"].keys():
		qdata = get_sanitized(name,cdata)
		outcome = qdata["outcome"]
		objectives = outcome["objectives"]
		location = objectives.get("location")
		if location and location == tstruct["name"]:
			data[qdata["name"]] = qdata
	return data
def get_character(cdata):
	entries = cdata["quests"]
	table = {}
	for name,entry in entries.items():
		qdata = get_sanitized(name,cdata)
		table[name] = qdata
	return table
def update_items_sold(cdata,item,amount,tstruct):
	for name,entry in cdata["quests"].items():
		props = entry["props"]
		items_sold = props.get("items_sold",{})
		this_item = items_sold.get(item)
		if this_item:
			loc = this_item.get("location")
			if loc and tstruct["name"] != loc: continue
			this_item["amount"] += amount
	cdata.save()
def update_targets_killed(cdata,predef):
	for name,entry in cdata["quests"].items():
		props = entry["props"]
		killed = props.get("targets_killed")
		if not killed: continue
		if predef["name"] in killed:
			killed[predef["name"]] += 1
	cdata.save()
def accept(self,quest_id,cdata):
	if accepted(cdata,quest_id): raise error.User("You have already accepted that quest.")
	if completed(cdata,quest_id): raise error.User("You've already completed this quest.")
	if not visible(cdata,quest_id) or not potential(cdata,quest_id): raise error.User("The quest isn't available: "+quest_id)
	entry = {
		"started": time.time(),
		"props": {}
	}
	#if first outcome depends on having moved, note down the current timestamp in the entry
	qdata = get_data(quest_id)
	outcome = get_outcome(cdata,qdata)
	qpotential = outcome.get("potential",{})
	if "moved" in qpotential:
		entry["props"]["last_moved"] = cdata["last_moved"]
	cdata["quests"][quest_id] = entry
	cdata.save()
def cancel(self,quest_id,cdata):
	if not accepted(cdata,quest_id): raise error.User("You don't have that quest.")
	del cdata["quests"][quest_id]
	cdata.save()
def submit(self,quest_id,cdata):
	qdata = get_data(quest_id)
	if not accepted(cdata,quest_id): raise error.User("You don't have that quest.")
	objs = objectives(cdata,qdata)
	for obj in objs:
		if not obj["completed"]:
			raise error.User("Quest objectives not completed.")
	outcome = get_outcome(cdata,qdata)
	pship = ship.get(cdata.ship())
	citems = cdata.get_items()
	oitems = outcome["objectives"].get("items",{})
	for item,amount in oitems.items():
		citems.add(item,-amount)
	cdata["quests_completed"][quest_id] = cdata["quests"][quest_id]
	cdata["quests_completed"][quest_id]["completed"] = time.time()
	del cdata["quests"][quest_id]
	reward_credits = outcome["rewards"].get("credits",0)
	cdata["credits"] += reward_credits
	reward_items = outcome["rewards"].get("items",{})
	for item,amount in reward_items.items():
		citems.add(item,amount)
	cdata.save()
	end_text = outcome["end_text"]
	return end_text