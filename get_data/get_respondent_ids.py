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
            #error happened in here once
            '''
            Traceback (most recent call last):
  File "download_all.py", line 18, in <module>
    ret = get_respondent_ids.run(name="", date=date)
  File "C:\Users\Seth\Documents\GitHub\SurveyMongo\get_data\get_respondent_ids.p
y", line 23, in run
    ret.append(get_respondent_list(client, survey['survey_id'], date))
  File "C:\Users\Seth\Documents\GitHub\SurveyMongo\get_data\sm_functions.py", li
ne 48, in get_respondent_list
    respondents_response_json = respondents_response.json()
  File "C:\Users\Seth\Anaconda\lib\site-packages\requests\models.py", line 776,
in json
    return json.loads(self.text, **kwargs)
  File "C:\Users\Seth\Anaconda\lib\json\__init__.py", line 338, in loads
    return _default_decoder.decode(s)
  File "C:\Users\Seth\Anaconda\lib\json\decoder.py", line 366, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
  File "C:\Users\Seth\Anaconda\lib\json\decoder.py", line 384, in raw_decode
    raise ValueError("No JSON object could be decoded")
ValueError: No JSON object could be decoded
            '''
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