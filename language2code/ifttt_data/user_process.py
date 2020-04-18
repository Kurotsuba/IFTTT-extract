import pickle
with open('coreresults.tsv', 'r') as f:
	user_dict = {}
	data = f.readlines()
	for each in data:
		words = each.split('\t')
		user_dict[words[2]] = set()
	for each in data:
		words = each.split('\t')
		user_dict[words[2]].add(words[5])
		user_dict[words[2]].add(words[8])

	pickle.dump(user_dict, open('user_dict.pkl', 'w'))
