from . import api
from server import defs,structure,items,build,map,Permission

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
	permission = Permission.check(cdata["name"],tstructure,"give")
	if not permission:
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
def get_prices(pship):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	if not tstructure: return
	return tstructure.get_prices()
def get_bp_info(pship):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	if not tstructure: return
	return build.get_bp_info(tstructure)
def get_repair_fees(pship):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	if not tstructure: return
	return tstructure.get_repair_fees()
def get_industry_defs(pship):
	psystem,px,py = pship.loc()
	tstructure = structure.get(psystem,px,py)
	if not tstructure: return
	return tstructure.get_industries()
def get_transport_targets(cdata,pship):
	return map.get_owned_structures(pship["pos"]["system"],cdata["name"])

api.register_query("idata",get_idata)
api.register_query("structure",get_structure)
api.register_query("prices",get_prices)
api.register_query("bp-info",get_bp_info)
api.register_query("repair-fees",get_repair_fees)
api.register_query("industry-defs",get_industry_defs)
api.register_query("transport-targets",get_transport_targets)
