from server import defs

def tick(entity):
	industries = entity.get("industries")
	if not industries: return
	items = entity.get_items()
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
		if entity["name"] == "Megrez Prime" and ind["name"] == "farming":
			print("workers:",ind["workers"],"produce:",produce,"output:",output,"capped supply ratio:",capped_supply_ratio,"worker ratio:",workers,1.)
		spent = tmult(capped_supply,-1)
		ind["supply_ratio"] = float(supply_ratio)
		#Calculate growth before changing items.
		demand_10k = tmult(input,10)
		demand_10k_value = value(demand_10k)
		supply_ratio_10k = get_supply_ratio(supply_value,demand_10k_value)
		supply_ratio_10k = min(supply_ratio_10k,max_ticks)
		max_pop = 10000*supply_ratio_10k/8 #Max pop that could be maintained over a day.
		migration = round((max_pop-ind["workers"])/1000)
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
		#if entity["name"] == "Megrez,-4,-3":
		#if entity["name"] == "Megrez Prime":
		#	print(ind["name"],ind["workers"],supply_ratio,round(max_pop),spent,supply,produce)
		adds(items,produce)
		adds(items,spent)
		#
		if type == "tertiary":
			if "credits" in entity:
				entity["credits"] += capped_supply_value
			else:
				owner = defs.characters[entity["owner"]]
				owner["credits"] += capped_supply_value
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











