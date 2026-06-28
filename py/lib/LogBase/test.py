import api,query
def test():
	api.init("example.csv","schema.csv")
	#Need to configure file for io operations. Let's say it's in init for now.
	api.restore()
	api.run(action="ref-set",table="ships",ref="beetle",key="name",val="bkargagd")
	print(api.ask(query="table-get",table="ships",ref="beetle"))
test()
