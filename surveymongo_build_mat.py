"""
use python 3.4
"""

import requests
import pandas
import pymongo
import surveymongo
import sys

if (len(sys.argv)<2):
	print('Please specify a filename')
else:
	filename = sys.argv[1]

mongoclient = pymongo.MongoClient()
db = mongoclient.answers


varnames = db.varnames.distinct('varname')
varnames.append('user_hash')
varnames.remove('')

time_varnames = db.time_varnames.distinct('varname')
time_varnames.remove('')

new_varnames = varnames + time_varnames

mat = pandas.DataFrame(columns=new_varnames)

users = db.responses.distinct('user_hash')

# what if this doesn't execute?
try:
	UT_users_json = requests.get('http://10.1.93.163/experiment/users/experiment/User%20Testing', timeout=5)
	UT_users = UT_users_json.json()
except:
	print('Cannot connect to STOUT server, working with all users')
	UT_users = users


user_list = []
for user in users:
    if user in UT_users:
        user_list.append(user)

for user in user_list:
    rd = surveymongo.get_responses_dict(db, user)
    mat = mat.append(rd, ignore_index=True)

mat.to_csv(filename)
