import gensim, logging
import os
from gensim.models import word2vec
from nltk.corpus import brown

logging.basicConfig(format = '%(asctime)s:%(levelname)s:%(message)s', level = logging.INFO)

#brown_vecs = word2vec.Word2Vec(brown.sents())
f = open('/home/kevinj22/lydia/SimpleQuestions_v2/annotated_fb_data_predicates.txt','r')
lines = f.readlines()

sentences = []
for line in lines:
	sentences.append(line.split())


total_examples = len(lines)
i=10
w2v_model = gensim.models.Word2Vec(min_count=1)
w2v_model.build_vocab(brown.sents())
w2v_model.train(sentences, total_examples = total_examples, epochs = i)

for line in lines:
	tmp = w2v_model[line.split()[0]]
	for i in range(1, len(line.split())):
		tmp += w2v_model[line.split()[i]]
	print tmp


'''
f = open('/home/kevinj22/lydia/SimpleQuestions_v2/annotated_fb_data_predicates.txt','r')
lines = f.readlines()
logging.basicConfig(format = '%(asctime)s:%(levelname)s:%(message)s', level = logging.INFO)
sentences = gensim.models.doc2vec.TaggedLineDocument('/home/kevinj22/lydia/SimpleQuestions_v2/annotated_fb_data_predicates.txt')

LabeledSentence = gensim.models.doc2vec.LabeledSentence

docLabels = ['/home/kevinj22/lydia/SimpleQuestions_v2/annotated_fb_data_predicates.txt']
data = []
for doc in docLabels:
	data.append(open('/home/kevinj22/lydia/SimpleQuestions_v2/annotated_fb_data_predicates.txt','r'))


class LabeledLineSentence(object):
	def __init__(self, filename):
		self.filename = filename
	def __iter__(self):
		for uid, line in enumerate(open('/home/kevinj22/lydia/SimpleQuestions_v2/annotated_fb_data_predicates.txt')):
			yield LabeledSentence(words = line.split(), tags = ['SENT_%s' % uid])

it = LabeledLineSentence(data)


model = gensim.models.Doc2Vec(size = 300, window = 5, min_count=5, workers = 11, alpha = 0.025, min_alpha = 0.025)
model.build_vocab(it)

total_examples = 0
for tmp in it:
	total_examples += 1
i = 5
for epoch in range(10):
	print model.alpha
	model.train(it, total_examples = total_examples, epochs = i)
	model.alpha -= 0.002
	model.min_alpha = model.alpha
	#model.train(it)

model.save("/home/kevinj22/lydia/articles/doc2vec.model")
'''



'''
class LabeledLineSentence(object):
	def __init__(self, filename):
		self.filename = filename
	def __iter__(self):
		for line in enumerate(open('/home/kevinj22/lydia/articles/separate/0299_3211_The_animal_source_of_the_Ebola_outbreak_in_West_Africa_eludes_scientists/0299_3211_The_animal_source_of_the_Ebola_outbreak_in_West_Africa_eludes_scientists')):
			yield LabeledSentence(words = line.split(), tags = ['SENT_%s' % uid])


model = gensim.models.Doc2Vec.load('/home/kevinj22/lydia/articles/doc2vec.model')

word_vectors = model.wv
#print model
test_data = []
f = open('/home/kevinj22/lydia/articles/separate/0299_3211_The_animal_source_of_the_Ebola_outbreak_in_West_Africa_eludes_scientists/0299_3211_The_animal_source_of_the_Ebola_outbreak_in_West_Africa_eludes_scientists','r')
lines = f.readlines()
for line in lines:
	for spl in line.split():
		test_data.append(spl)
#test_data.append(open('/home/kevinj22/lydia/articles/separate/0299_3211_The_animal_source_of_the_Ebola_outbreak_in_West_Africa_eludes_scientists/0299_3211_The_animal_source_of_the_Ebola_outbreak_in_West_Africa_eludes_scientists','r'))
#print test_data
#print test_data
#vocab = model.build_vocab(test_data)

test = []
#print "Vocabulary: ", vocab
for t in test_data:
	if t in word_vectors.vocab:
		test.append(t)

#print test
print model.most_similar(test)
'''