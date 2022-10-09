import random

def dice(amount,sides):
	sum = 0
	for i in range(amount):
		sum += random.randint(1,sides)
	return sum
	
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
		"0,1": 0,
		"1,1": 45,
		"1,0": 90,
		"1,-1": 135,
		"0,-1": 180,
		"-1,-1": 225,
		"-1,0": 270,
		"-1,1":315
	}
	return directions[delta]
def add(table,item,amount):
	if not item in table:
		table[item] = 0
	table[item] += amount
def get(table,item):
	if not item in table:
		return 0
	return table[item]