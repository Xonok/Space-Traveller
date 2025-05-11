from . import api
from server import wiki

def do_get_wiki_page(cdata,page="str"):
	return wiki.get_page(page,cdata)
api.register("get-wiki-page",do_get_wiki_page)
