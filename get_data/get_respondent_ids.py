# get a list of respondent ids

from __future__ import print_function
import sys
import requests
import json
from sm_functions import get_survey_list, get_respondent_list
import argparse

def run(name="", date=None):
    with open("private_key.txt", "r") as f:
        client = requests.session()       
        client.headers = json.loads(f.readline())
        client.params = json.loads(f.readline())
        
        survey_name = str(name)
        print ("Info: Downloading survey list", file=sys.stderr)
        survey_list = get_survey_list(client, survey_name, date) #optimize, date does nothing?
        ret = []
        count = 0
        for survey in reversed(survey_list['data']['surveys']):
            print ("Info: Downloading respondent IDs for", survey["title"], file=sys.stderr)
            ret.append(get_respondent_list(client, survey['survey_id'], date))
            count += 1
        print ("Info: %d surveys processed"%count, file=sys.stderr)
        return ret
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download latest respondent IDs')
    parser.add_argument('--name', default="", dest='name',
                   help='Name of survey, default is all')
    parser.add_argument('--date', default=None, dest='date',
                   help='Date and time of last read, default is None')
    args = parser.parse_args()
    
    ret = run(args.name, args.date)
    for item in ret:
        json.dump(item, sys.stdout)