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

predCounts = np.load('FullpredCounts.npy').item()
db = MySQLdb.connect(host="image.eecs.yorku.ca",    # your host, usually localhost
                     port=3306,
                     user="read_only_user",         # your username
                     passwd="P@ssw0rd",  # your password
                     db="freebase_mysql_db")        # name of the data base
cur = db.cursor()




# function replace for replacing the original entity with the subject entity

def replace(f_result, splits, subject_entity):
	sentence = splits[3]
	sentence.strip()

	# get the entity in the original sentence
	columns = splits[0].split('/')
	mid = columns[1] + '.' + columns[2]
	mid = "<http://rdf.freebase.com/ns/" + str(mid) + ">"
	cur.execute("select `min_row_id`, `max_row_id` from `freebase-onlymid_-_fb-id2row-id` where `freebase_id` = '{0}';".format(mid))
	rows = cur.fetchall()
	min_row_id = rows[0][0]
	max_row_id = rows[0][1]
	cur.execute("select `<object>` from `freebase-onlymid_-_datadump` where `<predicate>`='<http://rdf.freebase.com/ns/type.object.name>' and `row_id` between '{0}' and '{1}';".format(min_row_id, max_row_id))
	rows = cur.fetchall()
	for d in rows:
		if "@en" in d[0]:
			origin_entity = d[0].strip()
	#origin_entity = rows[0][0].strip()
	index = origin_entity.find('@')
	origin_entity = origin_entity[0:index].replace("\"","")
	origin_entity_lower = origin_entity.lower()
	f_result.write("\nThe original subject of the sentence:\n")
	f_result.write(origin_entity)
	#origin_entity = origin_entity[:int(len(origin_entity)*0.8)]
	#print origin_entity
	splits = sentence.split(' ')
	#print splits
	n = 0
	final_sentence = ""
	'''
	len_origin_entity = len(origin_entity.split(' '))
	if len_origin_entity != 1:
		for i in range(0, len(splits)-len_origin_entity):
			tmp_s = ""
			tmp_s = splits[i:i+len_origin_entity]
	for s in splits:
		if s.lower() in origin_entity.lower():
			final_sentence = final_sentence + ' ' + subject_entity

		else:
			final_sentence = final_sentence + ' ' + s
	'''
	final_sentence = str(splits)
	final_sentence = sentence.replace(origin_entity, subject_entity).replace(origin_entity_lower,subject_entity)
	f_result.write("\nThe generated sentence we got:\n")
	f_result.write(final_sentence)




# function generate_question for generating the questions

