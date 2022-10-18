import os,copy
from . import io,player,goods,gear,items,map,grid

class MItems(items.Items):
	def __init__(self,default=0,system="",**kwargs):
		super().__init__(default,**kwargs)
		self.system = system
	def add(self,key,value):
		super().add(key,value)
		write(self.system)
	def remove(self,key):
		super().remove(key)
		write(self.system)

markets = {}
for system in map.get_all():
	markets[system] = io.read("market",system,grid.Grid)
	for market in markets[system].get_all():
		if "items" not in market:
			market["items"] = {}
		market["items"] = MItems(system=system,**market["items"])

def adjust_prices(market,tax):
	pricelist = goods.default
	prices = {}
	for item, price in pricelist.items():
		entry = {}
		entry["buy"] = round(price/(1+tax))
		entry["sell"] = round(price*(1+tax))
		prices[item] = entry
	market["tax"] = tax
	market["prices"] = prices
def sell_gear(market):
	gearlist = gear.types
	gear_list = {}
	for item,data in gearlist.items():
		entry = copy.deepcopy(data)
		entry["buy"] = data["price"]//2
		entry["sell"] = data["price"]
		del entry["price"]
		gear_list[item] = entry
	market["gear"] = gear_list
def check_market(system_name,x,y):
	if system_name not in markets:
		return
	market_list = markets[system_name]
	if x not in market_list or y not in market_list[x]:
		if system_name == "Ska" and x == "1" and y == "0":
			if x not in market_list:
				market_list[x] = {}
			market_list[x][y] = {
				"credits": 1000000,
				"items":MItems(system=system_name),
				"population": "Skara",
				"system": system_name
			}
			adjust_prices(market_list[x][y],0.1)
			sell_gear(market_list[x][y])
			io.write("market",system_name,markets[system_name])
			return True
		else:
			return
	else:
		return True
def get(system_name,x,y):
	x = str(x)
	y = str(y)
	if not check_market(system_name,x,y):
		return None
	market_list = markets[system_name]
	return market_list[x][y]
def write(system_name):
	io.write("market",system_name,markets[system_name])
def trade(user,pdata,data,market):
	player_items = items.pitems[user]
	player_credits = pdata["credits"]
	buy = data["buy"]
	sell = data["sell"]
	market_items = market["items"]
	market_gear = market["gear"]
	market_prices = market["prices"]
	market_credits = market["credits"]
	success = False
	for item,amount in sell.items():
		if item in market_gear:
			price = market_gear[item]["buy"]
		elif item in market_prices:
			price = market_prices[item]["buy"]
		size = items.size(item)
		stock = player_items.get(item)
		#Can't sell more than you have, or more than market has money for.
		amount = min(amount,stock,market_credits//price)
		#Can't sell less than 0.
		amount = max(amount,0)
		if amount == 0:
			#Don't bother updating anything.
			continue
		player_items.add(item,-amount)
		player_credits += amount*price
		if item not in market_gear:
			market_items.add(item,amount)
		market_credits -= amount*price
		pdata["space_available"] += amount*size
		success = True
	for item,amount in buy.items():
		if item in market_gear:
			price = market_gear[item]["sell"]
		elif item in market_prices:
			price = market_prices[item]["sell"]
		size = items.size(item)
		stock = market_items.get(item)
		limit = int(pdata["space_available"]/size)
		#Can't buy more than market has, more than the player can fit, or more than the player has money for.
		amount = min(amount,limit,stock,player_credits//price)
		#Can't buy less than 0.
		amount = max(amount,0)
		if amount == 0:
			#Don't bother updating anything.
			continue
		player_items.add(item,amount)
		player_credits -= amount*price
		market_items[item] -= amount
		market_credits += amount*price
		pdata["space_available"] -= amount*size
		success = True
	if success:
		pdata["credits"] = player_credits
		market["items"] = market_items
		market["credits"] = market_credits
		player.write()
		system_name = pdata["system"]
		write(system_name)
get("Ska",1,0)
adjust_prices(markets["Ska"]["1"]["0"],0.1)
sell_gear(markets["Ska"]["1"]["0"])
write("Ska")