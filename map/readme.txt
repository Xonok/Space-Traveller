Each map is a json file structured as a key-pair table(dictionary).

The end result is that when interpreted in python or javascript, 
map[x][y] returns a dictionary which contains the following info:
*img: A valid image url from this repo.
*pathing: Whether a tile can be moved into.
*mineable: string with the name of a resource
*amount: how much mineable there is

This info corresponds to a single tile.