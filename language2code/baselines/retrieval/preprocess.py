import pickle
dl = []
with open('turk_public.tsv') as f:
	ds = f.readlines()
	dl = [each[:-1].split('\t') for each in ds]

data_list_des = [[' '.join(each[0].split('-')[1:]),each[2].replace(' ', '_'),each[3].replace(' ', '_'),each[4].replace(' ', '_'),each[5].replace(' ', '_')] for each in dl[1:]]
data_dict = {}
for each in data_list_des:
	data_dict[each[0]] = each

with open('data.pickle', 'wb') as data:
	pickle.dump(data_dict, data)
