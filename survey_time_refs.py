import requests
import surveymonkey
import sys
import pandas
import json
import argparse

#SPY4119, 3/8/2016
#The output format currently is nowhere close to Josh's example: this needs work
def run(survey_name=''):
    client = requests.session()
    with open("private_key.txt", "r") as f:
        client.headers = json.loads(f.readline())
        client.params = json.loads(f.readline())

    print("searching for " + survey_name + "...")
    # survey_name = str(sys.argv[1])
    survey_list = surveymonkey.get_survey_list(client=client, survey_name=survey_name)

    if len(survey_list['data']['surveys']) == 0:
        print("Unable to find",survey_name)
        exit(0)

    surveydetails_list = []

    for survey in survey_list['data']['surveys']:
        print('Processing '+survey['title'])
        surveydetails_start = {}
        surveydetails_start[survey['survey_id']] = survey['title']
        surveydetails_start['start_time_id'] = '1'
        surveydetails_list.append(surveydetails_start)

        surveydetails_end = {}
        surveydetails_end[survey['survey_id']] = survey['title']
        surveydetails_end['end_time_id'] = '0' 
        surveydetails_list.append(surveydetails_end)

    surveydetailsdf = pandas.DataFrame(surveydetails_list)
    surveydetailsdf.to_csv('./configs/' + survey_name + '_time.csv', encoding='utf-8')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='create time config file for surveys that match the name')
    parser.add_argument('--name', default="", dest='name',
                   help='Name of survey, default is all')
    args = parser.parse_args()

    run(args.name)
