One json file per map, structured as a key-pair table(dictionary).

The end result is that when interpreted in python or javascript, 
map[x][y] returns a dictionary which contains the following info:
*img: A valid image url from this repo.
*pathing: Whether a tile can be moved into.
*mineable: string with the name of a resource
*amount: how much mineable there is

This info corresponds to a single tile.

For a given map:
center is 0,0
1 left of center is -1,0
1 right of center is 1,0
1 up is 0,1
1 down is 0,-1