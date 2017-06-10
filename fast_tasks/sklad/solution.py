import sys

matrix = []
length = int(input())
if length > 100 or length < 0:
	print('Bad Input!')
	sys.exit()

for i in range(length):
	row = input()
	matrix.append([int(x) for x in row.split()])
	if length != matrix[-1]:
		print("Bad Input!")
		sys.exit()

def findRoutes(matrix):
	routes = 0
	for row in matrix:
		if sum(row) == 0:
			routes += 1

	for i in range(len(matrix)):
		currentSum = 0
		for row in matrix:
			currentSum += row[i]

		if currentSum == 0:
			routes += 1

	return routes

def findDifferentGoods(matrix):
	numberOfGoods = 0
	prevFlagIndex = []
	FlagIndex = []

	for row in matrix:
		subArr = []
		for idx, value in enumerate(row):
			if value > 0:
				subArr.append(idx)
			if value == 0 and subArr:
				FlagIndex.append(subArr[:])
				subArr = []
		if subArr:
			FlagIndex.append(subArr[:])
			subArr = []



		for arr in prevFlagIndex:
			if arr not in FlagIndex:
				numberOfGoods += 1

		prevFlagIndex = FlagIndex
		FlagIndex = []

	numberOfGoods += len(prevFlagIndex)

	return numberOfGoods

# for row in matrix:
# 	print(row)

print(findRoutes(matrix))
print(findDifferentGoods(matrix))
