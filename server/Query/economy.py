from . import api
from server import defs,structure,items

def get_idata(cdata,pship):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	idata = items.character_itemdata(cdata)
	if tstructure:
		prices = tstructure.get_prices()
		idata = idata | items.itemlist_data(prices.keys()) | items.structure_itemdata(tstructure)
	return idata
def get_structure(cdata,pship):
	def copys(a,b,*args):
		for arg in args:
			if arg in a:
				b[arg] = a[arg]
		return b
	def delete(table,key,replacement=None):
		if key in table:
			if replacement:
				table[key] = replacement
			else:
				del table[key]
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	if not tstructure: return
	output = copys(tstructure,{},"name","custom_name","desc","type","ship","owner","img","credits","pos","items","gear","market","stats","industries","quests","blueprints","builds","transport","props")
	owned = cdata["name"] == tstructure["owner"]
	if not owned:
		delete(output,"items",{})
		delete(output,"gear",{})
		delete(output,"blueprints",[])
		delete(output,"builds",[])
		delete(output,"transport",{})
		prices = tstructure.get_prices()
		output["items"] = {}
		output["gear"] = {}
		copys(tstructure["items"],output["items"],*prices.keys())
	return output

api.register_query("idata",get_idata)
api.register_query("structure",get_structure)
