from server import defs

def get(entity,source=True,owner=False,type=True,id=True):
	custom = entity.get("custom_name")
	if custom: return custom
	source2 = entity.get("source")
	if source2:
		source2 = get(defs.ships.get(source2))
	owner2 = entity.get("owner")
	type2 = entity.get("type")
	id2 = entity.get("id")
	result = ""
	if source and source2:
		result += source2
	if owner and owner2:
		if len(result):
			result += ","
		result += owner2
	if type and type2:
		if len(result):
			result += ","
		result += type2
	if id and id2:
		result += " #"+str(id2)
	if not result:
		return entity["name"]
	return result