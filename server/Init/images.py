import os
from server import defs

cwd = os.getcwd()
def image_exists(path):
	path = path.replace("/","\\")
	return os.path.exists(os.path.join(cwd,path))
def fallback(itype):
	#TODO: weapon subtypes
	match itype:
		case "gun":
			return "img/placeholders/placeholder_gun.webp"
		case "missile":
			return "img/placeholders/placeholder_missile.webp"
		case "armor":
			return "img/placeholders/placeholder_armor.webp"
		case "shield":
			return "img/placeholders/placeholder_shield.webp"
		case _:
			return "img/placeholders/placeholder_gun.webp"
record_originals = True
def swap(data,itype):
	img = data["img"]
	if not image_exists(img):
		fb_img = fallback(itype)
		if record_originals:
			data["img_original"] = img
		data["img"] = fb_img
def init():
	for name,data in defs.items.items():
		itype = data["type"]
		swap(data,itype)
	for name,data in defs.ship_types.items():
		swap(data,"ship")
	for name,data in defs.landmark_types.items():
		swap(data,"landmark")
	for name,data in defs.quests.items():
		img = data["icon"]
		if not image_exists(img):
			fb_img = fallback(itype)
			if record_originals:
				data["icon_original"] = img
			data["icon"] = fb_img
		for outcome in data["outcomes"]:
			if "end_img" in outcome:
				img = outcome["end_img"]
				if not image_exists(img):
					fb_img = fallback(itype)
					if record_originals:
						outcome["img_original"] = img
					outcome["end_img"] = fb_img