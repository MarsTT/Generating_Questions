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

def get_subject_entity(subject_mid):
	# get the subject entity
	cur.execute("select `min_row_id`, `max_row_id` from `freebase-onlymid_-_fb-id2row-id` where `freebase_id` = '{0}';".format(subject_mid))
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
	return subject_entity

# function try to use <subject, object> to find the fact, subject in the onehop entities and object in the extracted entities
def su_ob_fact(f_result, tmp_mid, l2v):
	print "This is function su_ob_fact:"
	print l2v[tmp_mid]
	print onehop2extracted[l2v[tmp_mid]]
	subject_mid = "<http://rdf.freebase.com/ns/" + tmp_mid + ">"
	for o in onehop2extracted[l2v[tmp_mid]]:
		object_mid = "<http://rdf.freebase.com/ns/" + l2v.keys()[l2v.values().index(o)] + ">"
		cur.execute("select `min_row_id`, `max_row_id` from `freebase-onlymid_-_fb-id2row-id` where `freebase_id` = '{0}';".format(subject_mid))
		rows = cur.fetchall()
		min_row_id = rows[0][0]
		max_row_id = rows[0][1]
		cur.execute("select * from `freebase-onlymid_-_datadump` where `row_id` between '{0}' and '{1}' and `<object>` = '{2}';".format(min_row_id, max_row_id, object_mid))
		rows = cur.fetchall()
		if len(rows) > 0:
			print rows
			subject_entity = get_subject_entity(subject_mid)
			predicate = rows[0][1]
			predicate = predicate.replace("<http://rdf.freebase.com/ns/", "").replace(">","").replace(".","/")
			predicate = "www.freebase.com/" + predicate
			current = open('/home/kevinj22/lydia/SimpleQuestions_v2/annotated_fb_data_train.txt','r')
			while 1:
				line = current.readline()
				if line == "":
					break
				line = line[:-1]
				splits = line.split('\t')
				origin_predicate = splits[1].strip()
				if predicate == origin_predicate:
					f_result.write("\n\n\nSubject entity is :")
					f_result.write(subject_entity)
					f_result.write('\n')
					f_result.write(tmp_mid)
					f_result.write('\n')

					f_result.write("\n\nThe fact and sentence from the SimpleQuestion which matches the fact we found:\n")
					f_result.write(line)
					replace(f_result, splits, subject_entity)
					break
			return 1

	return 0
	




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
	# origin_entity = rows[0][0].strip()
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
	f_result.write('\n\n')




# function generate_question for generating the questions

def generate_question(f_result, tmp_mid, file_path, l2v):
	
	if l2v[tmp_mid] in onehop_label2mid.keys():
		if su_ob_fact(f_result, tmp_mid, l2v) == 1:
			return
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

	'''
	# using dict to choose predicate
	predicate_no = len(predDict) - int(math.log(len(predDict), 2) ** 2)
	predicate = predDict[predicate_no][0].replace("('","").replace("',)","")
	print "select * from `freebase-onlymid_-_datadump` where `row_id` between '{0}' and '{1}' where `<predicate>` = '{2}';".format(min_row_id,max_row_id,predicate)
	cur.execute("select * from `freebase-onlymid_-_datadump` where `row_id` between '{0}' and '{1}' and `<predicate>` = '{2}';".format(min_row_id,max_row_id,predicate))
	rows = cur.fetchall()
	#print rows
	'''
	
	# using word2vec choose predicate
	predicate = word2vec.choose_predicate(pure_predDict, file_path)


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
	#print len(rows)
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

	# for word2vec choose
	#predicate = 'www.freebase.com/' + pre_relation
	
	# for dict choose
	predicate = 'www.freebase.com/' + pre_relation.replace('ns/','').replace('key/', '')

	print predicate

	'''
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
	'''

	subject_entity = get_subject_entity(subject_mid)


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
def top5_choose(f_result, centrals, file_path, l2v):
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
	print top5_labels	
	for d in top5_labels:
		#print l2m_dict[d]
		top5_mids.append(l2m_dict[d])

	for d in top5_mids:
		generate_question(f_result, d, file_path, l2v)


def get_top5_index(need_sort):
	top5_labels = [0,0,0,0,0]
	top5_values = [0.0,0.0,0.0,0.0,0.0]
	count = 0
	for d in need_sort:
		if d > top5_values[4]:
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

	return top5_labels

###########################################################################



###########################################################################
# calculate the centralities
# get the mids and labels


# get article list
separate_dir = "/home/kevinj22/lydia/articles/separate/"

files = [ f for f in listdir(separate_dir) if not isfile(join(separate_dir, f))]
f_article_path = open('/home/kevinj22/lydia/articles/separate/article_path.txt','r')
tmp_content = f_article_path.read().replace('[','').replace(']','')

articles_path = tmp_content.split(', ')
for i in range(0, len(articles_path)):
	articles_path[i] = articles_path[i].replace('\'','')
f_article_path.close()

choice_no = 110
file_path = articles_path[choice_no].replace('\"', '').replace('\'','\\\'').replace(',','\,')




f_result = open(file_path + "_results.txt", "w+")



