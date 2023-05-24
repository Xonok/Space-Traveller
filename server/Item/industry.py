from server import defs

def get_balance(entity):
	def add(table,item,amount):
		if item not in table:
			table[item] = 0
		table[item] += amount
	balance = {
		"output": {},
		"input": {}
	}
	eitems = entity.get_items()
	egear = entity.get_gear()
	eindustries = entity.get_industries()
	for name,amount in egear.items():
		efactory = defs.machines.get(name)
		if efactory:
			for item,amount in efactory.input.items():
				add(balance["input"],item,amount)
			for item,amount in efactory.output.items():
				add(balance["output"],item,amount)
	pop = entity.get_pop()//1000
	for name,amount in eindustries.items():
		eindustry = defs.industries.get(name)
		print(eindustry)
		if eindustry:
			for item,amount in eindustry["input"].items():
				add(balance["input"],item,round(amount*pop))
			for item,amount in eindustry["output"].items():
				add(balance["output"],item,round(amount*pop))
	return balance