import pickle

similar_dict = {}
with open('similar_dict.tsv') as f:
	line = f.readline()
	now_key = ''
	while line != '':
		if line[0] != '\t':
			now_key = line[:-2]
			similar_dict[now_key] = []
		else:
			similar_dict[now_key].append(line.split('\t')[1][:-1])

		line = f.readline()

pickle.dump(similar_dict, open('similar_dict.pkl', 'w'))
