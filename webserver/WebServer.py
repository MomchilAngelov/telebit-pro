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
	server_socket.listen(5)
except Exception as e:
	print(e)
	sys.exit(1)

server_socket_wrapped = MySocketWrapper(server_socket)

print("Socket is waiting for connection on 127.0.0.1:80/")

inputs = [server_socket_wrapped]
outputs = []
exceptions = []

try:
	while inputs:
		try:
			readable, writable, exceptional = select.select(inputs, outputs, [], 120)
		except Exception as e:
			print(e)
			continue

		for socket_wrapped in readable:
			if socket_wrapped is server_socket_wrapped:
				try:
					connection, client_address = server_socket_wrapped.socket.accept()
					#print(connection)
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
					continue

				new_socket_wrapped = MySocketWrapper(connection)
				inputs.append(new_socket_wrapped)

			else:
				result = socket_wrapped.read()
				if result == CLOSE_CONNECTION:
					inputs.remove(socket_wrapped)
					outputs.append(socket_wrapped)

				if result == KILL_CONNECTION:
					inputs.remove(socket_wrapped)


		for socket_wrapped in writable:
			result = socket_wrapped.write()

			if result == CLOSE_CONNECTION:
				outputs.remove(socket_wrapped)

except KeyboardInterrupt as e:
	print("Shutting server down...")
	server_socket_wrapped.close()
	print("Server is shut down...")