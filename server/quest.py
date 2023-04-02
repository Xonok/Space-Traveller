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
def objectives(cdata,qdata):
	array = []
	entry = cdata["quests"].get(qdata["name"],{})
	entry_props = entry.get("props",{})
	entry["props"] = entry_props
	outcome = qdata["outcomes"][0]
	objs = outcome["objectives"]
	pship = ship.get(cdata.ship())
	pitems = pship.get_items()
	tstruct = structure.from_pos(pship["pos"])
	if "location" in objs:
		loc = objs["location"]
		table = {}
		table["completed"] = False if loc != tstruct["name"] else True
		table["desc"] = "Be at "+objs["location"]
		table["status"] = "no" if loc != tstruct["name"] else "yes"
		array.append(table)
	if "items" in objs:
		for item,amount in objs["items"].items():
			table = {}
			table["completed"] = False
			table["desc"] = "Have "+str(amount)+" "+item
			done = pitems.get(item)
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
	qdata["outcome"] = qdata["outcomes"][0]
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
		#print(name,entry,qdata)
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
	print(cdata,predef)
	for name,entry in cdata["quests"].items():
		props = entry["props"]
		killed = props.get("targets_killed")
		if not killed: continue
		if predef["name"] in killed:
			killed[predef["name"]] += 1
	cdata.save()
def accept(self,data,cdata):
	name = data["quest-id"]
	if accepted(cdata,name): raise error.User("You have already accepted that quest.")
	if completed(cdata,name): raise error.User("You've already completed this quest.")
	if not visible(cdata,name) or not potential(cdata,name): raise error.User("The quest isn't available: "+name)
	entry = {
		"started": time.time(),
		"props": {}
	}
	cdata["quests"][name] = entry
	cdata.save()
	print(name)
def cancel(self,data,cdata):
	name = data["quest-id"]
	if not accepted(cdata,name): raise error.User("You don't have that quest.")
	del cdata["quests"][name]
	cdata.save()
def submit(self,data,cdata):
	name = data["quest-id"]
	qdata = get_data(name)
	if not accepted(cdata,name): raise error.User("You don't have that quest.")
	objs = objectives(cdata,qdata)
	for obj in objs:
		if not obj["completed"]:
			raise error.User("Quest objectives not completed.")
	outcome = qdata["outcomes"][0]
	pship = ship.get(cdata.ship())
	pitems = pship.get_items()
	oitems = outcome["objectives"].get("items",{})
	for item,amount in oitems.items():
		pitems.add(item,-amount)
	cdata["quests_completed"][name] = cdata["quests"][name]
	cdata["quests_completed"][name]["completed"] = time.time()
	del cdata["quests"][name]
	reward_credits = outcome["rewards"].get("credits",0)
	cdata["credits"] += reward_credits
	reward_items = outcome["rewards"].get("items",{})
	for item,amount in reward_items.items():
		pitems.add(item,amount)
	cdata.save()