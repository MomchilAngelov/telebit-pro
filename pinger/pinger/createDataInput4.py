"""
{
  "varsion": "3.0",
  "applications": {
    "icmp_pings3": {
      "name": "IMCP3 pings",
      "items": {
        "1": {
          "packet_interval" : 1.00,
          "packets_count" : 5,
          "address" : "https://kongregate.com/"
        },
        "2": {
          "packet_interval" : 0.25,
          "packets_count" : 5,
          "address" : "https://twitter.com/"
        },
        "3": {
          "packet_interval": 0.2,
          "packets_count": 5,
          "address": "http://facebook.com"
        },
        "4": {
          "packet_interval": 0.2,          
          "packets_count": 5,
          "address": "http://northshire.com"
        },
        "5": {
          "packet_interval": 0.2,          
          "packets_count": 5,
          "address": "whitekingdom.com"
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
dict_to_json['applications']['icmp_pings3'] = {}

dict_to_json['applications']['icmp_pings3']['name'] = "IMCP3 pings"
dict_to_json['applications']['icmp_pings3']['items'] = {}

domain_count = 3000

arr = dict_to_json['applications']['icmp_pings3']['items']
with open('test_Data/raw_domains_10k.txt') as f:
	for idx, domainName in enumerate(f):
		arr[str(idx)] = {
			"packet_interval": 0.2,
			"packets_count": 5,
			"address": domainName.strip()
		}

		if idx == domain_count:
			break

with open('test_Data/input4.json', 'w') as f:
	json.dump(dict_to_json, f, indent = 4)