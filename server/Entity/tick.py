import time,copy
from . import query
from server import defs,gathering,error,Item

def do_tick(entity):
	return
	ticks = query.ticks_since(entity["timestamp"],"long")
	ticks = max(ticks,0)
	entity["timestamp"] = time.time()
	sitems = entity.get_items()
	for i in range(ticks):
		#Harvesting and factories
		try:
			gathering.gather(entity)
		except error.User as e:
			pass
		run_factories(entity)
		#Colony stuff
		supply = get_supply(entity)
		demand = get_demand(entity)
		ratios = get_ratios(supply,demand)
		spent,produced = do_inds(entity,ratios)
		adds(spent,do_pops(entity,ratios))
		add_items(sitems,spent)
		add_items(sitems,produced)
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
	return new_table
def get_demand(entity):
	demand = {}
	pop = entity.get("pop")
	if pop:
		for name,data in pop.items():
			current = data["current"]/1000
			pop_def = defs.pops.get(name)
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
		ratios[item] = min(1,supply.get(item)/amount)
	return ratios
def do_inds(entity,ratios):
	pop = entity.get("pop")
	if not pop: return
	industries = entity.get("industries",[])
	sitems = entity.get_items()
	spent = {}
	produced = {}
	for name in industries:
		ind_def = defs.industries.get(name)
		scaling = ind_def["scaling"]
		data = entity.get("pop")["scaling"]
		current = pop[scaling]["current"]
		total_value = 0
		supplied_value = 0
		for item,amount in ind_def["input"].items():
			idata = Item.data(item)
			price = idata["price"]
			total_amount = round(amount*data["current"]/1000)
			supplied_amount = round(amount*data["current"]*ratios[item]/1000)
			total_value += total_amount*price
			supplied_value += supplied_amount*price
			add(spent,item,-round(supplied_amount))
		supply_factor = supplied_value/total_value
		for item,amount in ind_def["output"].items():
			produced_amount = round(amount*data["current"]*supply_factor/1000)
			add(produced,item,round(produced_amount))
	return spent,produced
def do_pops(entity,ratios):
	pop = entity.get("pop")
	if not pop: return
	spent = {}
	taxes = round(pop["wealth"]["current"])
	migration = pop["prestige"]["current"]
	#science too?
	#science = pop["science"]["current"]
	biotech = pop.get("biotech")
	bio_factor = 1
	if biotech:
		bio_factor = 1/(1+biotech["current"]/pop["workers"]["current"])
	
	food_factor = 0
	profit = 0
	for name,data in pop.items():
		pop_def = defs.pops.get(name)
		total_value = 0
		supplied_value = 0
		for item,amount in pop_def["input"].items():
			idata = Item.data(item)
			price = idata["price"]
			total_amount = round(amount*data["current"]/1000)
			supplied_amount = round(amount*data["current"]*get(ratios,item)/1000)
			total_value += total_amount*price
			supplied_value += supplied_amount*price
			add(spent,item,-round(supplied_amount*bio_factor))
		prev = data["current"]
		if total_value:
			supply_factor = supplied_value/total_value
			change_factor = 1+growth_factor(supply_factor,0.03,0.02)
			if name == "workers":
				food_factor = change_factor
			max_val = data["max"]
			if "limit" in data:
				max_val = min(max_val,data["limit"])
			data["current"] = bound(round(prev*change_factor),data["min"],max_val)
			profit += supplied_value
		data["change"] = data["current"]-prev
	if food_factor > 1:
		pop["workers"]["current"] += round(food_factor*migration)
	entity["credits"] += taxes+profit
	return spent
def get(table,key,default=0):
	if key not in table: return default
	return table[key]
def add_items(sitems,table):
	for item,amount in table.items():
		sitems.add(item,amount)
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