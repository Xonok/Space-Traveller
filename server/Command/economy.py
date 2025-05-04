from . import api
from server import gathering,Battle,archaeology,error,defs,items,ship,character,loot,structure,Query,build

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
def do_get_goods():
	pass
def do_structure_trade(server,cdata,pship,data="list"):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	if not tstructure: raise error.User("There is no structure here.")
	tstructure.transfer(cdata,data,server)
def do_structure_give_credits(cdata,pship,amount="int+"):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	structure.give_credits(amount,cdata,tstructure)
def do_structure_take_credits(cdata,pship,amount="int+"):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	structure.take_credits(amount,cdata,tstructure)
def do_start_build(cdata,pship,blueprint="str"):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	build.start(blueprint,cdata,tstructure)
def do_equip_blueprint(cdata,pship,blueprint="str"):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	build.equip_blueprint(blueprint,cdata,tstructure)
def do_unequip_blueprint(cdata,pship,blueprint="str"):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	build.unequip_blueprint(blueprint,cdata,tstructure)

api.register("gather",gather)
api.register("investigate",investigate)
api.register("excavate",excavate)
api.register("drop",drop)
api.register("use-item",use_item) #was use_item
api.register("ship-trade",ship_trade)
api.register("give-credits-character",give_credits_character)
api.register("take-loot",take_loot)
api.register("pack-station",pack_station)
api.register("get-goods",do_get_goods)
api.register("structure-trade",do_structure_trade)
api.register("structure-give-credits",do_structure_give_credits)
api.register("structure-take-credits",do_structure_take_credits)
api.register("start-build",do_start_build)
api.register("equip-blueprint",do_equip_blueprint)
api.register("unequip-blueprint",do_unequip_blueprint)

Query.register_command("get-goods","structure","idata","ship-defs")
Query.register_command("structure-trade","structure","idata","ship-defs")
Query.register_command("structure-give-credits","structure")
Query.register_command("start-build","structure")
Query.register_command("equip-blueprint","structure")
Query.register_command("unequip-blueprint","structure")

				# elif command == "update-trade":
					# tstructure.update_trade(cdata,data)
				# elif command == "update-name":
					# self.check(data,"structure","name")
					# structure.update_name(data,cdata)
				# elif command == "update-desc":
					# self.check(data,"structure","desc")
					# structure.update_desc(data,cdata)
				# elif command == "structure-next-tick":
					# tstructure.force_next_tick(udata)
				# elif command == "structure-update-limits":
					# self.check(data,"limits")
					# tstructure.update_limits(data,cdata)
				# elif command == "update-transport":
					# self.check(data,"entries","next_action")
					# Item.transport.update_actions(tstructure,data["entries"],data["next_action"])
				# elif command == "planet-donate-credits":
					# self.check(data,"amount","target")
					# tstructure.donate_credits(self,cdata,data)
				# elif command == "ship-pack":
					# self.check(data,"target")
					# tstructure.pack_ship(self,cdata,data)