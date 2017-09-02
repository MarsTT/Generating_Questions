import build_embedding_dict
import tensorflow as tf 
from tensorflow.contrib import rnn
import numpy as np 

def BiRNN(x, weights, biases):

	x = tf.unstack(x, n_steps, 1)
	lstm_fw_cell = rnn.BasicLSTMCell(n_hidden, forget_bias=1.0)
	lstm_bw_cell = rnn.BasicLSTMCell(n_hidden, forget_bias=1.0)

	try:
		outputs, _, _ = rnn.static_bidirectional_rnn(lstm_fw_cell, lstm_bw_cell, x, dtype=tf.float32)

	except Exception:
		outputs = rnn.static_bidirectional_rnn(lstm_fw_cell, lstm_bw_cell, x, dtype=tf.float32)

	return tf.matmul(outputs[-1], weights['out']) + biases['out']




def get_embed_lstm(sx, sy):

	# get the embedding dict 
	vector_dict = build_embedding_dict.build_dict()

	# initial the sx_embed, sy_embed
	sx_embed = zeros[300]
	sy_embed = zeros[300]

	# add up the vectors of singles words in the sentence
	for x in sx:
		if x in vector_dict.keys():
			sx_embed += vector_dict[x]
	for y in sy:
		if y in vector_dict.keys():
			sy_embed += vector_dict[y]

	# get the lstm presentation of the sentence


	return sx_embed, sy_embed, sx_bi, sy_bi

