from SPARQLWrapper import SPARQLWrapper, JSON
import numpy as np
uri_subject_prefix = 'http://elite.polito.it/ontologies/eupont-ifttt.owl#'
get_trigger_p = '<http://elite.polito.it/ontologies/eupont.owl#offerTrigger>'
uri_object_prefix = 'http://elite.polito.it/ontologies/eupont-ifttt.owl#'
get_action_p = '<http://elite.polito.it/ontologies/eupont.owl#offerAction>'

test_predict = {'trigger_chan':'Gmail', 'trigger_func': 'Email.Any New Mail in Inbox', 'action_chan': 'Email', 'action_func': 'Gmail.Send an Email'}
# Try to autofix trigger
def editDis(word1,word2):
	m,n = len(word1), len(word2)
	dp = [[0 for _ in range(n+1)] for _ in range(m+1)]
	for i in range(m+1):
		dp[i][0]=i
	for j in range(n+1):
		dp[0][j]=j
	for i in range(1,m+1):
		for j in range(1,n+1):
			dp[i][j] = min(dp[i-1][j-1] + (0 if word1[i-1] == word2[j-1] else 1),
						dp[i-1][j] + 1,
						dp[i][j-1] + 1,
						)
	
	return dp[m][n]

def autoFix(predict, prev_probs, index, user_chan_list):
	
	# No previous probs, return itself
	if prev_probs == []:
		return predict

	result = predict
	t_c = predict['trigger_chan']
	t_f = predict['trigger_func']
	a_c = predict['action_chan']
	a_f = predict['action_func']

# if channel is not in user channel list, change it to the nearest in the list
# here use the channel's category in the graph
	if not (t_c in user_chan_list):
		query_str = """
			SELECT ?object
			WHERE {{ <{}{}> <http://elite.polito.it/ontologies/eupont.owl#hasCategory> ?object}}
		""".format(uri_subject_prefix, "".join(filter(str.isalnum, t_c.lower())))
		query = SPARQLWrapper('http://202.120.40.28:4460/ifttt/query')
		query.setQuery(query_str)
		query.setReturnFormat(JSON)
		query_result = query.query().convert()
		cat_t_c = query_result['results']['bindings'][0]['object']['value']
		
		# if channel has been changed, then set probs to 1, prevent it be changed again	
		changed = 0
		for each in user_chan_list:
			query_str = """
				SELECT ?object
				WHERE {{ <{}{}> <http://elite.polito.it/ontologies/eupont.owl#hasCategory> ?object}}
			""".format(uri_subject_prefix, "".join(filter(str.isalnum, each.lower())))
			query.setQuery(query_str)
			query_result = query.query().convert()
			cat_cur = query_result['results']['bindings'][0]['object']['value']
			if cat_t_c == cat_cur:
				t_c = each
				prev_probs[0][index] = 1
				changed = 1
				break
		
		# most user only has 2 channel, as (trigger, action)
		# if didn't find a suitable channel to change to, use the first one in the list
		if not changed:
			t_c = user_chan_list[0]

	# same for action channel
	if not (a_c in user_chan_list):
		query_str = """
			SELECT ?object
			WHERE {{ <{}{}> <http://elite.polito.it/ontologies/eupont.owl#hasCategory> ?object}}
		""".format(uri_subject_prefix, "".join(filter(str.isalnum, a_c.lower())))
		query = SPARQLWrapper('http://202.120.40.28:4460/ifttt/query')
		query.setQuery(query_str)
		query.setReturnFormat(JSON)
		query_result = query.query().convert()
		cat_a_c = query_result['results']['bindings'][0]['object']['value']
		changed = 0
		for each in user_chan_list:
			query_str = """
				SELECT ?object
				WHERE {{ <{}{}> <http://elite.polito.it/ontologies/eupont.owl#hasCategory> ?object}}
			""".format(uri_subject_prefix, "".join(filter(str.isalnum, each.lower())))
			query.setQuery(query_str)
			query_result = query.query().convert()
			cat_cur = query_result['results']['bindings'][0]['object']['value']
			if cat_a_c == cat_cur:
				a_c = each
				prev_probs[1][index] = 1
				changed = 1
				break

		if not changed:
			a_c = user_chan_list[1]

