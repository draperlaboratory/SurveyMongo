"""
use python 3.4
"""

import unicodedata
import requests
import pandas
import pymongo
import surveymongo
import sys
import argparse
from datetime import datetime
from shutil import copyfile
from surveymongo_consts import SM_REPORT_PATH

def run(survey_name="", expName=""):
    if (len(sys.argv)<2):
        print('Please specify a filename')
    else:
        filename = sys.argv[1]

    mongoclient = pymongo.MongoClient()
    db = mongoclient.answers


    varnames = db.varnames.distinct('varname')
    varnames.append('user_hash')
    try:
        varnames.remove('')
    except ValueError:
        pass

    time_varnames = db.time_varnames.distinct('varname')
    try:
        time_varnames.remove('')
    except ValueError:
        pass

    new_varnames = varnames + time_varnames
    new_varnames.append('mechanicalTurkCode')

    mat = pandas.DataFrame(columns=new_varnames)

    users = db.user_hashes.distinct('user_hash')

    # what if this doesn't execute?
    try:
        #UT_users_json = requests.get('http://172.31.38.3/experiment/users/experiment/User%20Testing', timeout=5)
        UT_users_json = requests.get('http://127.0.0.1:8000/experiment/experiment/users/experiment/' + expName, timeout=5)
        UT_users = UT_users_json.json()
	print "Start UT_users"
        print UT_users
	print "End UT_users"
    except:
        print('Cannot connect to STOUT server, working with all users')
        UT_users = users


    user_list = []
    for user in users:
        if user in UT_users:
            user_list.append(user)

    #print user_list
    for user in user_list:
        rd = surveymongo.get_responses_dict(db, user)
	rd['mechanicalTurkCode']=UT_users[user]['mtcode']
        for key, value in UT_users[user]['vars'].iteritems():
            rd[key]=value
        for key, value in rd.iteritems():
            try:
                rd[key]=unicodedata.normalize('NFKD',value).encode('ascii','ignore')
            except TypeError:
                pass
        mat = mat.append(rd, ignore_index=True)

    filename = SM_REPORT_PATH + survey_name + '_mat.csv'
    mat.to_csv(filename)
    now_str = "%s"%datetime.now().strftime("_%Y-%m-%d-%H:%M:%S")
    copyfile(filename, SM_REPORT_PATH+survey_name+now_str+'_mat.csv')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='create mat file for surveys that match the name')
    parser.add_argument('--name', default="", dest='name',
                   help='Name of survey, default is all')
    parser.add_argument('--exp', default="VtV_TEST", dest='expName',
                   help='Name of STOUT experiment, default is "VtV_TEST"')
    args = parser.parse_args()

    run(args.name, args.expName)

