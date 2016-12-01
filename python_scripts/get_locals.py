data = {"name1": 1, "name2": 2}

my_data = locals().copy()

if "data" in my_data:
	print(my_data["data"])