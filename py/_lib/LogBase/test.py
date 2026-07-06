import api,query
def test():
	test_setup()
	test_ref()

def test_setup():
	api.init("example.csv","schema.csv")
	api.restore()
def test_ref():
	api.run(action="ref-set",table="ships",ref="beetle",key="name",val="bkargagd")
	print(api.ask(query="table-get",table="ships",ref="beetle"))
test()
