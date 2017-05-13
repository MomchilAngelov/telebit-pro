import sys, traceback, time

LOGGER = None

def init(logger):
	global LOGGER
	LOGGER = logger

def my_excepthook(_type, value, error_traceback):
	if _type is KeyboardInterrupt:
		if LOGGER:
			LOGGER.log('Please dont kill the script while its working')
		else:
			print('Please dont kill the script while its working')

	else:
		if LOGGER:
			print('There was an error in the script execution, please try again...')

			LOGGER.log('**************************')
			LOGGER.log(time.strftime('%c'))

			for exception_line in traceback.format_exception(_type, value, error_traceback):
				LOGGER.log(exception_line)
		else:
			for exception_line in traceback.format_exception(_type, value, error_traceback):
				print(exception_line)

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

	abc(a)
	abc(a, b)
