from . import api
from server import gathering

def gather(pship,server):
	gathering.gather(pship,server,user=True)
api.register("gather",gather)