import time,copy
from . import query
from server import defs

def do_tick(entity):
	ticks = query.ticks_since(parent["timestamp"],"long")
	ticks = max(ticks,0)
	entity["timestamp"] = time.time()
	for i in range(ticks):
		#Harvesting and factories
		gathering.gather(entity)
		run_factories(entity)
		#Colony stuff
		supply = get_supply(entity)
		demand = get_demand(entity)
		ratios = get_ratios(supply,demand)
		do_inds(entity,ratios)
		do_pops(entity,ratios)
	entity.save()
	#supply,demand,ratios (pops,industries)
	#update pops - grow/shrink, bound
	#update items
def run_factories(entity):
	for item,amount in entity.get_gear().items():
		machine = defs.machines.get(item)
		if not machine: continue
		for i in range(amount):
			factory.use_machine(item,entity.get_items(),entity)
def get_supply(entity):
	return copy.deepcopy(entity.get_items())
def add(table,item,amount):
	if not amount: return
	if item not in table:
		table[item] = 0
	table[item] += amount
def adds(table,other_table):
	for item,amount in other_table.items():
		add(table,item,amount)
def tmult(table,factor):
	new_table = {}
	for item,amount in table.items():
		new_table[item] = round(amount*factor)
def get_demand(entity):
	demand = {}
	pop = entity.get("pop")
	if pop:
		for name,data in pop.items():
			current = data["current"]/1000
			pop_def = defs.pops.get(pop)
			adds(demand,tmult(pop_def["input"],current))
			adds(demand,tmult(pop_def["boost"],current))
		industries = entity.get("industries")
		if industries:
			for name in industries:
				ind_def = defs.industries.get(name)
				scaling = ind_def["scaling"]
				current = pop[scaling]["current"]/1000
				adds(demand,tmult(ind_def["input"],current))
	return demand
def get_ratios(supply,demand):
	ratios = {}
	for item,amount in demand.items():
		ratios[item] = supply.get(item,0)/amount
	return ratios
def do_inds(entity,ratios):
	pop = entity.get("pop")
	if not pop: return
	industries = entity.get("industries",[])
	sitems = entity.get_items()
	for name in industries:
		ind_def = defs.industries.get(name)
		scaling = ind_def["scaling"]
		current = pop[scaling]["current"]
		factory.use_industry(name,sitems,current,entity)
def do_pops(entity,ratios):
	pop = entity.get("pop")
	if not pop: return
	sitems = entity.get_items()
	taxes = round(pop["wealth"]["current"])
	migration = pop["prestige"]["current"]
	#science too?
	#science = pop["science"]["current"]
	biotech = pop.get("biotech")
	bio_factor = 1
	if biotech:
		bio_factor = 1/(1+biotech["current"]/pop["workers"]["current"])
	
	food_factor = 0
	for name,data in pop.items():
		pop_def = defs.pops.get(name)
		total_value = 0
		supplied_value = 0
		for item,amount in pop_def["input"].items():
			idata = Item.data(item)
			price = idata["price"]
			total_amount = round(amount*data["current"]/1000)
			supplied_amount = round(amount*data["current"]/1000*ratios[item])
			total_value += total_amount*price
			supplied_value += supplied_amount*price
			sitems.add(item,-round(supplied_amount*bio_factor))
		supply_factor = supplied_value/total_value
		change_factor = growth_factor(supply_factor,0.03,0.02)
		if name == "workers":
			food_factor = change_factor
		prev = data["current"]
		max_val = data["max"]
		if "limit" in data:
			max_val = min(max_val,data["limit"])
		data["current"] = bound(round(prev*change_factor),data["min"],max_val)
		data["change"] = data["current"]-data["prev"]
	if food_factor > 1:
		pop["workers"]["current"] += round(food_factor*migration)
	entity["credits"] += taxes
def growth_factor(factor,growth,loss):
	if loss == 0.0:
		return factor*growth
	if factor < 0.5:
		return -(0.5-factor)*2*loss
	else:
		return (factor-0.5)*2*growth
def bound(val,min_val,max_val):
	return max(min_val,min(val,max_val))

#Notes
#workers = ["food","water","energy"],["medicine"] #primary production
#industry = ["energy","ore","metals"],["microchips","robots"] #secondary production
#wealth = ["gas","gems"],["chemicals","plastics"] #tax income
#prestige = ["liquor"],["exotic_matter"] #migration
#science = ["scrap","optics"],["phase_dust"] #archaeology
#biotech = ["jello","bioframe"],["living_armor"] #decreases pop inputs
#Max one industry per pop property(workers,industry,wealth,etc...)

##TODO
#Update max_pop,min_pop to pop_max,pop_min in json
#Redo industries