import time

class Graph():

	def __init__(self):
		self.nodes = []
		self.paths = []
		self.pathHistories = []
		self.callTime = 0

	def addNode(self, node):
		if node not in self.nodes:
			self.nodes.append(node)

	def addPath(self, path):
		self.paths.append(path)

	def allPathsForNode(self, node):
		paths = []
		for value in self.paths:
			if value.toNode == node or value.fromNode == node:
				paths.append(value)

		return paths

	def getPathByIdx(self, idx):
		return self.paths[idx]

	def getStartingNode(self):
		return self.nodes[0]

	def getAllPaths(self, node, pathHistory):
		paths = self.allPathsForNode(node)

		for path in paths:
			if path in pathHistory:
				continue
			pathHistory.append(path)

			otherNode = path.getOtherNode(node)

			if self.checksAll(pathHistory):
				self.pathHistories.append(pathHistory[:])
			else:
				self.getAllPaths(otherNode, pathHistory[:])

	def getAllPathsIniter(self, node):
		self.startingNode = node
		self.pathHistories = []
		self.getAllPaths(node, [])
		return self.pathHistories

	def checksAll(self, paths):
		visitedNodes = []
		for path in paths:
			if path.toNode not in visitedNodes:
				visitedNodes.append(path.toNode)

			if path.fromNode not in visitedNodes:
				visitedNodes.append(path.fromNode)

		if len(visitedNodes) == len(self.nodes):
			return True

		return False

	def sortPaths(self):
		self.paths = sorted(self.paths, key = lambda x: x.speed)

	def getShortestPath(self):
		self.treePaths = [[] for node in self.nodes]

		for k in range(0, len(self.paths) - len(self.nodes)):
		
			trees = [[node] for node in self.nodes]
			for path in self.paths:
				self.mergeIfRequired(path, trees)

				for idx, tree in enumerate(trees):
					if len(tree) == len(self.nodes):
						return self.treePaths[idx]


	def mergeIfRequired(self, path, trees):
		for i in range(len(trees)):
			for k in range(i + 1, len(trees)):
				if self.connectsTwoTrees(path, trees[i], trees[k]):
					trees[i] = self.mergeTwoTrees(trees[i], trees[k])
					self.treePaths[i] = self.treePaths[i][:] + self.treePaths[k][:] + [path]
					del trees[k]
					del self.treePaths[k]
					return

	def connectsTwoTrees(self, path, treeLeft, treeRight):
		for node in treeLeft:
			if path.fromNode == node or path.toNode == node:
				otherNode = path.getOtherNode(node)
				if otherNode in treeRight:
					return True

		return False

	def mergeTwoTrees(self, treeLeft, treeRight):
		copyRight = treeRight[:]
		copyLeft = treeLeft[:]
		treeLeft = copyRight + copyLeft
		return treeLeft

	def getAdjustent(self, node):
		paths = self.allPathsForNode(node)
		nodes = []
		for path in paths:
			nodes.append(path.getOtherNode(node))

		return nodes


class Path():

	def __init__(self, fromNode, toNode, speed):
		self.fromNode = fromNode
		self.toNode = toNode
		self.speed = speed

	def print(self):
		print('From: ', self.fromNode.number, ' To: ', self.toNode.number, ' Speed: ', self.speed)

	def getOtherNode(self, node):
		if self.toNode == node:
			return self.fromNode

		return self.toNode

	def __str__(self):
		return 'From: {0} To: {1} Speed: {2}'.format(self.fromNode.number, self.toNode.number, self.speed)

	def __repr__(self):
		return self.__str__()

	def __eq__(self, other):
		if self.fromNode == other.fromNode or self.fromNode == other.toNode or self.toNode == other.fromNode or self.toNode == other.toNode:
			return True
		return False

class Node():

	def __init__(self, number):
		self.number = number

	def __eq__(self, other):
		return self.number == other.number

	def __str__(self):
		return str(self.number)

	def __repr__(self):
		return self.__str__()


def maxSpeed(paths):
	return max([path.speed for path in paths])

def minSpeed(paths):
	return min([path.speed for path in paths])

graph = Graph()

numberOfCities, numberOfRoads = (int(x) for x in input().split())
for i in range(numberOfRoads):
	fromCity, toCity, speedLimit = (int(x) for x in input().split())
	
	fromCity = Node(fromCity)
	toCity = Node(toCity)
	path = Path(fromCity, toCity, speedLimit)

	graph.addNode(fromCity)
	graph.addNode(toCity)
	graph.addPath(path)


#find the minimum spanning tree with the kryst
graph.sortPaths()
shortestPath = graph.getShortestPath()

for path in shortestPath:
	print(path)

