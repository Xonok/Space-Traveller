from . import items,defs

def tick_simple(stock,input,output):
	for item,amount in input.items():
		if not stock.get(item) >= amount:
			return
	for item,amount in input.items():
		stock.add(item,-amount)
	for item,amount in output.items():
		stock.add(item,amount)
def tick_proportional(stock,input,output):
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
	if not total_product: return
	for item,amount in supply.items():
		stock.add(item,-amount)
	for item,amount in product.items():
		stock.add(item,amount)
def tick_credits(stock,input):
	credits = 0
	for item,amount in input.items():
		supply = min(stock.get(item),amount)
		credits += supply*defs.goods.get(item)
		stock.add(item,-supply)
	return credits
def tmult(table,mult):
	t2 = {}
	for item,amount in table.items():
		t2[item] = round(amount*mult)
	return t2

standard_drain = {
	"func": tick_credits,
	"input": {
		"gas": 2,
		"ore": 2,
		"metals": 0.5,
		"liquor": 1
	}	
}

def use_industry(name,stock,workers):
	if not name in defs.industries: return
	workers = workers/1000
	industry = defs.industries[name]
	func = globals()[industry["func"]]
	input = tmult(industry["input"],workers)
	output = tmult(industry["output"],workers)
	func(stock,input,output)
def use_machine(name,stock,user):
	if name not in defs.machines: return
	machine = defs.machines[name]
	func = globals()[machine["func"]]
	input = machine["input"]
	output = machine["output"]
	credits = func(stock,input,output)
	if credits:
		user["credits"] += credits
