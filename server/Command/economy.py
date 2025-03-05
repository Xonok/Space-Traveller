from . import api
from server import gathering

def gather(ctx):
	pship = ctx.get("pship")
	server = ctx.get("server")
	gathering.gather(pship,server,user=True)
api.register("gather",gather)