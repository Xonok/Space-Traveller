from . import api
from server import Battle,ship,structure,error,Chat

def start_battle(add_message,cdata,target="str"):
	if Battle.get(cdata): raise error.Battle()
	Battle.start(cdata,target,add_message)
def guard(cdata,pship,dship="str"):
	ship.guard(cdata,dship)
	psystem,x,y = pship.loc()
	Chat.map.send_tile_ships(cdata["name"],psystem,x,y)
def follow(cdata,pship,dship="str"):
	ship.follow(cdata,dship)
	psystem,x,y = pship.loc()
	Chat.map.send_tile_ships(cdata["name"],psystem,x,y)
def ship_rename(pship,name="str"):
	pship.rename(name)
def do_repair(add_message,cdata,pship,ship_id="str",hull="int+",armor="int+"):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	tstructure.repair(add_message,ship_id,hull,armor,cdata)
def do_repair_all(add_message,cdata,pship):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	tstructure.repair_all(cdata,add_message)
api.register("start-battle",start_battle)
api.register("guard",guard,"hwr")
api.register("follow",follow,"hwr")
api.register("ship-rename",ship_rename)
api.register("repair",do_repair)
api.register("repair-all",do_repair_all)
