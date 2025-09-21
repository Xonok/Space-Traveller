from server import defs,error,func
# *Allsüsteemi kaustast võib vaja olla query.py, juhul kui sa osa koodi sinna lükkad.

def tick(entity):
	stats = entity["stats"]
	stats["recycle"]["current"] += stats["recycle"]["reg"]
	if stats["recycle"]["current"] > stats["recycle"]["max"]:
		stats["recycle"]["current"] = stats["recycle"]["max"]

def recycle(cdata,struct_id,items,energy,exomatter):
	tstruct=defs.structures.get(struct_id)
	if not tstruct:
		raise error.User("No such structure")
	unrecyclable = ["energy","exotic_matter","antimatter"]
	boost = 0
	price = 0
	max_return={}
	player_loot={}
	c_items=cdata.get_items()
 	
	if energy:
		boost+=0.3
	if exomatter:
		boost+=0.3
		# calculating the price, whether the user has enough of items, if they are recyclable
	for iname,amount in items.items():
		#Kui recyclida laeva,siis läheb katki. See teeks korda:
		#Item.query.data(iname)
		idata = Item.query.data(iname)
		price += int(idata["price"] * amount)
		c_amount = c_items.get(iname)
		if c_amount < amount:
			raise error.User("Not enough " + idata["name"])
		if not defs.blueprint_of[iname]:
			raise error.User("Not recyclable: " + idata["name"])
		max_return[amount] = defs.blueprint_of[iname]["inputs"]
	
	if tstruct["stats"]["recycle"]["current"] < price:
		raise error.User("Not enought recycling power.")

	for iname,amount in items.items():
		c_items.add(iname,-amount)
		
	for dict_amount,dict_items in max_return.items():
		for input_name,input_amount in dict_items.items():
			if input_name in unrecyclable:
				continue
			i=dict_amount*input_amount
			recycle_output = func.f2ir(i*boost)
			c_items.add(input_name,recycle_output)
	tstruct["stats"]["recycle"]["current"] -= price
	cdata.save() 
	tstruct.save()


	



