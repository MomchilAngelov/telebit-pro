import json
import urllib.request
import pymysql.cursors
import pycountry

t = list(pycountry.countries)

link = "http://api.geonames.org/searchJSON?country={0}&username=clasingu&maxRows=1000&startRow={1}&orderby=population&cities=cities1000"
conn = pymysql.connect(host='localhost', user='root', password='root', db='api_results', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)


with conn.cursor() as x:
	for country_code in t:
		sql = """INSERT INTO data (country_name, population, longitude, latitude, name) VALUES """
		for k in range(0, 5000, 1000):
			url = link.format(country_code.alpha_2, k)
			print(url)
			f = urllib.request.urlopen(url)
			cities = json.loads(str(f.read(), "utf-8"))

			if "geonames" in cities:
				for city in cities["geonames"]:
					lat = city["lat"]
					lng = city["lng"]
					name = city["name"]
					size = city["population"]
					sql += """(\"{0}\",\"{1}\",\"{2}\",\"{3}\",\"{4}\"),""".format(country_code.name, size, lng, lat, name)
		
		try:
			sql = sql[:-1]
			x.execute(sql)
			conn.commit()
		except Exception as e:
			print(e)
			conn.rollback()
conn.close()
