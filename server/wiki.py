from . import defs,error

def t_copy(a,b,key):
	if key in a:
		b[key] = a[key]
def t_copys(a,b,*keys):
	for k in keys:
		t_copy(a,b,k)
def get_page(data,response,cdata):
	page = data["page"]
	data2 = {}
	response["command"] = data["command"]
	response["page"] = page
	response["data"] = data2
	
	if page == "item_list":
		for iname,idata in defs.items.items():
			data2[iname] = {}
			t_copys(idata,data2[iname],iname,"img","name","type","tech","size")
	elif page == "ship_list":
		for sname,sdata in defs.ship_types.items():
			data2[sname] = {}
			t_copys(sdata,data2[sname],sname,"img","name","tech","size","room","hull","speed","agility","tracking","control","slots")
	elif page == "monster_list":
		for mname,mdata in defs.premade_ships.items():
			if "spawner_count" in mdata:
				data2[mname] = {}
				t_copys(mdata,data2[mname],mname,"default_name","ship","bounty","gear")
	else:
		raise error.User("Unknown wiki page: "+page)
