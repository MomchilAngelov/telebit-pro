import sys, traceback

def my_excepthook(_type, value, error_traceback):
	print("*" * 50)
	print("The type of the exception is: ", _type)
	print("The value of the exception is: ", value)
	print("The traceback is: ", error_traceback)
	
	for exception_line in traceback.format_exception(_type, value, error_traceback):
		print(exception_line)

	print("*" * 50)

def greenletException(greenlet):
	print("*" * 50)
	print("Error in greenlet: ", greenlet)
	print("*" * 50)

sys.excepthook = my_excepthook

if __name__ == "__main__": 
	def abc(a, b):
		print(a/b)
	
	a = 15
	b = 202

	#abc(a)
	try:
		abc(a)
	except Exception as e:
	 	print(e)
	abc(a, b)

