from . import api
from server import art

def do_get_art(cdata):
	return {"images":art.get_all_images()}
api.register("get-art",do_get_art)
