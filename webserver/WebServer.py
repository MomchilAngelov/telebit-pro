'''
	TO DO LIST:
		Now: Reading till the socket is readable
			Reading till \r\n\r\n
			Reading till timeoout
		Non-blocking read from file
'''

from SocketWrapper import *

try:
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.setblocking(0)
	server_socket.bind((HOST, PORT))
except Exception as e:
	print(e)
	sys.exit(1)
	

try:
	server_socket.listen(1000)
except Exception as e:
	print(e)
	sys.exit(1)

server_socket_wrapped = MySocketWrapper(server_socket)

print("Socket is waiting for connection on {0}".format(server_socket_wrapped.socket))
print("Buffer reading size from socket: " + str(server_socket_wrapped.buff_size))
print("Buffer reading size from file: " + str(server_socket_wrapped.buff_size_file_read))

counter = 0
inputs = [server_socket_wrapped]
outputs = []
exceptions = []

try:
	while inputs:
		# for wrapper, text in zip([outputs, exceptions, inputs], ["output", "exceptions", "inputs"]):
		# 	print(text)
		# 	for socket_wrapped in wrapper:
		# 		print(socket_wrapped)	
		try:
			readable, writable, exceptional = select.select(inputs, outputs, exceptions, 1)
			if DEBUG:
				print("Number of sockets i need to handle: {0}".format(len(readable) + len(writable)))
		except Exception as e:
			if DEBUG:
				print("Select result has exception: {0}".format(e))
			continue

		for socket_wrapped in readable:
			if socket_wrapped in writable:
				print("Socket both readable and writable!")
				writable.remove(socket_wrapped)

		for socket_wrapped in readable:
			if socket_wrapped is server_socket_wrapped:
				try:
					connection, client_address = server_socket_wrapped.socket.accept()
				except Exception as e:
					print("Socket acception: {0}".format(e))
					continue

				try:
					connection.setblocking(0)
					connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
				except Exception as e:
					try:
						connection.close()
					except Exception as e:
						continue
					connection.close()
					continue

				new_socket_wrapped = MySocketWrapper(connection)
				inputs.append(new_socket_wrapped)

			else:
				result = socket_wrapped.read()
				if result == CLOSE_CONNECTION:
					inputs.remove(socket_wrapped)
					if socket_wrapped not in outputs:
						outputs.append(socket_wrapped)

				if result == KILL_CONNECTION:
					inputs.remove(socket_wrapped)

				if result == COULD_BE_EMPTY_OR_SLOW:
					if socket_wrapped not in outputs:
						outputs.append(socket_wrapped)

		for socket_wrapped in writable:
			result = socket_wrapped.write()
			if result == CLOSE_CONNECTION or result == KILL_CONNECTION:
				outputs.remove(socket_wrapped)
				if socket_wrapped in inputs:
					inputs.remove(socket_wrapped)


		for socket_wrapped in exceptional:
			print(exceptional)
			print("Exceptional!")
			print(socket_wrapped)
			counter += 1
			socket_wrapped.close()

			if socket_wrapped in inputs:
				inputs.remove(socket_wrapped)

			if socket_wrapped in outputs:
				inputs.remove(socket_wrapped)
			
except KeyboardInterrupt as e:
	print("Shutting server down...")
	server_socket_wrapped.close()
	print("Server is shut down...")
	print("Number of exceptioned sockets: {0}".format(counter))