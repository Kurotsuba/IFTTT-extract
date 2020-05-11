import pickle

class IftttFunction:
	def __init__(self, name, URI, attr_list, has_attribute):
		self.name = name
		self.has_attribute = has_attribute
		self.attr_list = attr_list
		self.URI = URI

attr_list = []
with open('attr_uri_labeled.csv', 'r') as f:
	l = f.readlines()
	attr_list = [each.split(',')[0] for each in l if each.split(',')[1] == '1']

chan_dict = {}
with open('chan_attr_graph.pkl', 'rb') as f:
	chan_dict = pickle.load(f)
	
with open('toyresults.tsv', 'r') as in_f:
	with open('need_label.csv', 'w') as out_f:
		line = in_f.readline()
		while line:
			write_list = []
			ifwrite = False
			token = line.split('\t')
			trigger_chan = token[5]
			action_chan = token[8]
			trigger_function = token[6]
			action_function = token[9]
			description = token[1]
			for each in chan_dict[trigger_chan]:
				if each.name == trigger_function:
					trigger_function = each
			
			for each in chan_dict[action_chan]:
				if each.name == action_function:
					action_function = each
			
			if trigger_function.has_attribute:
				for each in trigger_function.attr_list:
					if each in attr_list:
						write_list.append(each)

			if action_function.has_attribute:
				for each in action_function.attr_list:
					if each in attr_list:
						write_list.append(each)
			
			if len(write_list) != 0:
				out_f.write('{},{},{},{},{},'.format(description, trigger_chan, trigger_function.name, action_chan, action_function.name))
				for each in write_list:
					out_f.write('{},,'.format(each))
				out_f.write('\n')

			line = in_f.readline()
