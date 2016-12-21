def func1():
	print("Hello from func1")

def func2():
	print("Hello from func2")

def func3():
	print("Hello from func3")

def func4():
	print("Hello from func4")

def executor(function):
	function()

executor(func1)
executor(func2)
executor(func3)
executor(func4)
