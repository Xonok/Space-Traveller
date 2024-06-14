from . import defs,error,Item

def use_machine(name,stock,room,user=False):
	if name not in defs.machines:
		raise error.User("There is no machine called "+name)
	machine = defs.machines[name]
	input = machine["input"]
	output = machine["output"]
	input_room = 0
	output_room = 0
	for item,amount in input.items():
		size = Item.size(item)
		input_room += amount*size
	for item,amount in output.items():
		size = Item.size(item)
		output_room += amount*size
	if room+input_room-output_room < 0:
		if user:
			raise error.User("Not enough room to use factory.")
		else:
			return
	for item,amount in input.items():
		if not stock.get(item) >= amount:
			if user:
				raise error.User("Not enough "+defs.items[item]["name"])
			else:
				return
	for item,amount in input.items():
		stock.add(item,-amount)
	for item,amount in output.items():
		stock.add(item,amount)
	return True