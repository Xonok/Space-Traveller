import os
from . import io,player

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
				"items":{
					"energy": {
						"amount": 0,
						"buy": 50,
						"sell": 100
					},
					"gas": {
						"amount": 0,
						"buy": 100,
						"sell": 200
					}
				}
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
def trade(pdata,data,market):
	player_items = pdata["items"]
	player_credits = pdata["credits"]
	buy = data["buy"]
	sell = data["sell"]
	market_items = market["items"]
	market_credits = market["credits"]
	success = False
	for item,amount in sell.items():
		price = market_items[item]["buy"]
		stock = player_items[item]
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
		market_items[item]["amount"] += amount
		market_credits -= amount*price
		pdata["space_available"] += amount
		success = True
	for item,amount in buy.items():
		price = market_items[item]["sell"]
		stock = market_items[item]["amount"]
		#Can't buy less than 0.
		amount = max(amount,0)
		#Can't buy more than market has, or more than the player has money for.
		amount = min(amount,stock,player_credits//price)
		if amount == 0:
			#Don't bother updating anything.
			continue
		player.add_item(pdata,item,amount)
		player_credits -= amount*price
		market_items[item]["amount"] -= amount
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
		io.write(os.path.join("market",system_name+".json"),markets[system_name])