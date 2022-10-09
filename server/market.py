import os,copy
from . import io,player,goods,func

io.check_dir("market")

markets = {}
markets["Ska"] = io.read(os.path.join("market","Ska.json"))

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
				"items":{},
				"prices":copy.deepcopy(goods.default),
				"population": "Skara",
				"system": "Ska"
			}
			io.write(os.path.join("market",system_name+".json"),markets[system_name])
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
	io.write(os.path.join("market",system_name+".json"),markets[system_name])
def trade(pdata,data,market):
	player_items = pdata["items"]
	player_credits = pdata["credits"]
	buy = data["buy"]
	sell = data["sell"]
	market_items = market["items"]
	market_prices = market["prices"]
	market_credits = market["credits"]
	success = False
	for item,amount in sell.items():
		price = market_prices[item]["buy"]
		stock = func.get(player_items,item)
		#Can't sell less than 0.
		amount = max(amount,0)
		#Can't sell more than you have, or more than market has money for.
		amount = min(amount,stock,market_credits//price)
		if amount == 0:
			#Don't bother updating anything.
			continue
		player_items[item] -= amount
		if not player_items[item]:
			del player_items[item]
		player_credits += amount*price
		market_items[item] += amount
		market_credits -= amount*price
		pdata["space_available"] += amount
		success = True
	for item,amount in buy.items():
		price = market_prices[item]["sell"]
		stock = func.get(market_items,item)
		#Can't buy less than 0.
		amount = max(amount,0)
		#Can't buy more than market has, or more than the player has money for.
		amount = min(amount,stock,player_credits//price)
		if amount == 0:
			#Don't bother updating anything.
			continue
		player.add_item(pdata,item,amount)
		player_credits -= amount*price
		market_items[item] -= amount
		market_credits += amount*price
		pdata["space_available"] -= amount
		success = True
	if success:
		pdata["items"] = player_items
		pdata["credits"] = player_credits
		market["items"] = market_items
		market["credits"] = market_credits
		player.write()
		system_name = pdata["system"]
		write(system_name)
