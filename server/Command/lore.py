from . import api
from server import Content,defs

def do_get_lore(cdata):
	return {"lore_entries":Content.lore.entries()}
def do_request_lore(cdata,name="str"):
	return {
		"request_name": name,
		"request_data": Content.lore.request(name)
	}
api.register("get-lore",do_get_lore)
api.register("request-lore",do_request_lore)
