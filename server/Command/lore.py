from . import api
from server import defs,lore

def do_get_lore(cdata):
	return {"lore_entries":lore.entries()}
def do_request_lore(cdata,name="str"):
	return {
		"request_name": name,
		"request_data": lore.request(name)
	}
api.register("get-lore",do_get_lore)
api.register("request-lore",do_request_lore)
