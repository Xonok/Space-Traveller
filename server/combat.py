#in seconds
time_per_tick = 60*5 # 5 minutes per tick. Used for armor regeneration, actual combat can happen faster.

##COMBAT MECHANICS
#
#WEAPONS
#Laser - basic weapon
#Cannon - accuracy drops off with distance
#Missile - limited, but impressive firepower
#
#DEFENSES
#Hull - If this drops to 0, the ship is destroyed.
#Armor - Extra protection for the hull. 
#Shield - Regenerates every round.
#PD - shoot down missiles
#
#OTHER
#Speed - Can be used to make enemies target this ship more or less. 
#Agility - Makes a ship harder to hit.
#
#Actions - shoot

def attack(source,target):
	sweapons = {}
	tweapons = {}
	