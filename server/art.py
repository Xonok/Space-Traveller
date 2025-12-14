import os
from server import defs,io

def get_all_images():
	items = {}
	ships = {}
	landmarks = {}
	wormholes = {}
	badges = {}
	glyphs = {}
	quests = {}
	for name,data in defs.items.items():
		items[name] = data.get("img_original",data["img"])
	for name,data in defs.ship_types.items():
		ships[name] = data.get("img_original",data["img"])
	for name,data in defs.landmark_types.items():
		landmarks[name] = data.get("img_original",data["img"])
	for name,data in defs.wormhole_types.items():
		if "img" in data:
			wormholes[name] = data.get("img_original",data["img"])
	for name,data in defs.factions.items():
		if "badge" in data:
			badges[name] = data.get("img_original",data["badge"])
		if "glyph" in data:
			glyphs[name] = data.get("img_original",data["glyph"])
	for name,data in defs.quests.items():
		quests[name] = []
		quests[name].append(data.get("icon_original",data["icon"]))
		for outcome in data["outcomes"]:
			if "end_img" in outcome:
				quests[name].append(data.get("end_img_original",outcome["end_img"]))
	result = {
		"items": items,
		"ships": ships,
		"landmarks": landmarks,
		"wormholes": wormholes,
		"badges": badges,
		"glyphs": glyphs,
		"quests": quests
	}
	all_images = {}
	for key,data in result.items():
		for name,src in data.items():
			if type(src) == list:
				for src2 in src:
					all_images[src2] = name
			else:
				all_images[src] = name
	image_files = os.listdir("img")
	unused = []
	for path in image_files:
		if os.path.isdir(os.path.join(io.cwd,"img",path)): continue
		path = "img/"+path
		if path not in all_images:
			# print(path)
			unused.append(path)
	result["unused"] = unused
	#make an overall list of images
	#list images in img folder
	#cross-reference image folder with overall list
	#any unused images should go into a separate category
	return result