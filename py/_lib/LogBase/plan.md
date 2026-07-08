A database based on storing changes to dictionaries into logs.
In order to eventually support transactions, a single log has to contain every table.

Currently this project is stuck behind lack of usefulness.
If it could be used in practice, then that would provoke more interest on my part. (X)

The structure of data is like this:

DB(the entire log)
	(Currently well-supported case)
	ships(table)
		beetle-5
			name: "Beetlastic"
			x: 5
			y: -7
			r: 180
			system: "Megrez"
	(Badly supported case)
	(5,-7,tile_full_time would have to be squished into one here)
	(Seems like the csv format needs to have a little flexibility in this)
	(Changing number of columns or expecting a maximum case doesn't seem reasonable)
	(I guess I need a special separator like : so that there could be a chain of keys)
	(Essentially, everything is attached to DB with a list of keys and then finally an optional value)
	(Seems like it would even be possible to treat every chain of keys as in itself a key, thus making the whole DB flat)
	(A possible counterargument is that schemas need to be implemented somehow)
	(Schemas need some kind of pattern to check against, though it need not be in the form of objects)
	(Something like an object could be useful for processing purposes. It might as well be a class instance that has a reference to its address in the DB.)
	(But hey, ain't that just object pointers with extra steps?)
	(In any case, it seems like each table in the DB should have a schema attached. The schema says what the keychain looks like and what's at the end of it.)
	(It hardly seems to matter whether it's a keychain or a single joined key though)
	(Counterpoint: looping over stuff. How do you loop over stuff like tiles? Split it by why you're looping?)
	(What if you care about many aspects? For example, let's say you want the stats of a ship, its location, its owner, etc)
	(Can still be done with splitting.)
	(The performance impact isn't a big deal - the amount of dictionary lookups is likely the same, if it isn't actually lower for the flat one)
	(Unlike dictionaries it's theoretically possible to pack data into arrays or something, even)
	(Dict-based: tiles->x->y->full_time)
	(Flat: tile_full_time->xy)
	(Could say "Okay, but once you have the tile, you can just pick stuff out of it)
	(Yeah, but that's also a dictionary operation.)
	(Best case, if you have a large dict, you'll do 1 operation per field in dict-based and 2 in flat)
	(If that ever matters, it's possible to make the flat one also 1 op per field, though it would make schemas a little harder to implement)
	(Hardly matters in any case. Flat is likely better overall, since it's more open to optimization and unlikely to be slower than dict-based in the first place)
	(Anyways, it seems with this logic it's possible to handle a lot of recursion by reorganizing how I think about things.)
	(There are no objects. Instead there are tables for object properties, with the object IDs as references)
	(ship_name->"beetle-5"->"Beetlastic")
	(This is essentially identical to how it's done in C)
	(Heck, it could be done without dictionaries, if the object IDs are numbers instead of strings)
	tiles(table)
		"Megrez"
			5
				-7
					tile_full_time: 1783431575.610082
			

What does it need to be useful?
Basic table operations: table_new, table_delete, table_load(for log rotation)
Basic entry operations: entry_add, entry_delete
Basic var operations: set, clear


Immediate concerns:
*Create, delete, update a dictionary.

Later:
*Schemas, validation, transactions, log rotation


Start with a pregenerated log.
For testing purposes, keep everything in the same folder for now and run this file alone.

**Issues**
- When there is an error during testing, the rollback isn't done. It seems having any operation fail with an error is unacceptable.

