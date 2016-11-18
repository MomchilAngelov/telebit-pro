import pymysql.cursors
import sys

conn = pymysql.connect(host='localhost', user='root', password='root', db='ekatte', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
sql = """select naseleni_mesta.name, oblast.name, obstini.name, documents.institution, documents.name, 
region.name, big_region.name from naseleni_mesta 
INNER JOIN obstini ON naseleni_mesta.fk_obshtini=obstini.Alphabetical_code 
INNER JOIN oblast ON obstini.oblast_fk=oblast.Alphabetical_code 
INNER JOIN region ON oblast.region_fk=region.Alphabetical_code 
INNER JOIN big_region ON region.big_alpha_code=big_region.Alphabetical_code 
INNER JOIN documents ON naseleni_mesta.fk_document=documents.id WHERE naseleni_mesta.name LIKE '{0}%'""".format(sys.argv[1])

with conn.cursor() as x:
	try: 				
		x.execute(sql)
		result = x.fetchall()
		
		for row in result:
			print(row)
	except Exception as e:
		print(e)
		conn.rollback()