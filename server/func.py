import random

def dice(amount,sides):
	amount = int(amount)
	sides = int(sides)
	total = 0
	for i in range(amount):
		total += random.randint(1, sides)
	return total
	
def direction(diff_x,diff_y):
	if abs(diff_x) > abs(diff_y):
		diff_y = 0
	if abs(diff_y) > abs(diff_x):
		diff_x = 0
	diff_x = min(diff_x,1)
	diff_x = max(diff_x,-1)
	diff_y = min(diff_y,1)
	diff_y = max(diff_y,-1)
	delta = str(diff_x)+","+str(diff_y)
	directions = {
		"0,1": 180,
		"1,1": 135,
		"1,0": 90,
		"1,-1": 45,
		"0,-1": 0,
		"-1,-1": 315,
		"-1,0": 270,
		"-1,1": 225
	}
	return directions[delta]