# if function does not belong to channel, fix them according to the probs
	if t_c != t_f.split('.')[0:-1]:
		if np.mean(prev_probs[0][index]) > np.mean(prev_probs[1][index]):
		# channel better than function
			result['trigger_chan'] = t_f.split('.')[0:-1]
		
		else:
		# function better than channel
			trigger_func_entity = '<http://elite.polito.it/ontologies/eupont-ifttt.owl#trigger{}{}>'.format(t_c.lower(), t_f.replace(' ', '').lower())
			query_str = """
				SELECT ?object
				WHERE {{ {} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?object }}
			""".format(trigger_func_entity)
			query = SPARQLWrapper('http://202.120.40.28:4460/ifttt/query')
			query.setQuery(query_str)
			query.setReturnFormat(JSON)
			query_result = query.query().convert()
			t_f_type = query_result['results']['bindings'][1]['object']['value']
			
			result['trigger_chan'] = t_c
			query_str = """
				SELECT ?object 
				WHERE {{ <{}{}> {} ?object }}
			""".format(uri_subject_prefix, "".join(filter(str.isalnum, t_c.lower())), get_trigger_p)
			query.setQuery(query_str)
			query.setReturnFormat(JSON)
			query_result = query.query().convert()
			str_list = [each['object']['value'] for each in query_result['results']['bindings']]
		

			t_f_result = ''
			try:
				# try to fix function with 'type'
				func_type_list = []
				for each in str_list:
					query_name_str = """
						SELECT ?object
						WHERE {{ <{}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?object }}
					""".format(each)
					query.setQuery(query_name_str)
					query_result = query.query().convert()

					func_type_list.append(query_result['results']['bindings'][1]['object']['value'])
				for	i, e in enumerate(func_type_list):
					if e == t_f_type:
						result_str = str_list[i]
						query_str = """
							SELECT ?object
							WHERE {{ <{}> <http://elite.polito.it/ontologies/eupont-ifttt.owl#name> ?object}}
						""".format(result_str)
						query.setQuery(query_str)
						query_result = query.query().convert()
						t_f_result = query_result['results']['bindings'][0]['object']['value']
			except Exception:
				# use edit distance for fixing
				func_name_list = []
				for each in str_list:
					query_name_str = """
						SELECT ?object
						WHERE {{ <{}> <http://elite.polito.it/ontologies/eupont-ifttt.owl#name> ?object }}
					""".format(each)
					query.setQuery(query_name_str)
					query_result = query.query().convert()
					func_name_list.append(query_result['results']['bindings'][0]['object']['value'])
            
					t_f = t_f.split('.')[-1]
					min_dis = 99

					for i in func_name_list:
						try:
							dis = editDis(t_f, i)
						except IndexError:
							print t_f, i
							dis = 99

						if dis <= min_dis:
							min_dis = dis
							t_f_result = i
			
			result['trigger_func'] = '{}.{}'.format(t_c,t_f_result)
	
	if a_c != a_f.split('.')[0:-1]:
		if np.mean(prev_probs[2][index]) > np.mean(prev_probs[3][index]):
	
			result['action_chan'] = a_f.split('.')[0:-1]
	
		else:
			action_func_entity = '<http://elite.polito.it/ontologies/eupont-ifttt.owl#action{}{}>'.format(t_c.lower(), t_f.replace(' ', '').lower())
			query_str = """
				SELECT ?object
				WHERE {{ {} <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?object }}
			""".format(trigger_func_entity)
			query = SPARQLWrapper('http://202.120.40.28:4460/ifttt/query')
			query.setQuery(query_str)
			query.setReturnFormat(JSON)
			query_result = query.query().convert()
			a_f_type = query_result['results']['bindings'][1]['object']['value']


			result['action_chan'] = a_c
			query_str = """
				 SELECT ?object
			     WHERE {{ <{}{}> {} ?object }}
			""".format(uri_subject_prefix, "".join(filter(str.isalnum, a_c.lower())), get_action_p)
			query = SPARQLWrapper('http://202.120.40.28:4460/ifttt/query')
			query.setQuery(query_str)
			query.setReturnFormat(JSON)
			query_result = query.query().convert()
			str_list = [each['object']['value'] for each in query_result['results']['bindings']]

			a_f_result = ''
			try:
				# try to fix function with 'type'
				func_type_list = []
				for each in str_list:
					query_name_str = """
						SELECT ?object
						WHERE {{ <{}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?object }}
					""".format(each)
					query.setQuery(query_name_str)
					query_result = query.query().convert()

					func_type_list.append(query_result['results']['bindings'][1]['object']['value'])
				for	i, e in enumerate(func_type_list):
					if e == t_f_type:
						result_str = str_list[i]
						query_str = """
							SELECT ?object
							WHERE {{ <{}> <http://elite.polito.it/ontologies/eupont-ifttt.owl#name> ?object}}
						""".format(result_str)
						query.setQuery(query_str)
						query_result = query.query().convert()
						a_f_result = query_result['results']['bindings'][0]['object']['value']
			except Exception:
				# use edit distance for fixing
				func_name_list = []
				for each in str_list:
					query_name_str = """
						SELECT ?object
						WHERE {{ <{}> <http://elite.polito.it/ontologies/eupont-ifttt.owl#name> ?object }}
					""".format(each)
					query.setQuery(query_name_str)
					query_result = query.query().convert()
					func_name_list.append(query_result['results']['bindings'][0]['object']['value'])
            
					a_f = a_f.split('.')[-1]
					min_dis = 99

					for i in func_name_list:
						try:
							dis = editDis(a_f, i)
						except IndexError:
							print a_f, i
							dis = 99

						if dis <= min_dis:
							min_dis = dis
							a_f_result = i
			result['action_func'] = '{}.{}'.format(a_c, a_f_result)
	
	for each in result.keys():
		if type(result[each]) == type([]):
			result[each] = result[each][0]
	
	return result
