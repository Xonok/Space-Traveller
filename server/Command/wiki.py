from . import api
from server import Content

def do_get_wiki_page(cdata,page="str"):
	return Content.wiki.get_page(page,cdata)
api.register("get-wiki-page",do_get_wiki_page)
