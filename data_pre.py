import MySQLdb
import re
import graph_tool as gt 
from graph_tool import centrality
import os
from os import listdir
from os.path import isfile, join
import shutil
import numpy as np
import math
from math import log
import word2vec



top5_mids = []

# build the dicts of edge
onehop2extracted = {}
extracted2onehop = {}
onehop_label2mid = {}
extracted_label2mid = {}

predCounts = np.load('FullpredCounts.npy').item()
db = MySQLdb.connect(host="image.eecs.yorku.ca",    # your host, usually localhost
                     port=3306,
                     user="read_only_user",         # your username
                     passwd="P@ssw0rd",  # your password
                     db="freebase_mysql_db")        # name of the data base
cur = db.cursor()
# pre-process of the data

# make directory including current_nodes, onehop_nodes, analysis of nodes
separate_dir = "/home/kevinj22/lydia/articles/separate/"
articles_dir = "/home/kevinj22/lydia/articles/alternativeArticleDB_Unique/"
graphs_dir = "/home/kevinj22/lydia/articles/lydia_NoLOCorGPE_Weighted/Unfiltered_No_LOC_Top5_FB20_Stemmed_SimCheck_1Hop_NoLeaves/"
#files = [ f for f in listdir(articles_dir) if isfile(join(articles_dir, f))]

'''
#move the graph file and original text file to sub directory
for f in files:
	os.mkdir(separate_dir + f)
	shutil.move(articles_dir + f, separate_dir + f + '/' + f)
	shutil.move(graphs_dir + f + ".gt", separate_dir + f + '/' + f + ".gt")

files = [ f for f in listdir(separate_dir) ]
articles_path = []
for i in files:
	articles_path.append(separate_dir + f + '/' + f)

'''
# use one of the file to try

files = [ f for f in listdir(separate_dir) if not isfile(join(separate_dir, f))]
articles_path = []
for f in files:
	articles_path.append(separate_dir + f + '/' + f)

f_article_path = open("/home/kevinj22/lydia/articles/separate/article_path.txt", "w+")
f_article_path.write(str(articles_path))
f_article_path.close()


for choice_no in range(0, len(articles_path)):

	tmp_file = files[choice_no]
	file_path = articles_path[choice_no]
	g = gt.load_graph(file_path + ".gt")
	original_edges = g.get_edges()
	extracted_entites = []
	onehop_entites = []
	frequency_dict = {}
	# save the graph
	f = open(file_path + "_graph.txt", 'w+')

	#f_result = open(file_path + "_results.txt", "w+")



	# get the labels of extracted entites and onehop entities
	for e in original_edges:
		if e[0] not in extracted_entites:
			extracted_entites.append(e[0])
			frequency_dict[e[0]] = 1
			extracted2onehop[e[0]] = []
			extracted2onehop[e[0]].append(e[1])
		else:
			frequency_dict[e[0]] = frequency_dict[e[0]] + 1
			extracted2onehop[e[0]].append(e[1])
		if e[1] not in onehop_entites:
			onehop_entites.append(e[1])
			frequency_dict[e[1]] = 1
			onehop2extracted[e[1]] = []
			onehop2extracted[e[1]].append(e[0])
		else:
			frequency_dict[e[1]] = frequency_dict[e[1]] + 1
			onehop2extracted[e[1]].append(e[0])
		

		f.write(str(e[0]))
		f.write(" ")
		f.write(str(e[1]))
		f.write("\n")

	f.close()


	# save all the mids of all, current entities, onehop entities
	l2v = g.graph_properties['lToV']
	#print file_path + "_all_nodes.txt"
	f = open(file_path + "_all_nodes.txt", "w+")
	f_1 = open(file_path + "_current.txt", "w+")
	f_2 = open(file_path + "_onehop.txt", "w+")


	extracted_mids = []
	for l in l2v:
		f.write(str(l))
		f.write(' ')
		f.write(str(l2v[l]))
		f.write("\n")
		if l2v[l] in extracted_entites:
			extracted_label2mid[l2v[l]] = l
			f_1.write(str(l))
			f_1.write(' ')
			f_1.write(str(l2v[l]))
			f_1.write('\n')
		if l2v[l] in onehop_entites:
			onehop_label2mid[l2v[l]] = l
			f_2.write(str(l))
			f_2.write(' ')
			f_2.write(str(l2v[l]))
			f_2.write('\n')


	f.close()
	f_1.close()
	f_2.close()



	# save the frequency of the current and onehop entities
	# the frequency file is not sorted
	# frequency_dict = sorted(frequency_dict.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)


	#print l2v
	#print frequency_dict
	weights = []
	freebase_frequency = []
	for w in frequency_dict:
		weights.append(frequency_dict[w])
		mid = l2v.keys()[l2v.values().index(w)]
		mid = "<http://rdf.freebase.com/ns/" + mid + ">"
		cur.execute("select `min_row_id`, `max_row_id` from `freebase-onlymid_-_fb-id2row-id` where `freebase_id` = '{0}';".format(mid))
		rows = cur.fetchall()
		min_row_id = rows[0][0]
		max_row_id = rows[0][1]
		freebase_frequency.append(max_row_id - min_row_id)



	for i in range(len(weights)):
		weights[i] = weights[i] / float(freebase_frequency[i])
	print weights
	f = open(file_path + "_tf_weights.txt", "w+")

	for w in weights:
		f.write(str(w))
		f.write('\n')
	f.close()



	#print "The length of frequency_dict", len(frequency_dict)
	f_1 = open(file_path + "_frequency_current.txt", "w+")
	f_2 = open(file_path + "_frequency_onehop.txt", "w+")
	for ee in frequency_dict:
		#print ee
		if ee in extracted_entites:
			f_1.write(str(ee))
			f_1.write(' ')
			f_1.write(str(frequency_dict[ee]))
			f_1.write('\n')
		else:
			f_2.write(str(ee))
			f_2.write(' ')
			f_2.write(str(frequency_dict[ee]))
			f_2.write('\n')

	f_1.close()
	f_2.close()
