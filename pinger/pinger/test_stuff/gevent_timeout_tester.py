import gevent
from gevent import Timeout

time_to_wait = 3 # seconds

class TooLong(Exception):
	

with Timeout(time_to_wait, TooLong):
	gevent.sleep(5)
