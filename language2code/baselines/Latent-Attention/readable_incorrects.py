import pickle
trans_data = pickle.load(open('data_true.pkl'))
l = pickle.load(open('incorrect.pkl'))
word_ids = trans_data['word_ids']
id_words = {}
for each in word_ids.keys():
	id_words[word_ids[each]] = each

trigger_chans = trans_data['labelers']['trigger_chans']
action_chans = trans_data['labelers']['action_chans']
trigger_funcs = trans_data['labelers']['trigger_funcs']
action_funcs = trans_data['labelers']['action_funcs']

result = []
for each in l:
	item = {}
	item['preds'] = [
		list(trigger_chans.inverse_transform([each['preds'][0]]))[0],
		list(trigger_funcs.inverse_transform([each['preds'][1]]))[0],
		list(action_chans.inverse_transform([each['preds'][2]]))[0],
		list(action_funcs.inverse_transform([each['preds'][3]]))[0]
	]
	item['labels'] = [
		list(trigger_chans.inverse_transform([each['labels'][0]]))[0],
		list(trigger_funcs.inverse_transform([each['labels'][1]]))[0],
		list(action_chans.inverse_transform([each['labels'][2]]))[0],
		list(action_funcs.inverse_transform([each['labels'][3]]))[0]
	]
	description = []
	for i in each['ids']:
		try:
			description.append(id_words[i])
		except KeyError:
			pass
	item['des'] = [i for i in description if i != 'to']
	result.append(item)

pickle.dump(result, open('readable_incorrect.pkl', 'w'))
print 'pickle done.'
with open('readable_incorrect.csv', 'w') as f:
	for each in result:
		for i in range(4):
			if each['preds'][i] == each['labels'][i]:
				each['preds'][i] = ''
				each['labels'][i] = ''
		pred_str = ','.join(each['preds'])
		label_str = ','.join(each['labels'])
		des_str = ' '.join(each['des'])
		des_str = des_str.replace(',', '')
		f.write(','.join([des_str, pred_str, label_str]))
		f.write('\n')
print 'csv done.'

