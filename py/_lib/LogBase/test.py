import sys
sys.path.insert(0,"..")
import LogBase as lb

def test():	
	try:
		test_start()
		test_run()
		test_rotate()
	finally:
		test_end()

"""
What does it need to be useful?
Log rotation: table_load
Basic table operations: table_create, table_delete, table_set, table_unset
Queries: table_get, table_all, table_dump, (maybe)table_filter
Tests for all of the above^

start server:
*get latest log
*replay events
*calculate next rotation time and set timeout

log rotate:
*stop saving to disk(still accept writes,just buffer them)
*start a new log
*dump each table into the new log
*move old log to storage
*rename new log to standard name

"""

test_start_idx = None

def test_start():
	global test_start_idx
	lb.init("example.csv","schema.csv")
	lb.restore()
	test_start_idx = lb.log_idx()
def test_run():
	pass
	#log_restore
	#table_create
	#table_delete
	global test_start_idx
	lb.run("table-set","ship_name","beetle","bkargagd")
	#test_start_idx = lb.run("table-set","ship_name","beetle","bkargagd")
	print(lb.ask("table-get","ship_name","beetle"))
	#ref_create
	#ref_key_set
	#ref_key_clear
	#ref_delete
def test_rotate():
	lb.log_rotate("logs_old")
def test_end():
	if test_start_idx is not None:
		lb.rollback(test_start_idx)

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
