import pickle
from SPARQLWrapper import SPARQLWrapper, JSON

class IftttFunction:
	def __init__(self, name, URI, attr_list, has_attribute):
		self.name = name
		self.has_attribute = has_attribute
		self.attr_list = attr_list
		self.URI = URI

channel_dict = {}
with open('channel_dict.tsv') as f:
	for each in f.readlines():
		if each[0] != '\t':
			chan_name = each.replace('\t', '').replace('\n', '')
			channel_dict[chan_name] = []

query = SPARQLWrapper('http://202.120.40.28:4460/ifttt/query')
query.setReturnFormat(JSON)

for each in channel_dict.keys():
	chan_uri = "<{}#{}>".format('http://elite.polito.it/ontologies/eupont-ifttt.owl', "".join(filter(str.isalnum, each.lower())))
	query_trigger_str = """
		SELECT ?object 
		WHERE {{ {} <http://elite.polito.it/ontologies/eupont.owl#offerTrigger> ?object }}
	""".format(chan_uri)
	query_action_str = """
		SELECT ?object
		WHERE {{ {} <http://elite.polito.it/ontologies/eupont.owl#offerAction> ?object }}
	""".format(chan_uri)

	query.setQuery(query_trigger_str)
	trigger_result = query.query().convert()
	trigger_bindings = trigger_result['results']['bindings']

	query.setQuery(query_action_str)
	action_result = query.query().convert()
	action_bindings = action_result['results']['bindings']

	func_uri_list = ['<{}>'.format(i['object']['value']) for i in trigger_bindings+action_bindings]
	func_list = []
	
	for uri in func_uri_list:
		query_name_str = """
			SELECT ?object
			{{ {} <http://elite.polito.it/ontologies/eupont-ifttt.owl#name> ?object }}
		""".format(uri)
		query.setQuery(query_name_str)
		name_result = query.query().convert()
		try:
			func_name = name_result['results']['bindings'][0]['object']['value']
		except IndexError:
			func_name = uri
		func_uri = uri

		query_attr_str = """
			SELECT ?object
			{{ {} <http://elite.polito.it/ontologies/eupont.owl#offerDetail> ?object }}
		""".format(uri)
		query.setQuery(query_attr_str)
		attr_result = query.query().convert()

		func_attr_list = [item['object']['value'] for item in attr_result['results']['bindings']]
		func_has_attr = False
		if len(func_attr_list) != 0:
			func_has_attr = True
		
		func_list.append(IftttFunction(func_name, func_uri, func_attr_list, func_has_attr))
	
	channel_dict[each] = func_list

with open('readable_attr.csv', 'w') as f:	
	for func_list in channel_dict.values():
		for each in func_list:
			for attr in each.attr_list:
				attr_name = attr.replace(each.URI.replace('#', '#detail').replace('>', '').replace('<', ''), '')
				f.write('{}, {}\n'.format(each.name, attr_name))


		 



