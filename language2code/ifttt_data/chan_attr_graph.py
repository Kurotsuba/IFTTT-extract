import pickle
from SPARQLWrapper import SPARQLWrapper, JSON

class IftttFunction:
    def __init__(name, URI):
        self.name = name
        self.has_attribute = False
        self.attr_list = []
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
    chan_uri = "<{}#{}>".format('http://elite.polito.it/ontologies/eupont-ifttt.owl', ''."".join(filter(str.isalnum, each.lower())))
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
    print(func_uri_list)
    exit(0)