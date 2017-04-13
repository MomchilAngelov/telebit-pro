"""
{
  "varsion": "3.0",
  "applications": {
    "icmp_pings3": {
      "name": "IMCP3 pings",
      "items": {
       "6": {
          "request_interval": 0.2,          
          "request_count": 5,
          "address": "157.240.122.35",
          
          //optional
          
          "expected_response_code": [500, 200, "ако нашия респонс е тук -> 0% във value, ако не 100%"],
          "expected_headers": [

          ],
          "authorization": "<plain text, в който имаме име и парола, ако върне 401 -> чак тогава гледаме във файла с паролите>"
          "адреса може да има full pathing"
          "няма resolve"
        }
      }
    }
  }
}

"""
import json

dict_to_json = {}
dict_to_json['version'] = "3.0"
dict_to_json['applications'] = {}
dict_to_json['applications']['html_pings3'] = {}

dict_to_json['applications']['html_pings3']['name'] = "HTML pings"
dict_to_json['applications']['html_pings3']['items'] = {}

domain_count = 500

arr = dict_to_json['applications']['html_pings3']['items']
with open('test_Data/raw_domains_10k.txt') as f:
  for idx, domainName in enumerate(f):
    arr[str(idx)] = {
      "request_interval": 0.8,
      "request_count": 5,
      "address": domainName.strip(),
      "expected_response_code": [200, 301, 500, 401],
      "expected_headers": ["Date", "Content-Type"]
    }

    if idx == domain_count:
      break

with open('test_Data/inputHTML.json', 'w') as f:
  json.dump(dict_to_json, f, indent = 4)