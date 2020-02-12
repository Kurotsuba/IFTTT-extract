import pickle

def getDistance(src, dst):
    rows = len(src) + 1
    cols = len(dst) + 1
    dist = [[0 for x in range(cols)] for x in range(rows)]

    for i in range(1, rows):
        dist[i][0] = i

    for i in range(1, cols):
        dist[0][i] = i
        
    for col in range(1, cols):
        for row in range(1, rows):
            if src[row-1] == dst[col-1]:
                cost = 0
            else:
                cost = 1
            dist[row][col] = min(dist[row-1][col] + 1,
								 dist[row][col-1] + 1,
								 dist[row-1][col-1] + cost)
 
    return dist[rows-1][cols-1]

def main():
	data_dict = {}
	with open('data.pickle', 'rb') as datafile:
		data_dict = pickle.load(datafile)
	description_list = list(data_dict.keys())
	
	target_str = input('get the description')
	min_dist = getDistance(target_str, description_list[0])
	min_description = description_list[0]

	for each in description_list:
		dist = getDistance(target_str, each)
		if dist < min_dist:
			min_dist = dist
			min_description = each
	
	print(data_dict[min_description])
main()


