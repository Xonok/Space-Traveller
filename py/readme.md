This is the endpoint for code migration. Any new code should be placed according to this system:
**_lib** - generic libraries that are not intended to change. Among those is *func*, which is the container for any code too small to have its own library (yet).
**game** - game rules api. Should mostly be handled as game/tick or command/*
**command** - controller-logic - filtered through rights. Generic code in lib.
**query** - view-logic - requests for data, filtered through rights. Generic code in lib.
**def** - model-logic - how data actually works internally. Schema definition and checking logic in lib, schemas themselves not.
**update** - migration-logic - dealing with data updates between game versions
**auth** - who is allowed to do what - register and check requirements
**net** - game-specific net protocols. Should use generic code from lib.
**analysis** - code for gathering data about the game, including analyzing balance and content. Parts of it should move into balance sheets once those are integrated into the game repo. (currently in google sheets)
**forum** - forum code
**wiki** - generation code for wiki pages. Possibly balance sheets?
**test** - unit tests for various parts of the game. The idea is that an entire game mechanics file can be deleted and it would say what broke.

Can game mechanics be handled in such a way that code rarely has to refer to the files?
Possibly, if command and query logic is used enough.

Lots of "thing" files, like "ship" and "character". Should probably be split between parts of the MVC shceme instead.

Kinda want the decorator pattern or something. I want the way mechanics apply to entities to be simpler, so that nest could for example be treated as both a ship and station.
A start would be to cut all such classes down to being a composition of supported features.

Kinda also wish the names of folders didn't matter so much. Maybe I can force python to work like C by merging files on server start?
Definitely need to avoid loose code running itself though.

Current systems to migrate:
*AI - game/ai
*Analysis - analysis/
*Battle - game/battle
*Character - game/character
*Chat - net/ and game/chat and game/query, etc
*Command - command/
*Entity - game/<various>
*Forum - forum/
*Group - game/group
*Init - game/init - currently lots of code, should be boiled down to calling init handlers of various modules.
*Item - game/item
*js - unneeded, was an experiment
*Map - game/map
*Name - query/name
*Permission - auth/
*Query - query/\*
*Recycling - game/recycling
*Skill - game/skill
*Tick - game/tick
*Update - update/\*
*Validation - analysis/
*anomaly.py - game/
*archaeology - game/archaeology
*art - query/
*build - game/build
*cache - lib/cache
*character - game/character
*config - lib/config and game/init?
*defs - lib/schema and game/init
*error - lib/error? and query/error?
*exploration - game/achievements
*factory - game/factory
*func - lib/func
*gathering - game/gathering
*hive - game/hive
*html - lib/html
*info - game/init? and using info from query
*io - game/lib, mostly
*items - game/item
*log - game/lib, currently not used much
*loot - game/loot
*lore - query/lore
*map - game/map
*quest - game/quest
*reputation - game/rep
*ship - game/ship
*spawner - game/spawner? (don't like the name) maybe game/mobspawn?
*stats - game/stats? (seems like it should be an internal function, not directly from outside. Seems like it could be cut down a lot somehow.
*structure - game/structure
*tick - lib/tick and game/tick?
*types - lib/schema and def/schema
*user - lib/auth and auth/
*wiki - wiki/


