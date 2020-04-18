import pickle
channel_dict = {}
with open('coreresults.tsv', 'r') as f:
	data = f.readlines()[1:]
	for each in data:
		words = each.split('\t')
		try:
			channel_dict[words[5]].append(words[1])
		except Exception:
			channel_dict[words[5]] = [words[1]]

		try:
			channel_dict[words[8]].append(words[1])
		except Exception:
			channel_dict[words[8]] = [words[1]]

pickle.dump(channel_dict, open('channel_dict.pkl', 'w'))
			
