from . import api
from server import Battle

def get_battle(cdata):
	return Battle.get(cdata)

api.register_query("battle",get_battle)