extracted_entites = []
onehop_entites = []
frequency_dict = {}

# file _graph.txt
g = gt.load_graph(file_path + ".gt")
original_edges = g.get_edges()
extracted_entites = []
onehop_entites = []
frequency_dict = {}

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

# file _all_nodes.txt

# file _current.txt
f_current = open(file_path + '_current.txt', 'r')
for line in f_current.readlines():
	extracted_label2mid[line.split()[1]] = line.split()[0]
f_current.close()

f_result.write("This is extracted nodes:\n")
for label in extracted_label2mid:
	mid = extracted_label2mid[label]
	f_result.write(mid)
	f_result.write('\t')
	mid = "<http://rdf.freebase.com/ns/" + mid + ">"
	cur.execute("select `min_row_id`, `max_row_id` from `freebase-onlymid_-_fb-id2row-id` where `freebase_id` = '{0}';".format(mid))
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
	f_result.write(subject_entity)
	f_result.write('\n')

# file _onehop.txt
f_onehop = open(file_path + '_onehop.txt', 'r')
for line in f_onehop.readlines():
	onehop_label2mid[line.split()[1]] = line.split()[0]
f_onehop.close()

f_result.write("\n\n\nThis is onehop nodes:\n")
for label in onehop_label2mid:
	mid = onehop_label2mid[label]
	f_result.write(mid)
	f_result.write('\t')
	mid = "<http://rdf.freebase.com/ns/" + mid + ">"
	cur.execute("select `min_row_id`, `max_row_id` from `freebase-onlymid_-_fb-id2row-id` where `freebase_id` = '{0}';".format(mid))
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
	f_result.write(subject_entity)
	f_result.write('\n')

# file _tf_weights.txt
weights = []
f_frequency = open(file_path + '_tf_weights.txt', 'r')
for line in f_frequency.readlines():
	weights.append(float(line))
f_frequency.close()


# file _frequency_current.txt

# file _frequency_onehop.txt






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
l2v = g.graph_properties['lToV']
f_weights.close()


# pagerank
#f_result.write("\nThis is pagerank:\n")
pr = gt.centrality.pagerank(g, prop = g.vertex_properties['new_weights'], ret_iter = True, max_iter = 30000)
#top5_choose(f_result, pr[0], file_path, l2v)



# use betweenness, closeness, eigenvector centrality and katz to rank the top5

#ranked5 = get_ranked_top_5()


def get_ranked_top_5(betweenness, closeness, eigenvector, katz):
	scores = {}
	for i in range(0, len(betweenness)):
		scores[betweenness[i]] = 0.5 - float(i/10)
	for i in range(0, len(closeness)):
		scores[closeness[i]] += 0.5 - float(i/10)
	for i in range(0, len(eigenvector)):
		scores[eigenvector[i]] += 0.5 - float(i/10)
	for i in range(0, len(katz)):
		scores[katz[i]] += 0.5 - float(i/10)


	top5_choose(f_result, scores, file_path, l2v)
	








# betweenness 
bt = gt.centrality.betweenness(g, vprop = g.vertex_properties['new_weights'])
#top5_choose(f_result, bt[0], file_path, l2v)



# closeness

cl = gt.centrality.closeness(g, vprop = g.vertex_properties['new_weights'])
#top5_choose(f_result, cl,file_path, l2v)


# eigenvector centrality

ev = gt.centrality.eigenvector(g, vprop = g.vertex_properties['new_weights'])
#top5_choose(f_result, ev[1], file_path, l2v)


# katz
kz = gt.centrality.katz(g, vprop = g.vertex_properties['new_weights'])
#top5_choose(f_result, kz, file_path, l2v)




scores = []
for d in bt[0]:
	scores.append(0)

top5_l = get_top5_index(bt[0])
for i in range(0, 5):
	scores[top5_l[i]] += 0.5 - float(i/10)

top5_l = get_top5_index(cl)
for i in range(0, 5):
	scores[top5_l[i]] += 0.5 - float(i/10)

top5_l = get_top5_index(pr)
for i in range(0, 5):
	scores[top5_l[i]] += 0.7 * (0.5 - float(i / 10))

top5_l = get_top5_index(ev[1])
for i in range(0, 5):
	scores[top5_l[i]] += 0.7 * (0.5 - float(i/10))

top5_l = get_top5_index(kz)
for i in range(0, 5):
	scores[top5_l[i]] += 0.3 * (0.5 - float(i/10))


# print the original passage
f_result.write("\n\nThis is the original passage:\n")
f = open(file_path, "r")
f_result.write(f.read())
f_result.write('\n\n\n\n')


top5_choose(f_result, scores, file_path, l2v)	
#get_ranked_top_5(bt[0], cl, ev[1], kz)


f.close()

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
'''
	f_1 = open(file_path + "_current.txt","r")
	f_2 = open(file_path + "_onehop.txt","r")

	f_result.write("This is extracted nodes:\n")
	f_result.write(f_1.read())
	f_result.write("\n")

	f_result.write("This is onehop nodes:\n")
	f_result.write(f_2.read())
	f_result.write('\n')

	f_1.close()
	f_2.close()
'''
