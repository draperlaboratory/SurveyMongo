# get survey details

from __future__ import print_function
import sys
import requests
import argparse
import json
from sm_functions import get_survey_list, get_survey_details


def run(name="", date=None):
    with open("private_key.txt", "r") as f:
        client = requests.session()       
        client.headers = json.loads(f.readline())
        client.params = json.loads(f.readline())
        survey_name = str(name)
        print ("Info: Downloading survey list", file=sys.stderr)
        survey_list = get_survey_list(client, survey_name) #optimize

	print (survey_list, file=sys.stderr)
	if survey_list["status"] == 1:
	    print ("Error: " + survey_list["errmsg"], file=sys.stderr)
            sys.exit(1)

        ret = []
        for survey in reversed(survey_list['data']['surveys']):
            print ("Info: Downloading survey details for", survey["title"], file=sys.stderr)
            ret.append(get_survey_details(client, survey['survey_id'], date))
        return ret
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download latest survey details')
    parser.add_argument('--name', default="", dest='name',
                   help='Name of survey, default is all')
    parser.add_argument('--date', default=None, dest='date',
                   help='Date and time of last read, default is None')
    args = parser.parse_args()
    
    ret = run(args.name, args.date)
    for item in ret:
        json.dump(item, sys.stdout)
