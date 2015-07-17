# get survey details

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

        for survey in reversed(survey_list['data']['surveys']):
            json.dump(get_survey_details(client, survey['survey_id']), sys.stdout)
        
if __name__ == '__main__':
    run(sys.argv[1])    