import MySQLdb
import numpy as np

# read the file
predCounts = np.load('FullpredCounts.npy').item()
db = MySQLdb.connect(host="image.eecs.yorku.ca",    # your host, usually localhost
                     port=3306,
                     user="read_only_user",         # your username
                     passwd="P@ssw0rd",  # your password
                     db="freebase_mysql_db")        # name of the data base
cur = db.cursor()


f = open('/home/kevinj22/lydia/SimpleQuestions_v2/annotated_fb_data_train.txt','r')
lines = f.readlines()
f.close()
f = open('/home/kevinj22/lydia/SimpleQuestions_v2/annotated_fb_data_predicates.txt','w+')
print len(lines)
for line in lines:
	splits = line.split('\t')
	predicate = splits[-1]
	columns = splits[0].split('/')
	#print columns
	mid = columns[1] + '.' + columns[2]
	mid = "<http://rdf.freebase.com/ns/" + str(mid) + ">"
	cur.execute("select `min_row_id`, `max_row_id` from `freebase-onlymid_-_fb-id2row-id` where `freebase_id` = '{0}';".format(mid))
	rows = cur.fetchall()
	if len(rows) == 0:
		f.write('\n')
		continue
	#print rows
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
	predicate = predicate.replace(origin_entity, " ")
	predicate = predicate.replace(origin_entity_lower," ")
	f.write(predicate)
	#f.write('\n')

f.close()