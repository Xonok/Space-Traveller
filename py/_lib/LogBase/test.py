import api,query
def test():
	#setup
	api.init("example.csv","schema.csv")
	api.restore()
	
	#ref
	idx = api.run(action="ref-key-set",table="ships",ref="beetle",key="name",val="bkargagd")
	print(api.ask(query="table-get",table="ships",ref="beetle"))
	api.rollback(idx)
test()

"""
Test types needed:
Basic - does each command work.
Limit - weird inputs. Q: what happens on a failure?
Smoke - actual game data

Tests should create their own environment and clear it regardless of what happens.
Probably clear at the start instead of end, because looking at files might be useful.

"""
