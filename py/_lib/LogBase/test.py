import api,query
def test():
	#setup
	api.init("example.csv","schema.csv")
	api.restore()
	
	#ref
	idx = api.run(action="ref-set",table="ships",ref="beetle",key="name",val="bkargagd")
	print(api.ask(query="table-get",table="ships",ref="beetle"))
	api.rollback(idx)
test()
