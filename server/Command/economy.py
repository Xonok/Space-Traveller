from . import api
from server import gathering,Battle,archaeology,error,defs,items,ship,character,loot,structure,Query,build,Item

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
def do_get_goods(cdata,pship):
	if Battle.get(cdata): raise error.Battle()
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	if not tstructure: raise error.Page()
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
def do_update_trade(cdata,pship,items="dict"):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	tstructure.update_trade(cdata,items)
def do_update_structure_name(cdata,struct_id="str",name="str"):
	structure.update_name(struct_id,name,cdata)
def do_update_structure_desc(cdata,struct_id="str",desc="str"):
	structure.update_desc(struct_id,desc,cdata)
def do_structure_next_tick(udata,pship):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	tstructure.force_next_tick(udata)
def do_structure_update_limits(cdata,pship,limits="dict"):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	tstructure.update_limits(limits,cdata)
def do_update_transport(pship,entries="list",next_action="int+"):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	Item.transport.update_actions(tstructure,entries,next_action)
def do_planet_donate_credits(server,cdata,pship,target="str",amount="int+"):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	tstructure.donate_credits(server,cdata,amount)
def do_ship_pack(server,cdata,pship,target="str"):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	tstructure.pack_ship(server,cdata,target)
api.register("gather",gather)
api.register("investigate",investigate)
api.register("excavate",excavate)
api.register("drop",drop)
api.register("use-item",use_item) #was use_item
api.register("ship-trade",ship_trade)
api.register("give-credits-character",give_credits_character)
api.register("take-loot",take_loot)
api.register("pack-station",pack_station)
api.register("get-goods",do_get_goods,"structure","idata","ship-defs","prices","bp-info","repair-fees","industry-defs","transport-targets","tile","local-quests","character-quests","skill-location","skill-data")
api.register("structure-trade",do_structure_trade,"structure","idata","ship-defs")
api.register("structure-give-credits",do_structure_give_credits,"structure")
api.register("structure-take-credits",do_structure_take_credits,"structure")
api.register("start-build",do_start_build,"structure")
api.register("equip-blueprint",do_equip_blueprint,"structure","bp-info")
api.register("unequip-blueprint",do_unequip_blueprint,"structure")
api.register("update-trade",do_update_trade,"structure","prices")
api.register("update-name",do_update_structure_name,"structure")
api.register("update-desc",do_update_structure_desc,"structure")
api.register("structure-next-tick",do_structure_next_tick,"structure")
api.register("structure-update-limits",do_structure_update_limits,"structure")
api.register("update-transport",do_update_transport,"structure")
api.register("planet-donate-credits",do_planet_donate_credits,"structure")
api.register("ship-pack",do_ship_pack)
