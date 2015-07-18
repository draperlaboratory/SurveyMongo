# get a list of survey ids 
# this is also done in the other 3 get_ files. It's redundant, but pretty fast. Perhaps a future to do.
from __future__ import print_function
import sys
import requests
import json
from sm_functions import get_survey_list, get_respondent_list, get_responses, get_survey_details
import pprint

def run(name=""):
    with open("private_key.txt", "r") as f:
        client = requests.session()       
        client.headers = json.loads(f.readline())
        client.params = json.loads(f.readline())
        survey_name = str(name)
        print ("Info: Downloading survey ID list", file=sys.stderr)
        survey_list = get_survey_list(client, survey_name)
        return survey_list

    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        ret = run(sys.argv[1])
    else:
        ret = run()
    if sys.version_info[0] > 2:
        pprint.pprint(ret) # only works correctly in python 3
    else: 
        print (json.dumps(ret, indent=2, sort_keys=True)) #only works in python 2    