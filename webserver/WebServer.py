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
	server_socket.listen(15)
except Exception as e:
	print(e)
	sys.exit(1)

server_socket_wrapped = MySocketWrapper(server_socket)

print("Socket is waiting for connection on 127.0.0.1:80/")
print("Buffer reading size: " + str(server_socket_wrapped.buff_size))

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
			# print("*"*150)
			#counter += 1
			#print("big cycle number: {0}!".format(counter))
		except Exception as e:
			print("41: {0}".format(e))
			time.sleep(1)
			continue

		for socket_wrapped in readable:
			if socket_wrapped in writable:
				print("Socket both readable and writable!")
				writable.remove(socket_wrapped)

		for socket_wrapped in readable:
			print(readable)
			if socket_wrapped is server_socket_wrapped:
				try:
					connection, client_address = server_socket_wrapped.socket.accept()
					print("Socket received: {0}".format(connection))
					# counter += 1
					# if counter % 10 == 0:
					# 	print(counter)
				except Exception as e:
					print(e)
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
					outputs.append(socket_wrapped)
					exceptions.append(socket_wrapped)

		for socket_wrapped in writable:
			print(writable)
			result = socket_wrapped.write()
			if result == CLOSE_CONNECTION:
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