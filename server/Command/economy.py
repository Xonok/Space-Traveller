from . import api
from server import gathering,Battle,archaeology,error,defs,items,ship,character,loot

def gather(server,pship,cdata):
	if Battle.get(cdata): raise error.Battle()
	gathering.gather(pship,server,user=True)
def investigate(server,cdata,struct_name="str"):
	tstructure = defs.structures.get(struct_name)
	if not tstructure:
		raise error.User("Unknown structure id: "+struct_name)
	archaeology.investigate(server,cdata,tstructure)
def excavate(server,cdata,struct_name="str"):
	tstructure = defs.structures.get(struct_name)
	if not tstructure:
		raise error.User("Unknown structure id: "+struct_name)
	archaeology.excavate(server,cdata,tstructure)
def drop(cdata,pship,drop_items="dict"):
	items.drop(drop_items,cdata,pship)
def use_item(server,cdata,item="str"):
	items.use(server,cdata,item)
def ship_trade(cdata,pship,data="list"):
	pship.trade(cdata,data)
def give_credits_character(cdata,target="str",amount="int+"):
	character.give_credits(cdata,target,amount)
def take_loot(cdata,take_items="dict"):
	loot.take(cdata,take_items)
def pack_station(cdata,pship):
	structure.pick_up(pship,cdata)
api.register("gather",gather)
api.register("investigate",investigate)
api.register("excavate",excavate)
api.register("drop",drop)
api.register("use-item",use_item) #was use_item
api.register("ship-trade",ship_trade)
api.register("give-credits-character",give_credits_character)
api.register("take-loot",take_loot)
api.register("pack-station",pack_station)
