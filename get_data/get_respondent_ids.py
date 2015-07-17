# get a list of respondent ids

from __future__ import print_function
import sys
import requests
import json
from sm_functions import get_survey_list, get_respondent_list, get_responses, get_survey_details
import time
import pprint

def run(name=""):
    with open("private_key.txt", "r") as f:
        client = requests.session()       
        client.headers = json.loads(f.readline())
        client.params = json.loads(f.readline())
        
        survey_name = str(name)
        print ("Info: Downloading survey list", file=sys.stderr)
        survey_list = get_survey_list(client, survey_name)
        ret = []
        for survey in reversed(survey_list['data']['surveys']):
            print ("Info: Downloading", survey["title"], file=sys.stderr)
            ret.append(get_respondent_list(client, survey['survey_id']))
        return ret
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        ret = run(sys.argv[1])
    else:
        ret = run()
    for item in ret:
        json.dump(item, sys.stdout)