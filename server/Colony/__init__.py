from . import procedure,query

#A colony is always located on an entity(ship/structure)
#Colonies don't have their own resource storage. Instead they buy goods from their parent entity every time they need something.
#Every tick the parent gains credits from the colony if the colony has wealth.

#Each colony has some pop attributes:
#*Workers - primary output
#*Industry - industrial output
#*Wealth - taxation
#*Prestige - migration(source of colonists)
#*Science - archaeology, don't know how
#*Biotech - hive-exclusive. Decreases input costs.

#Required functionality
#Start a colony
#Default colonies(planets)
#Tick - spend resources, change pop details
#Industrial production
#Management - get rid of population to unequip hab modules