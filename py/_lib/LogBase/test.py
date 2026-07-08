import sys
sys.path.insert(0,"..")
import LogBase as lb

#import api,query
def test():
	#setup
	#lb.init("example.csv","schema.csv")
	#lb.restore()
	
	#ref
	#idx = lb.run(action="ref-key-set",table="ships",ref="beetle",key="name",val="bkargagd")
	#print(lb.ask(query="table-get",table="ships",ref="beetle"))
	#lb.rollback(idx)
	
	test_start()
	test_log()
	test_table()
	test_ref()
	test_end()

test_start_idx = None

def test_start():
	global test_start_idx
	lb.init("example.csv","schema.csv")
	lb.restore()
	test_start_idx = lb.log_idx()
def test_end():
	lb.rollback(test_start_idx)
def test_log():
	pass
	#log_restore
def test_table():
	pass
	#table_create
	#table_delete
def test_ref():
	global test_start_idx
	lb.run(action="ref-key-set",table="ships",ref="beetle",key="name",val="bkargagd")
	#test_start_idx = lb.run(action="ref-key-set",table="ships",ref="beetle",key="name",val="bkargagd")
	print(lb.ask(query="table-get",table="ships",ref="beetle"))
	#ref_create
	#ref_key_set
	#ref_key_clear
	#ref_delete




test()

"""
Test types needed:
Basic(action) - does each command work. Not done yet: log_restore, table_create, table_delete, ref_create, ref_key_set, ref_key_clear
Basic(query) - Not done yet: table_get, table_get_ref, ref_key_get
Limit - weird inputs. Q: what happens on a failure?
Smoke - actual game data

Tests should create their own environment and clear it regardless of what happens.
Probably clear at the start instead of end, because looking at files might be useful.

"""
