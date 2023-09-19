from server import defs

def tick(entity):
	industries = entity.get("industries")
	if not industries: return
	items = entity.get_items()
	
	industry_stats = {}
	for name,ind in defs.industries2.items():
		industry_stats["workers_max_"+name] = name
	ind_max = {}
	if entity["name"] in defs.assigned_industries:
		for name in defs.assigned_industries[entity["name"]]:
			ind_max[name] = 2000000000
	for item,amount in entity.get_gear().items():
		idata = defs.items[item]
		props = idata.get("props",{})
		for stat,ind_name in industry_stats.items():
			if stat in props:
				if ind_name not in ind_max:
					ind_max[ind_name] = 0
				ind_max[ind_name] += props[stat]*amount
	new_industries = []
	for ind in industries:
		if ind["name"] in ind_max:
			new_industries.append(ind)
	entity["industries"] = new_industries
	industries = new_industries

	tertiary_workers = 0
	for ind in industries:
		ind_def = defs.industries2[ind["name"]]
		type = ind_def["type"]
		if ind["workers"] < ind_def["min"]: 
			ind["workers"] = ind_def["min"]
		if type != "tertiary":
			tertiary_workers += ind["workers"]
	for ind in industries:
		ind_def = defs.industries2[ind["name"]]
		type = ind_def["type"]
		input = ind_def["input"]
		output = ind_def["output"]
		if ind["workers"] < ind_def["min"]: 
			ind["workers"] = ind_def["min"]
		workers = ind["workers"]/1000
		#Figure out supply ratio.
		#For primary industries, it's % of total demand value present.
		#For all others, it's minimum % of each demand value present.
		demand = tmult(input,workers)
		demand_value = value(demand)
		supply = get_supply(input,items)
		capped_supply = get_capped_supply(supply,demand)
		capped_supply_value = value(capped_supply)
		supply_value = value(supply)
		supply_ratio = get_supply_ratio(supply_value,demand_value)
		max_ticks = get_max_supply(supply,demand)
		if type == "secondary" or type == "special":
			supply_ratio = min(supply_ratio,max_ticks)
		capped_supply_ratio = get_supply_ratio(capped_supply_value,demand_value)
		produce = tmult(output,workers*capped_supply_ratio)
		spent = tmult(capped_supply,-1)
		ind["supply_ratio"] = float(supply_ratio)
		#Calculate growth before changing items.
		demand_10k = tmult(input,10)
		demand_10k_value = value(demand_10k)
		supply_ratio_10k = get_supply_ratio(supply_value,demand_10k_value)
		supply_ratio_10k = min(supply_ratio_10k,max_ticks)
		max_pop = 10000*supply_ratio_10k/8 #Max pop that could be maintained over a day.
		migration = round((max_pop-ind["workers"])/2000)
		if max_pop < ind["workers"]:
			migration -= round((ind["workers"]-max_pop)*0.1)+1
		growth = round(ind["workers"]*growth_factor(min(supply_ratio,20.),0.03,0.02))
		workers_new = round(ind["workers"]+growth+migration)
		workers_new = max(0,workers_new)
		ind["workers"] = workers_new
		ind["growth"] = growth
		ind["migration"] = migration
		if ind["workers"] < ind_def["min"]:
			ind["workers"] = ind_def["min"]
			ind["growth"] = 0
			ind["migration"] = 0
		if ind["workers"] > ind_max[ind["name"]]:
			ind["workers"] = ind_max[ind["name"]]
			ind["growth"] = 0
			ind["migration"] = 0
		#if entity["name"] == "Megrez,-4,-3":
		#if entity["name"] == "Megrez Prime":
		#	print(ind["name"],ind["workers"],supply_ratio,round(max_pop),spent,supply,produce)
		adds(items,produce)
		adds(items,spent)
		#
		if type == "tertiary":
			if "credits" in entity:
				entity["credits"] += int(capped_supply_value*1.2)
			else:
				owner = defs.characters[entity["owner"]]
				owner["credits"] += int(capped_supply_value*1.2)
	tertiary_workers = 0
	for ind in industries:
		ind_def = defs.industries2[ind["name"]]
		type = ind_def["type"]
		if type != "tertiary":
			tertiary_workers += ind["workers"]
	for ind in industries:
		ind_def = defs.industries2[ind["name"]]
		type = ind_def["type"]
		if type == "tertiary" and ind["workers"] > tertiary_workers:
			ind["workers"] = tertiary_workers
			ind["growth"] = 0
			ind["migration"] = 0
	#print(entity["industries"])
def check_construction_industry(entity):
	if "ship" not in entity or entity["type"] != "station": return
	if "industries" not in entity:
		entity["industries"] = []
	has_construction = False
	for data in entity["industries"]:
		if data["name"] == "construction":
			has_construction = True
	needs_construction = False
	for item in entity.get_gear().keys():
		idata = defs.items[item]
		props = idata.get("props",{})
		if "workers_max_construction" in props:
			needs_construction = True
	if not has_construction and needs_construction:
		entity["industries"].append({
			"name": "construction",
			"type": "special",
			"workers": 0,
			"growth": 0,
			"migration": 0,
			"supply_ratio": 0.0
		})
	if has_construction and not needs_construction:
		new_industries = []
		for ind in entity["industries"]:
			if ind["name"] != "construction":
				new_industries.append(ind)
		entity["industries"] = new_industries
def growth_factor(factor,growth,loss):
	if factor < 10:
		return float(-(10-factor)/10*loss)
	else:
		return float((factor-10)/10*growth)
def get_supply_ratio(supply_value,demand_value):
	if supply_value == 0:
		return 0.
	if demand_value == 0:
		return 100.
	else:
		return min(supply_value/demand_value,100.)
def get_capped_supply(supply,demand):
	result = {}
	for item,amount in demand.items():
		result[item] = min(amount,supply.get(item,0))
	return result
def get_max_supply(supply,demand):
	global_max = 100.0
	for item,amount in demand.items():
		supply_item = supply.get(item)
		if not supply_item:
			global_max = 0
		if amount == 0: continue
		local_max = supply_item/amount
		global_max = min(local_max,global_max)
	return global_max
def tmult(table,mult):
	result = {}
	for item,amount in table.items():
		result[item] = round(amount*mult)
	return result
def value(items):
	result = 0
	for name,amount in items.items():
		idata = defs.items[name]
		result += idata["price"]*amount
	return result
def get_supply(demand,items):
	result = {}
	for item,amount in demand.items():
		available = items.get(item)
		result[item] = available
	return result
def adds(items,to_add):
	for item,amount in to_add.items():
		items.add(item,amount)











