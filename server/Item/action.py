import copy
from server import defs
from . import query

def give(items,cdata):
	remaining = copy.deepcopy(items)
	room_left = cdata.get_room()
	inv = cdata["items"]
	for item,amount in remaining.items():
		size = query.size(item)
		if size:
			amount = min(amount,room_left//size)
		amount = max(amount,0)
		if not amount: continue
		inv.add(item,amount)
		remaining[item] -= amount
		if size:
			room_left -= amount*size
	cdata.save()
	return remaining
def drop(items,system,x,y):
	otiles = defs.objmaps[system]["tiles"]
	otile = otiles.get(x,y)
	if "items" not in otile:
		otile["items"] = {}
	for name,amount in items.items():
		if not amount: continue
		if name not in otile["items"]:
			otile["items"][name] = 0
		otile["items"][name] += amount
	otiles.set(x,y,otile)
	otiles.save()