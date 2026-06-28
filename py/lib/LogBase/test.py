import api,query
def test():
	api.init()
	api.restore("example.csv")
	api.run(action="ref-set",table="ships",ref="beetle",key="name",val="bkargagd")
	print(api.ask(query="table-get",table="ships",ref="beetle"))
test()
