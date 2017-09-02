'''
get the embedded words from the file 'glove.6B.300d.txt'

return: the word_dict , key=word, value=vector
'''


def build_dict():
	vector_dict = {}
	f = open('glove.6B.300d.txt','r')
	while 1:
		line = file.readline()
		vector = []
		splits = line.split()
		for s in splits[1:]:
			vector.append(float(s))
		vector_dict[splits[0]] = vector
	return vector_dict