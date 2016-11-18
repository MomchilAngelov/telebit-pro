import csv
import pymysql.cursors

conn = pymysql.connect(host='localhost', user='root', password='root', db='ekatte', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)


# with open("./data/csv/Ek_reg1.csv") as f:
# 	data = csv.reader(f)

# 	i = 0
# 	print("adding data about the big regions!")
# 	for row in data:
# 		if i < 1:
# 			i += 1
# 			continue

# 		code = row[0]
# 		name = row[1]
# 		name = name.replace("\"", "")

# 		with conn.cursor() as x:
# 			sql = """INSERT INTO big_region (Alphabetical_code, name) VALUES ("{0}", "{1}");""".format(code, name)
# 			try:
# 				x.execute(sql)
# 				conn.commit()
# 			except Exception as e:
# 				conn.rollback()

# with open("./data/csv/Ek_reg2.csv") as f:
# 	data = csv.reader(f)

# 	i = 0
# 	print("adding data about the smaller regions!")
# 	for row in data:
# 		if i < 1:
# 			i += 1
# 			continue

# 		code = row[0]
# 		name = row[1]
# 		big_region_code = row[0][:-1]

# 		with conn.cursor() as x:
# 			sql = """INSERT INTO region (Alphabetical_code, name, big_alpha_code) VALUES ("{0}", "{1}", "{2}");""".format(code, name, big_region_code)
# 			try:
# 				x.execute(sql)
# 				conn.commit()
# 			except Exception as e:
# 				conn.rollback()


# with open("./data/csv/Ek_doc.csv") as f:
# 	data = csv.reader(f)

# 	i = 0
# 	print("adding data about the documents!")
# 	for row in data:
# 		if i < 1:
# 			i += 1
# 			continue

# 		doc_id = row[0]
# 		name = row[2]
# 		institution = row[3]
# 		doc_type = row[1]

# 		with conn.cursor() as x:
# 			sql = """INSERT INTO documents (id, type, institution, name) VALUES ("{0}", "{1}", "{2}", "{3}");"""\
# 				.format(doc_id, doc_type, name, institution)
# 			try:
# 				print(sql)
# 				x.execute(sql)
# 				conn.commit()
# 			except Exception as e:
# 				print(e)
# 				conn.rollback()


# with open("./data/csv/Ek_obl.csv") as f:
# 	data = csv.reader(f)

# 	i = 0
# 	print("adding data about the oblasti!")
# 	for row in data:
# 		if i < 1:
# 			i += 1
# 			continue

# 		oblast_id = row[0]
# 		ekatte = row[1]
# 		name = row[2]
# 		region_fk_id = row[3]
# 		document_fk_id = row[4]

# 		with conn.cursor() as x:
# 			sql = """INSERT INTO oblast (Alphabetical_code, ekatte, region_fk, name, fk_document) VALUES ("{0}", {1}, "{2}", "{3}", "{4}");"""\
# 				.format(oblast_id, ekatte, region_fk_id, name, document_fk_id)
# 			try:
# 				print(sql)
# 				x.execute(sql)
# 				conn.commit()
# 			except Exception as e:
# 				print(e)
# 				conn.rollback()


# with open("./data/csv/Ek_obst.csv") as f:
# 	data = csv.reader(f)

# 	i = 0
# 	print("adding data about the obstini!")
# 	for row in data:
# 		if i < 1:
# 			i += 1
# 			continue

# 		obstina_id = row[0]
# 		ekatte = row[1]
# 		name = row[2]
# 		oblast_fk_id = row[0][:-2]
# 		document_fk_id = row[4]
# 		with conn.cursor() as x:
# 			sql = """INSERT INTO obstini (Alphabetical_code, ekatte, oblast_fk, name, fk_document) VALUES ("{0}", {1}, "{2}", "{3}", "{4}");"""\
# 				.format(obstina_id, ekatte, oblast_fk_id, name, document_fk_id)
# 			try:
# 				print(sql)
# 				x.execute(sql)
# 				conn.commit()
# 			except Exception as e:
# 				print(e)
# 				conn.rollback()

# with open("./data/csv/Ek_kmet.csv") as f:
# 	data = csv.reader(f)

# 	i = 0
# 	print("adding data about the kmetstva!")
# 	for row in data:
# 		if i < 1:
# 			i += 1
# 			continue

# 		kmetstvo_id = row[0]
# 		obshtina_fk_id = row[0][:-3]
# 		name = row[1]
# 		ekatte = row[2]
# 		document_fk_id = row[3]
# 		with conn.cursor() as x:
# 			sql = """INSERT INTO kmestva (Alphabetical_code, fk_obshtina, name, fk_document) VALUES ("{0}", "{1}", "{2}", {3});"""\
# 				.format(kmetstvo_id, obshtina_fk_id, name, document_fk_id)
# 			try:
# 				x.execute(sql)
# 				conn.commit()
# 			except Exception as e:
# 				print(sql)
# 				print(e)
# 				conn.rollback()

# with open("./data/csv/Ek_atte.csv") as f:
# 	data = csv.reader(f)

# 	i = 0
# 	error_count = 0
# 	print("adding data about the places!")
# 	for row in data:
# 		if i < 2:
# 			i += 1
# 			continue

# 		ekatte = row[0]
# 		front = row[1]
# 		name = row[2]
# 		fk_obshtina = row[4]
# 		document_fk_id = row[9]
# 		with conn.cursor() as x:
# 			sql = """INSERT INTO naseleni_mesta (ekatte, name, fk_obshtini, fk_document, front) VALUES ({0}, "{1}", "{2}", "{3}", "{4}");"""\
# 				.format(ekatte, name, fk_obshtina, document_fk_id, front)
# 			try:
# 				x.execute(sql)
# 				conn.commit()
# 			except Exception as e:
# 				error_count += 1
# 				print(sql)
# 				print(e)
# 				conn.rollback()

# print("\n"*20)
# print("Number of errors: " + str(error_count))

conn.close()
