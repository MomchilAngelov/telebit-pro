import sys

matrix = []
length = int(input())
if length > 100 or length < 0:
	print('Bad Input!')
	sys.exit()

for i in range(length):
	row = input()
	matrix.append([int(x) for x in row.split()])
	if length != len(matrix[-1]):
		print("Bad Input!")
		sys.exit()

def findRoutes(matrix):
	routes = 0
	for row in matrix:
		if sum(row) == 0:
			routes += 1

	#If the matrix is a rectangle instead of a square
	#We need to use the rows length instead of columns length
	for i in range(len(matrix[0])):
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
			elif value == 0 and subArr:
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

def printMatrix(matrix):
	for row in matrix:
		for value in row:
			print(value, ' ', end='')
		print()

#printMatrix(matrix)
print(findRoutes(matrix), findDifferentGoods(matrix))
