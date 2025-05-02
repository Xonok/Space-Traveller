from . import api
from server import items,structure

#kind of annoying that everything has to take udata and cdata
#just udata alone would probably be fine
def get_idata(cdata,pship):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	idata = items.character_itemdata(cdata)
	if tstructure:
		prices = tstructure.get_prices()
		idata = idata | items.itemlist_data(prices.keys())
		if tstructure["owner"] == cdata["name"]:
			idata = idata | items.structure_itemdata(tstructure)
	return idata

api.register_query("idata",get_idata)

