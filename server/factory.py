import copy
from . import items,defs,error

def growth_factor(factor,growth,loss):
	if factor < 0.5:
		return -(0.5-factor)*2*loss
	else:
		return (factor-0.5)*2*growth
def tick_simple(stock,input,output,user,growth=0,loss=0):
	for item,amount in input.items():
		if not stock.get(item) >= amount:
			return
	for item,amount in input.items():
		stock.add(item,-amount)
	for item,amount in output.items():
		stock.add(item,amount)
def tick_proportional(stock,input,output,user,growth=0,loss=0):
	supply = items.Items()
	total_supply = 0
	total_demand = 0
	for item,amount in input.items():
		x = min(stock.get(item),amount)
		supply.add(item,x)
		total_demand += amount
		total_supply += x
	if total_demand == 0:
		ratio = 1
	else:
		ratio = total_supply/total_demand
	product = items.Items()
	total_product = 0
	for item,amount in output.items():
		x = round(amount*ratio)
		product.add(item,x)
		total_product += x
	if total_product:
		for item,amount in supply.items():
			stock.add(item,-amount)
		for item,amount in product.items():
			stock.add(item,amount)
	if "population" in user:
		user["population"]["workers"] = round(user["population"]["workers"]*(1+growth_factor(ratio,growth,loss)))
def tick_credits(stock,input,output,user,growth=0,loss=0):
	credits = 0
	for item,amount in input.items():
		supply = min(stock.get(item),amount)
		credits += supply*defs.items[item]["price"]
		stock.add(item,-supply)
	return credits
def tmult(table,mult):
	t2 = {}
	for item,amount in table.items():
		t2[item] = round(amount*mult)
	return t2

def use_industry(name,stock,workers,user):
	if not name in defs.industries: raise error.User("There is no industry called "+name)
	workers = workers/1000
	industry = defs.industries[name]
	func = globals()[industry["func"]]
	input = tmult(industry["input"],workers)
	output = tmult(industry["output"],workers) if "output" in industry else {}
	growth = industry["growth"] if "growth" in industry else 0
	loss = industry["loss"] if "loss" in industry else 0
	credits = func(stock,input,output,user,growth,loss)
	if credits:
		user["credits"] += credits
def use_machine(name,stock,user):
	if name not in defs.machines: raise error.User("There is no machine called "+name)
	machine = defs.machines[name]
	func = globals()[machine["func"]]
	input = machine["input"]
	output = machine["output"]
	credits = func(stock,input,output,user)
	if credits:
		user["credits"] += credits
def consume(change,stock,workers,user):
	workers = workers/1000
	industry = defs.industries["standard_drain"]
	func = globals()[industry["func"]]
	full_input = copy.deepcopy(industry["input"])
	input = {}
	for item,amount in full_input.items():
		if item not in change:
			input[item] = amount
	output = industry["output"]
	credits = func(stock,input,output,user)
	if credits:
		user["credits"] += credits