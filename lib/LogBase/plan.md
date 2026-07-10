A database based on storing changes to dictionaries into logs.
In order to eventually support transactions, a single log has to contain every table.

Currently this project is stuck behind lack of usefulness.
If it could be used in practice, then that would provoke more interest on my part. (X)

Each command has at most these parameters:
- action - what the command is
- table - which table it's on
- key - which key in the table
- val - value of that key, to change it

Table and key are slightly redundant, but...
- table can support typechecking on setters.
- looping over everything in a table is useful, so having a separate key variable can help with that.

Edge cases:
- maps. Each map is a separate table, because otherwise it would be annoying to get all tiles in a map. (current structure doesn't like nesting tables within tables)
- complex data. When thinking in terms of objects, each parameter has to be in a different table.

The structure of data is like this:
DB->table->key->value
DB(the entire log)
	ship_name
		beetle-5: "Beetlastic"
	ship_x
		beetle-5: 5
	ship_y
		beetle-5: -7
	ship_r
		beetle-5: 180
	ship_system
		beetle-5: "Megrez"
	"Megrez:tile_full_time"
		"5,-7": 1783431575.610082

What does it need to be useful?
Log rotation: table_load
Basic table operations: table_create, table_delete, table_set, table_unset
Queries: table_get, table_all, (maybe)table_filter
Tests for all of the above^

After that, try to run it as an alternative database for traveller. 
Initially use this as a parallel option, then start transferring things over.
Start with positions for example: they break entire ships when the server computer crashes.
Later: make it illegal to change data except in the context of a transaction. 

Immediate concerns:
*Create, delete, update a dictionary.
*Log rotation

Later:
*Schemas, validation, transactions

**Issues**
- When there is an error during testing, the rollback isn't done. It seems having any operation fail with an error is unacceptable.

