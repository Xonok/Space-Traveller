from . import item,structure,character
from server import defs,stats,ship,types,Group

predef_update = {
	"ark_probe": "ark_miner"
}
structure_update = {
	"starbase": "bastion"
}
def run():
	for omap_name,omap in defs.objmaps.items():
		for x,col in omap["tiles"].items():
			for y,otile in col.items():
				if "items" not in otile: continue
				item.item_names(otile["items"],omap_name+": "+x+","+y)
		omap.save()
	for tstruct in defs.structures.values():
		if tstruct["ship"] in structure_update:
			tstruct["ship"] = structure_update[tstruct["ship"]]
	for tstruct in defs.structures.values():
		structure.assigned_industries(tstruct)
	for tstruct in defs.structures.values():
		structure.price_lists(tstruct)
	for name,data in defs.ships.items():
		owner = data["owner"]
		if owner not in defs.character_ships:
			defs.character_ships[owner] = {}
		defs.character_ships[owner][name] = name
	character.inventory_revamp()
	for cdata in defs.characters.values():
		item.inventory(cdata["items"],cdata)
	for pship in defs.ships.values():
		item.inventory(pship["gear"],pship)
	for tstruct in defs.structures.values():
		item.inventory(tstruct["items"],tstruct)
		item.inventory(tstruct["gear"],tstruct)
		item.station(tstruct)
	for name,data in defs.ships.items():
		shipdef = defs.ship_types.get(data["type"])
		if shipdef:
			data["img"] = shipdef["img"]
		stats.update_ship(data)
		data.save()
	for name,data in defs.structures.items():
		owner = data["owner"]
		if owner not in defs.character_structures:
			defs.character_structures[owner] = {}
		defs.character_structures[owner][name] = name
		shipdef = defs.ship_types.get(data["ship"])
		if shipdef:
			data["img"] = shipdef["img"]
		stats.update_ship(data)
		data.save()
	for name,data in defs.structures.items():
		structure.update_pos(data)
	for name,data in defs.structures.items():
		structure.update_desc(data)
		if name in defs.predefined_structures:
			data["owner"] = defs.predefined_structures[name]["owner"]
	for pship in defs.ships.values():
		if "predef" not in pship: continue
		if pship["predef"] in predef_update:
			pship["predef"] = predef_update[pship["predef"]]
	for cname,ship_names in defs.character_ships.items():
		if cname not in defs.npc_characters: continue
		for name in ship_names:
			pship = ship.get(name)
			if "predef" not in pship: continue #This is hiding a real problem. Older ship files don't always have predefs mentioned, although they should.
			predef = defs.predefined_ships.get(pship["predef"])
			if not predef: continue
			pship["gear"] = types.copy(predef["gear"],"items")
	for cdata in defs.characters.values():
		character.update(cdata)
	Group.api.update()