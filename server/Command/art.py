from . import api
from server import Content

def do_get_art(cdata):
	return {"images":Content.art.get_all_images()}
api.register("get-art",do_get_art)
