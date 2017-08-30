import gensim
import os
import collections
import nltk
from nltk.corpus import gutenberg
import numpy as np
import MySQLdb 


class LabeledLineSentence(object):
	def __init__(self, doc_list, labels_list):
		self.labels_list = labels_list
		self.doc_list = doc_list
	def __iter__(self):
		for idx, doc in enumerate(self.doc_list):
			yield gensim.models.doc2vec.LabeledSentence(words = doc.split(), tags=[self.labels_list[idx]])

def choose_predicate(predDict, file_path):
	

	LabeledSentence = gensim.models.doc2vec.LabeledSentence

	'''
	raw_texts = []
	labels_texts = gutenberg.fileids()
	for l in labels_texts:
		raw_texts.append(gutenberg.raw(l))

	it = LabeledLineSentence(raw_texts, labels_texts)

	model = gensim.models.Doc2Vec(min_count=1, alpha=0.025, min_alpha=0.025,size=100)

	model.build_vocab(it)
	total_words = len(model.wv.vocab)
	for epoch in range(10):
		model.train(it, total_words = total_words, epochs = 10)
		model.alpha -= 0.002
		model.min_alpha = model.alpha
		model.train(it, total_words = total_words, epochs = 10)

	model.save('/home/kevinj22/lydia/articles/Aug28_model.model')
	'''




	# get the predicate vectors
	model = gensim.models.Doc2Vec.load('/home/kevinj22/lydia/articles/Aug28_model.model')
	f = open('/home/kevinj22/lydia/SimpleQuestions_v2/annotated_fb_data_train.txt','r')
	lines = f.readlines()
	f.close()

	predicates = []
	predicate_fisrt_parts = []
	for p in predDict:
		if "ns/" in p:
			predicate_fisrt_parts.append("ns/")
		elif "key/" in p:
			predicate_fisrt_parts.append("key/")
		p = p.replace("ns/","").replace("key/","")
		splits = p.split('.')
		p = '/'.join(splits)
		p = "www.freebase.com/" + p
		predicates.append(p)
	#predicates = predDict
	#print predicates[0]
	pre2sen = {}
	for pre in predicates:
		pre2sen[pre] = []

	#print pre2sen.keys()
	predCounts = np.load('FullpredCounts.npy').item()
	db = MySQLdb.connect(host="image.eecs.yorku.ca",    # your host, usually localhost
                     port=3306,
                     user="read_only_user",         # your username
                     passwd="P@ssw0rd",  # your password
                     db="freebase_mysql_db")        # name of the data base
	cur = db.cursor()

	predicate_sentence = []
	for line in lines:
		tmp_pred = line.split('\t')[1]
		if tmp_pred == 'www.freebase.com/common/topic/notable_types':
			continue
		#print tmp_pred
		if tmp_pred in pre2sen.keys():
			#print "Got ONE!"
			'''
			columns = line.split('\t')[0].split('/')
			mid = columns[1] + '.' + columns[2]
			mid = "<http://rdf.freebase.com/ns/" + str(mid) + ">"
			cur.execute("select `min_row_id`, `max_row_id` from `freebase-onlymid_-_fb-id2row-id` where `freebase_id` = '{0}';".format(mid))
			rows = cur.fetchall()
			if len(rows) <= 0 :
				continue
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
			print origin_entity
			'''
			pre2sen[tmp_pred].append(line.split('\t')[-1])
			#predicate_sentence.append(line.split('\t')[-1].replace(origin_entity,"").replace(origin_entity_lower,""))
			predicate_sentence.append(line.split('\t')[-1])
	#print len(pre2sen)
	
	

	predicate_vectors = []
	for p in predicate_sentence:
		splits = p.split()
		i = 0
		while splits[i] not in model.wv.vocab and i < len(splits)-1:
			i += 1

		if i < len(splits) - 1:
			tmp_vector = model[splits[i]]
			for j in range(i + 1, len(splits)-1):
				if splits[j] in model.wv.vocab:
					tmp_vector += model[splits[j]]
		else:
			tmp_vector = 2 * np.random.random(size=100) - 1
			#print "None of the words in the sentence exits in the vocab"
			continue

		predicate_vectors.append(tmp_vector)


	print "predicate_vectors:",len(predicate_vectors)
	f = open(file_path,'r')
	lines = f.readlines()
	f.close()

	splits = []
	for line in lines:
		splits += line.split()

	i = 0
	while splits[i] not in model.wv.vocab and i < len(splits)-1:
		i += 1

	vector = model[splits[i]]
	for s in splits[i+1:]:
		if s in model.wv.vocab:
			vector += model[s]


	vector = vector.astype(float)
	min_dis = float("inf")
	count = 0
	predicate_no = 0
	for v in predicate_vectors:
		v = v.astype(float)
		if np.sqrt(np.sum(np.square(vector-v))) < min_dis:
			min_dis = np.sqrt(np.sum(np.square(vector-v)))
			predicate_no = count
		#else:
			#print "Bigger than min"
		count += 1

	print "We are Here"
	print predicate_no
	print predicate_sentence[predicate_no]
	#print predicates[predicate_no]
	for p in pre2sen:
		if predicate_sentence[predicate_no] in pre2sen[p]:
			p = p.replace("www.freebase.com/","")
			splits = p.split('/')
			p = '.'.join(splits)
			#p = predicate_fisrt_parts
			#p = "<http://rdf.freebase.com/" + p + ">"
			print p
			return p
