import xml, json

class Outputter():

	def __init__(self, versionNumber, applicationName):
		self.outputDictionary = {}
		self.outputDictionary['version'] = versionNumber
		self.outputDictionary['name'] = applicationName
		self.outputDictionary['applications'] = {}

	def createRootForApplications(self, data, name):
		self.outputDictionary['applications'][data] = {}
		self.outputDictionary['applications'][data]['name'] = name
		self.outputDictionary['applications'][data]['pings'] = {}

	def appendItemToOutputter(self, output):
		rtt = output['rtt']
		packet_loss = output['packet_loss']
		timestamp = output['timestamp']

		try:
			items = self.outputDictionary['applications'][output['application_name']]['pings']
		except Exception as e:
			self.createRootForApplications(data = output['application_name'], name = output['application_name_human_name'])
			items = self.outputDictionary['applications'][output['application_name']]['pings']

		items[output['ip'].strip()+'.rtt'] = {
			'value': rtt, 
			'units': 'ms', 
			'name': '[{0} -> {1}] ICMP ping: packet round trip time'.format(output['ip'], output['address']), 
			'type': 'float', 
			'timestamp': int(timestamp), 
			'domain': output['address'], 
			'requesting_application': output['application_name_human_name']
		}

		items[output['ip'].strip()+'.packet_loss'] = {
			'value': packet_loss,
			'units': '%', 'name': '[{0} -> {1}] ICMP ping: packet loss'.format(output['ip'], output['address']),
			'type': 'float',
			'timestamp': int(timestamp), 
			'domain': output['address'],
			'requesting_application': output['application_name_human_name']
		}

	def appendItemToOutputterHTML(self, output):
		try:
			items = self.outputDictionary['applications'][output['application_name']]['pings']
		except Exception as e:
			self.createRootForApplications(data = output['application_name'], name = output['application_name_human_name'])
			items = self.outputDictionary['applications'][output['application_name']]['pings']
		
		output.pop('application_name')
		output.pop('application_name_human_name')

		items['{0}.packet_loss'.format(output['idx'])] = output

	def getResultInJSON(self):
		return json.dumps(self.outputDictionary, ensure_ascii=False, indent = 4)

	def getResultInXML(self):
		return xml.dom.minidom.parseString(str(dicttoxml(self.outputDictionary, custom_root='root', attr_type=False), 'utf-8')).toprettyxml()

	def getResult(self, outputFormat):
		return eval('self.getResultIn'+ outputFormat.upper() +'()')
