import requests
import json
import datetime
import copy

sm_client = requests.session()
sm_client.headers = {
	"Authorization" : "bearer paTBz61kMlD0mPWrsaHR3921EuYbHlBvqU0GDZQ.5nahBvB1GbdZpbh2WnOzXY4S1m4CvPfPmXO9cABCSafzRjNeH9zln7ik1mnK.DPSQSI=", 
	"Content-Type" : "application/json"
}
sm_client.params = {
	"api_key": "xda4n5zxycnbhxqy84pb6bas" 
}

HOST = "https://api.surveymonkey.net"
SURVEY_LIST_ENDPOINT = "/v2/surveys/get_survey_list"


# ## Get a list of all surveys


survey_uri = "%s%s" % (HOST, SURVEY_LIST_ENDPOINT)
survey_post_data = {}
survey_post_data["fields"] = ["date_modified", "title"]
survey_post_data['title'] = ' UT '
survey_response = sm_client.post(survey_uri, data=json.dumps(survey_post_data))
# check this following result to proceed without errors
survey_response.headers 
survey_response_json = survey_response.json()
survey_list = survey_response_json["data"]["surveys"]

# ## Get the details for all the surveys

details_uri = "%s%s" % (HOST, '/v2/surveys/get_survey_details')
details_post_data = {}
survey_details = []

for survey in survey_list:
    details_post_data['survey_id'] = survey['survey_id']
    details_response = sm_client.post(details_uri, data=json.dumps(details_post_data))
    details_json = details_response.json()
    survey_details.append(details_json)

# ## Create a master answer dataframe that builds a single entry for every unique question-answer.  This dictionary will be the lookup table for answers to questions 

question_answer_table = []

for survey in survey_details:
    for page in survey['data']['pages']:
        for question in page['questions']:
            question_elements = {}
            question_elements['survey_id'] = survey['data']['survey_id']
            question_elements['page_id'] = page['page_id']
            question_elements['question_id'] = question['question_id']
            question_elements['heading'] = question['heading']
            question_elements['family'] = question['type']['family']
            question_elements['subtype'] = question['type']['subtype']
            if len(question['answers']) > 0:
                for answer in question['answers']:
                    answer_elements = {}
                    for key, value in answer.iteritems():
                        answer_elements[key]=value
                    question_elements.update(copy.deepcopy(answer_elements))
                    question_answer_table.append(copy.deepcopy(question_elements))
            else:
                question_answer_table.append(copy.deepcopy(question_elements))

# ##Create a sessionID questionID lookup table
sessions = []

for survey_detail in survey_details:
    try:
        sessionIDquestionID = survey_detail['data']['custom_variables'][0]['question_id']
        sessions.append({'SID':survey_detail['data']['survey_id'], 
                         'question_id':survey_detail['data']['custom_variables'][0]['question_id']})
    except IndexError:
        sessionIDquestionID = 0

# ## Start dumping sessionID table and answer table into Mongo
import pymongo
mongoclient = pymongo.MongoClient()
db = mongoclient.answers

db.drop_collection('sessions')
db.create_collection('sessions')
db.sessions.insert_many(sessions)

# ## Create a master answer table database

db.drop_collection('answer_table')
db.create_collection('answer_table')
db.answer_table.insert_many(question_answer_table)

# ## Get SM responses and dump those into Mongo also
# (but start with just one to test until the date crawler function is up...)

respondent_uri = "%s%s" % (HOST, '/v2/surveys/get_respondent_list')
respondent_post_data = {}
respondent_post_data['fields'] = ['date_modified', 'status']
respondent_post_data['start_modified_date'] = '2013-01-01 00:00:00'
response_uri = "%s%s" % (HOST, '/v2/surveys/get_responses')
response_post_data = {}

# cycle through all the surveys and collect responses
# survey_respondents = []
survey_responses = []
for survey in survey_list:
    respondent_post_data['survey_id'] = survey['survey_id']
    respondent_response = sm_client.post(respondent_uri, data=json.dumps(respondent_post_data))
    respondent_response_json = respondent_response.json()
    respondent_ids = []

    for respondent in respondent_response_json['data']['respondents']:
        if respondent['status'] == 'completed':
            respondent_ids.append(respondent['respondent_id'])
    if len(respondent_ids) > 0:
        response_post_data['survey_id'] = survey['survey_id']
        response_post_data['respondent_ids'] = respondent_ids
        responses_response = sm_client.post(response_uri, data=json.dumps(response_post_data))
        responses_json = responses_response.json()
        survey_responses.append(responses_json)


db.drop_collection('responses')
db.create_collection('responses')

for survey_response in survey_responses:
    db.responses.insert_many(survey_response['data'])

# ## Import config file into new collection

import csv
varnames = []
with open('Yr3_UT_ConfigFile.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        varnames.append({'question_id':row['Question ID'], 
                         'answer_id':row['Answer ID'], 
                         'varname':row['varnames']})

db.drop_collection('varnames')
db.create_collection('varnames')
db.varnames.insert_many(varnames)
