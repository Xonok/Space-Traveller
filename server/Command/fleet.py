from . import api
from server import Battle,ship,hive

def start_battle(server,cdata,target="str"):
	if Battle.get(cdata): raise error.Battle()
	Battle.start(cdata,target,server)
def guard(cdata,dship="str"):
	ship.guard(cdata,dship)
def follow(cdata,dship="str"):
	ship.follow(cdata,dship)
def homeworld_return(cdata):
	hive.use_homeworld_return(cdata)
def ship_rename(pship,name="str"):
	pship.rename(name)
api.register("start-battle",start_battle)
api.register("guard",guard)
api.register("follow",follow)
api.register("homeworld-return",homeworld_return)
api.register("ship-rename",ship_rename)
