import itertools

def insideUniquePaths(unqPaths, path1, path2):
	counter = 0
	for unique in unqPaths:
		if (unique[0] == path1 and unique[1] == path2) or (unique[1] == path1 and unique[0] == path2):
				return counter
		counter += 1
	return -1

uniquePaths = []

numberOfVillages, numberOfPaths = input('numberOfVillages, numberOfPaths: ').split(' ')


for inputPaths in range(int(numberOfPaths)):
	currentPathFirst, currentPathSecond, currentSpeed = input('currentPathFirst, currentPathSecond, currentSpeed: ').split(' ')
	idx = insideUniquePaths(uniquePaths, currentPathFirst, currentPathSecond)
	if idx == -1:
		uniquePaths.append([currentPathFirst, currentPathSecond, [int(currentSpeed)]])
	else:
		uniquePaths[idx][2].append(int(currentSpeed))


speedList = []
for path in uniquePaths:
	speedList.append(path[2])

paths = list(itertools.product(*speedList))

result = []
final = []

print()
print()

for path in paths:
	print(path)
	minSpeed = min(path)
	maxSpeed = max(path)

	print('min: ', minSpeed)
	print('max: ', maxSpeed)

	difference = maxSpeed - minSpeed
	result.append([difference, minSpeed, maxSpeed])


result.sort()

final.append(result[0])
for pathData in result:
	if final[-1][0] == pathData[0]:
		final.append(pathData)
	else:
		break

#print(min(final))