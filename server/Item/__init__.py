from . import transfer,query,industry,consumable,obtainable,transport,action,scrapyard,research,init

#submodules
query = query
industry = industry
transport = transport

#functions
transfer = transfer.transfer
size = query.size
data = query.data
prop = query.prop
ship_prop = query.ship_prop
ship_type = query.ship_type
consumable = consumable.use
give = action.give
drop = action.drop
init = init.init
