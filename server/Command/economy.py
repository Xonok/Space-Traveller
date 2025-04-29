from . import api
from server import gathering,Battle

def gather(pship,server):
	if Battle.get(cdata): raise error.Battle()
	gathering.gather(pship,server,user=True)
api.register("gather",gather)