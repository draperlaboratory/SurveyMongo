# get a list of surveys 
import sys
import requests
import json
from sm_functions import get_survey_list, get_respondent_list, get_responses, get_survey_details
import time
import pprint

with open("private_key.txt", "r") as f:
    client = requests.session()       
    client.headers = json.loads(f.readline())
    client.params = json.loads(f.readline())

    survey_list = get_survey_list(client)

    if sys.version_info[0] > 2:
        pprint.pprint(survey_list) # only works correctly in python 3
    else: 
        print json.dumps(survey_list, indent=2, sort_keys=True) #only works in python 2