def generate_question(f_result, tmp_mid, file_path):
	subject_mid = "<http://rdf.freebase.com/ns/" + str(tmp_mid) + ">"
	cur.execute("select `min_row_id`, `max_row_id` from `freebase-onlymid_-_fb-id2row-id` where `freebase_id` = '{0}';".format(subject_mid))
	rows = cur.fetchall()
	min_row_id = rows[0][0]
	max_row_id = rows[0][1]
	cur.execute("select `<predicate>` from `freebase-onlymid_-_datadump` where `row_id` between '{0}' and '{1}';".format(min_row_id,max_row_id))
	rows = cur.fetchall()
	#print tmp_mid, len(rows)
	predicate_dict = {}
	for tmp_row in rows:
		row = str(tmp_row)
		predCount_row = str(row).replace("('<http://rdf.freebase.com/ns/","")
		predCount_row = predCount_row.replace(">',)","")
		if row not in predicate_dict:
			if predCount_row in predCounts:
				predicate_dict[row] = predCounts[predCount_row]
			else:
				predicate_dict[row] = 1

	#print len(predicate_dict)
	predDict = sorted(predicate_dict.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
	pure_predDict = []
	for p in predDict:
		pure_predDict.append(p[0].replace("('<http://rdf.freebase.com/","").replace(">',)",""))
	predicate = word2vec.choose_predicate(pure_predDict, file_path)
	#print pure_predDict
	#print predDict

	predicate_1 = "<http://rdf.freebase.com/ns/" + predicate + ">"
	predicate_2 = "<http://rdf.freebase.com/key/" + predicate + ">"
	#predicate = "<http://rdf.freebase.com/" + predicate + ">"
	#predicate = predicate.replace("('", "").replace("',)", "")
	print "select * from `freebase-onlymid_-_datadump` where `row_id` between '{0}' and '{1}' where `<predicate>` = '{2}';".format(min_row_id,max_row_id,predicate_1)
	cur.execute("select * from `freebase-onlymid_-_datadump` where `row_id` between '{0}' and '{1}' and `<predicate>` = '{2}';".format(min_row_id,max_row_id,predicate_1))
	rows = cur.fetchall()
	
	if len(rows) == 0 :
		cur.execute("select * from `freebase-onlymid_-_datadump` where `row_id` between '{0}' and '{1}' and `<predicate>` = '{2}';".format(min_row_id,max_row_id,predicate_2))
		rows = cur.fetchall()
		print "select * from `freebase-onlymid_-_datadump` where `row_id` between '{0}' and '{1}' and `<predicate>` = '{2}';".format(min_row_id,max_row_id,predicate_2)
	#print "select * from `freebase-onlymid_-_datadump` where `row_id` between '{0}' and '{1}' and `<predicate>` = '{2}';".format(min_row_id,max_row_id,predicate_2)
	
	#print "select * from `freebase-onlymid_-_datadump` where `row_id` between '{0}' and '{1}' and `<predicate>` = '{2}';".format(min_row_id,max_row_id,predicate)
	print len(rows)
	#print rows

	# origin codes start from here 
	# choose the first line as the single fact 
	fact = str(rows[0])
	subject = fact.split(', ')[0].replace("'",'')[1:]
	predicate = fact.split(', ')[1].replace("'","")
	object = fact.split(', ')[2].replace("'","")
	# get the predicate
	pre_splits = predicate.strip().split('/')
	pre_relation = pre_splits[-1][:-1].replace('.','/')
	predicate = 'www.freebase.com/' + pre_relation
	#print predicate

	# get the subject entity
	cur.execute("select `min_row_id`, `max_row_id` from `freebase-onlymid_-_fb-id2row-id` where `freebase_id` = '{0}';".format(subject))
	rows = cur.fetchall()
	min_row_id = rows[0][0]
	max_row_id = rows[0][1]
	cur.execute("select `<object>` from `freebase-onlymid_-_datadump` where `<predicate>`='<http://rdf.freebase.com/ns/type.object.name>' and `row_id` between '{0}' and '{1}';".format(min_row_id, max_row_id))
	rows = cur.fetchall()

	for d in rows:
		if "@en" in d[0]:
			subject_entity = d[0].strip()
	index = subject_entity.find('@')
	subject_entity = subject_entity[0:index].replace("\"","")



	# get the origin entity
	current = open('/home/kevinj22/lydia/SimpleQuestions_v2/annotated_fb_data_train.txt','r')
	while 1:
		line = current.readline()
		if line == "":
			#f_result.write("\n\nNot found the sentence from SimpleQuestion for the predicate:\n")
			#f_result.write(predicate)
			break
		line = line[:-1]
	# splits[0]: object; splits[1]: predicate; splits[2]: subject; splits[3]: sentence
		splits = line.split('\t')
		# find the same predicate

		origin_predicate = splits[1].strip()
		if predicate == origin_predicate:
			sig = 1
			# here got the subject entity
			f_result.write("\n\n\nSubject entity is :")
			f_result.write(subject_entity)
			f_result.write('\n')
			f_result.write(tmp_mid)
			f_result.write('\n')

			f_result.write("\n\nThe fact and sentence from the SimpleQuestion which matches the fact we found:\n")
			f_result.write(line)
			replace(f_result, splits, subject_entity)
			break
	current.close()




# choose top5 entities based on the centrality
def top5_choose(f_result, centrals, file_path):
	top5_labels = [0,0,0,0,0]
	top5_mids = []
	top5_values = [0.0,0.0,0.0,0.0,0.0]
	count = 0
	for d in centrals:
		if count in l2m_dict and d > top5_values[4]:
			if d > top5_values[3]:
				if d > top5_values[2]:
					if d > top5_values[1]:
						if d > top5_values[0]:
							top5_values[0] = d
							top5_labels[0] = count
						else:
							top5_values[1] = d
							top5_labels[1] = count
					else:
						top5_values[2] = d
						top5_labels[2] = count
				else:
					top5_values[3] = d
					top5_labels[3] = count
			else:
				top5_values[4] = d
				top5_labels[4] = count
		count = count + 1
	#print top5_labels	
	for d in top5_labels:
		#print l2m_dict[d]
		top5_mids.append(l2m_dict[d])

	for d in top5_mids:
		generate_question(f_result, d, file_path)




###########################################################################
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
print files[0]
tmp_file = files[0]
file_path = articles_path[0]
g = gt.load_graph(file_path + ".gt")
original_edges = g.get_edges()
extracted_entites = []
onehop_entites = []
frequency_dict = {}
# save the graph
f = open(file_path + "_graph.txt", 'w+')

f_result = open(file_path + "_results.txt", "w+")

# get the labels of extracted entites and onehop entities
for e in original_edges:
	if e[0] not in extracted_entites:
		extracted_entites.append(e[0])
		frequency_dict[e[0]] = 1
	else:
		frequency_dict[e[0]] = frequency_dict[e[0]] + 1
	if e[1] not in onehop_entites:
		onehop_entites.append(e[1])
		frequency_dict[e[1]] = 1
	else:
		frequency_dict[e[1]] = frequency_dict[e[1]] + 1
	

	f.write(str(e[0]))
	f.write(" ")
	f.write(str(e[1]))
	f.write("\n")

f.close()

# save the frequency of the current and onehop entities
# the frequency file is not sorted
# frequency_dict = sorted(frequency_dict.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)

weights = []
for w in frequency_dict:
	weights.append(frequency_dict[w])
max_weight = max(weights)
for i in range(len(weights)):
	weights[i] = weights[i] / float(max_weight)
#print weights
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

# save all the mids of all, current entities, onehop entities
l2v = g.graph_properties['lToV']
#print file_path + "_all_nodes.txt"
f = open(file_path + "_all_nodes.txt", "w+")
f_1 = open(file_path + "_current.txt", "w+")
f_2 = open(file_path + "_onehop.txt", "w+")
for l in l2v:
	f.write(str(l))
	f.write(' ')
	f.write(str(l2v[l]))
	f.write("\n")
	if l2v[l] in extracted_entites:
		f_1.write(str(l))
		f_1.write(' ')
		f_1.write(str(l2v[l]))
		f_1.write('\n')
	if l2v[l] in onehop_entites:
		f_2.write(str(l))
		f_2.write(' ')
		f_2.write(str(l2v[l]))
		f_2.write('\n')

f.close()
f_1.close()
f_2.close()

###########################################################################



###########################################################################
# calculate the centralities
# get the mids and labels

#file_path = '/home/kevinj22/lydia/articles/separate/0299_3211_The_animal_source_of_the_Ebola_outbreak_in_West_Africa_eludes_scientists/0299_3211_The_animal_source_of_the_Ebola_outbreak_in_West_Africa_eludes_scientists'
f_l2m = open(file_path + '_all_nodes.txt','r')
lines = f_l2m.readlines()
mids = []
labels = []
for line in lines:
	mids.append(line.split(' ')[0])
	labels.append(int(line.split(' ')[-1]))
l2m_dict = dict(zip(labels, mids))
f_l2m.close()



#calculate the weights
f_weights = open(file_path + '_tf_weights.txt','r')
lines = f_weights.readlines()
weights = []
for line in lines:
	weights.append(float(line.strip()))

g = gt.load_graph(file_path + ".gt")
g.vertex_properties["new_weights"] = g.new_vertex_property("double", vals = weights)
f_weights.close()

f_result = open(file_path + "_results.txt", "w+")

# pagerank
f_result.write("\nThis is pagerank:\n")
pr = gt.centrality.pagerank(g, prop = g.vertex_properties['new_weights'], ret_iter = True, max_iter = 30000)
top5_choose(f_result, pr[0], file_path)


# betweenness 
f_result.write("\n\n\n\n\nThis is betweenness:\n")
bt = gt.centrality.betweenness(g, vprop = g.vertex_properties['new_weights'])
#print bt
top5_choose(f_result, bt[0], file_path)


# closeness
f_result.write("\n\n\n\n\nThis is closeness:\n")
cl = gt.centrality.closeness(g, vprop = g.vertex_properties['new_weights'])
#print cl
top5_choose(f_result, cl,file_path)


# eigenvector centrality
f_result.write("\n\n\n\n\nThis is eigenvector centrality:\n")
ev = gt.centrality.eigenvector(g, vprop = g.vertex_properties['new_weights'])
top5_choose(f_result, ev[1], file_path)


# katz
f_result.write("\n\n\n\n\nThis is katz centrality:\n")
kz = gt.centrality.katz(g, vprop = g.vertex_properties['new_weights'])
top5_choose(f_result, kz, file_path)


f_result.close()
'''



# central point dominance
f_result.write("\n\n\n\n\nThis is central_point_dominance:\n")
cpd = gt.centrality.central_point_dominance(g, bt[0])
f_result.write(str(cpd))


# hits
print "\nThis is authority and hub centralities:"
ht = gt.centrality.hits(g)
print ht
top5_choose(ht[1])

# eigentrust
print "\nThis is eigentrust centrality:"
et = gt.centrality.eigentrust(g, bt[1], vprop = g.vertex_properties['new_weights'])
print et
top5_choose(et)

# pervasive trust transitivity
print "\nThis is trust_transitivity:"
#print g.list_properties()
tt = gt.centrality.trust_transitivity(g, bt[1])
print tt
top5_choose(tt)
'''

