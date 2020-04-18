import pickle
channel_dict = {}
with open('channel_dict.pkl') as f:
	channel_dict = pickle.load(f)

with open('channel_dict.tsv', 'w') as f:
	for each in channel_dict.keys():
		f.write('{}\t\n'.format(each))
		for d in channel_dict[each]:
			f.write('\t{}\n'.format(d))

