import build_embedding_dict
import tensorflow as tf 


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


