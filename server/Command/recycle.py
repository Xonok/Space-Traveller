from server import Recycling

def do_recycle_items(cdata,struct_id="str",items="dict:int",energy="bool",exomatter="bool"):
	Recycling.recycle(cdata,struct_id,items,energy,exomatter)

api.register("recycle-items",do_recycle_items)