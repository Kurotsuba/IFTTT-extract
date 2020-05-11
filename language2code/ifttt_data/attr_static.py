import pickle

data = pickle.load(open('coreresults_attr.pkl', 'rb'))

total = 0
trigger = 0
action = 0
for i in range(0, 200000, 10000):
	if data[i]['trigger_attribute'] == [] and data[i]['action_attribute'] == []:
		continue

	total += 1
	print("description: {}".format(data[i]['description']))
	print("trigger attributes: {}".format(data[i]['trigger_attribute']))
	print("action attributes: {}".format(data[i]['action_attribute']))
	f_type = input("which type? 0 for neither, 1 for trigger, 2 for action, 3 for both:\n")
	if f_type == '1':
		trigger += 1
	if f_type == '2':
		action += 1
	if f_type == '3':
		trigger += 1
		action += 1


print("End of process")
print("total: {}, trigger: {}, action: {}".format(total, trigger, action))
