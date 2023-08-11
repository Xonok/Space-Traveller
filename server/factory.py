from . import defs,error

def tick_simple(stock,input,output):
	for item,amount in input.items():
		if not stock.get(item) >= amount:
			return
	for item,amount in input.items():
		stock.add(item,-amount)
	for item,amount in output.items():
		stock.add(item,amount)

def use_machine(name,stock):
	if name not in defs.machines: raise error.User("There is no machine called "+name)
	machine = defs.machines[name]
	input = machine["input"]
	output = machine["output"]
	tick_simple(stock,input,output)