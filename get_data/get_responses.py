# get the responses to the survey

from __future__ import print_function
import sys
import requests
import json
import argparse
from sm_functions import get_survey_list, get_respondent_list, get_responses


def run(name="", date=None):
    with open("private_key.txt", "r") as f:
        client = requests.session()
        client.headers = json.loads(f.readline())
        client.params = json.loads(f.readline())

        survey_name = str(name)
        print ("Info: Downloading survey list", file=sys.stderr)
        survey_list = get_survey_list(client, survey_name) #optimize 

        respondent_list = {}

        ret = []
        for survey in reversed(survey_list['data']['surveys']):
            print ("Info: Downloading responses for", survey["title"], file=sys.stderr)
            respondent_list[survey['survey_id']] = get_respondent_list(client, survey['survey_id'], date) #optimize
            
            for respondent in respondent_list[survey['survey_id']]['data']['respondents']:
                ret.append(get_responses(client, survey['survey_id'], [respondent['respondent_id']], date))
              
        return ret
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download latest responses')
    parser.add_argument('--name', default="", dest='name',
                   help='Name of survey, default is all')
    parser.add_argument('--date', default=None, dest='date',
                   help='Date and time of last read, default is None')
    args = parser.parse_args()
    
    ret = run(args.name, args.date)
    for item in ret:
        json.dump(item, sys.stdout)
