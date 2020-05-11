import pickle

class IftttFunction:
	def __init__(self, name, URI, attr_list, has_attribute):
		self.name = name
		self.has_attribute = has_attribute
		self.attr_list = attr_list
		self.URI = URI

with open('chan_attr_graph.pkl', 'rb') as f:
    chan_dict = pickle.load(f)

data_list = []
result_list = []
with open('coreresults.tsv') as f:
    f_data = f.readlines()
    for each in f_data:
        data = each.split('\t')
        tri_chan = data[5]
        tri_func = data[6]
        act_chan = data[8]
        act_func = data[9]
        tri_attr = []
        act_attr = []
        tri_has_attr = False
        act_has_attr = False

        tri_func_list = chan_dict[tri_chan]
        for func in tri_func_list:
            if func.name == tri_func:
                tri_attr = func.attr_list
                tri_has_attr = func.has_attribute
        
        act_func_list = chan_dict[act_chan]
        for func in act_func_list:
            if func.name == act_func:
                act_attr = func.attr_list
                act_has_attr = func.has_attribute
        
        data_list.append((tri_has_attr, act_has_attr))

        result = {
            'description': data[1],
            'user': data[2],
            'trigger_channel': data[5],
            'trigger_function': data[6],
            'trigger_attribute': tri_attr,
            'action_channel': data[8],
            'action_function': data[9],
            'action_attribute': act_attr
        }

        result_list.append(result)

total = len(data_list)
act_attr = 0
tri_attr = 0
for each in data_list:
    if each[0]:
        tri_attr += 1
    if each[1]:
        act_attr += 1

print('trigger_attr: {}, action_attr: {}, total: {}'.format(tri_attr, act_attr, total))
with open('coreresults_attr.pkl', 'wb') as f:
    pickle.dump(result_list, f)

