with open('coreresults.tsv') as in_f:
	out_f = open('toyresults.tsv', 'w')
	for i in range(20000):
		str_in = in_f.readline()
		out_f.write(str_in)
	out_f.close()

