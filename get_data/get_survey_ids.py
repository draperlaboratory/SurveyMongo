# get a list of surveys 
import sys
import requests
import json
from sm_functions import get_survey_list, get_respondent_list, get_responses, get_survey_details
import time
import pprint

def run(name):
    with open("private_key.txt", "r") as f:
        client = requests.session()       
        client.headers = json.loads(f.readline())
        client.params = json.loads(f.readline())

        survey_name = str(name)
        survey_list = get_survey_list(client, survey_name)

        if sys.version_info[0] > 2:
            #print(survey_list) # only works correctly in python 3
            pprint.pprint(survey_list) # only works correctly in python 3
        else: 
            json.dumps(survey_list, indent=2, sort_keys=True) #only works in python 2
    
if __name__ == '__main__':
    run(sys.argv[1])    