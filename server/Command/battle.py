from . import api
from server import Battle

def do_get_battle(cdata):
	pass
def do_attack(cdata):
	battle_update = Battle.attack(cdata)
	return {
		"battle-update": battle_update
	}
def do_retreat(server,cdata):
	pbattle = Battle.get(cdata)
	battle_update = Battle.retreat(pbattle,0,server)
	if battle_update:
		return {
			"battle-update": battle_update
		}
api.register("get-battle",do_get_battle,"battle")
api.register("attack",do_attack)
api.register("retreat",do_retreat)