from . import api
from server import defs,ship,map

def get_vision(cdata):
	return cdata.get_vision()

api.register_query("vision",get_vision)
