def use(used_item,pitems,pship):
	if used_item == "jello":
		jello_handler(pship)
	else:
		return
	pitems.add(used_item,-1)
def jello_handler(pship):
	sstats = pship["stats"]
	has_armor_reg = sstats["armor"]["reg"]
	current_armor = sstats["armor"]["current"]
	max_armor = sstats["armor"]["max"]
	if not has_armor_reg:
		raise error.User("Can only use Jello when the ship has regenerating armor.")
	if current_armor >= max_armor:
		raise error.User("Armor is already full.")
	sstats["armor"]["current"] = min(current_armor+8,max_armor)