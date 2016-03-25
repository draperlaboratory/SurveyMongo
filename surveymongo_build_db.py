import requests
import json
import copy
import argparse
import pymongo
import csv
from time import sleep

SM_QUERIES_PER_SEC = -1

def run(survey_name="", start_date=None):
    sm_client = requests.session()
    #sm_client.headers = {
#	"Authorization" : "bearer paTBz61kMlD0mPWrsaHR3921EuYbHlBvqU0GDZQ.5nahBvB1GbdZpbh2WnOzXY4S1m4CvPfPmXO9cABCSafzRjNeH9zln7ik1mnK.DPSQSI=", 
#	"Content-Type" : "application/json"
#}
#    sm_client.params = {
#	"api_key": "xda4n5zxycnbhxqy84pb6bas" 
#}
    with open("private_key.txt", "r") as f:
        sm_client.headers = json.loads(f.readline())
        sm_client.params = json.loads(f.readline())


    HOST = "https://api.surveymonkey.net"
    SURVEY_LIST_ENDPOINT = "/v2/surveys/get_survey_list"


    # Get a list of all surveys
    print 'Getting a list of surveys... '
    survey_uri = "%s%s" % (HOST, SURVEY_LIST_ENDPOINT)
    if survey_name != "":
        survey_post_data = {}
        # FROM ORIGINAL BITBUCKET VERSION
        #survey_post_data["fields"] = ["date_modified", "title"]
        #survey_post_data['title'] = ' UT '
        survey_post_data["fields"] = ["date_modified", "title"]
        survey_post_data["start_modified_date"] = start_date
        survey_post_data["title"] = survey_name
        
        survey_response = sm_client.post(survey_uri, data=json.dumps(survey_post_data), verify=True)
    else:
        survey_response = sm_client.post(survey_uri, '{"fields":["title"]}', verify=True)
    
    # check this following result to proceed without errors
    survey_response.headers 
    try:
        survey_response_json = survey_response.json()
        print survey_response_json
    except:
        print "Exception occurred"
        print sys.exc_info()[0]
        print "survey_name =", survey_name
        print "survey_response =", survey_response
        raise
    survey_list = survey_response_json["data"]["surveys"]
    
    # Get the details for all the surveys
    
    details_uri = "%s%s" % (HOST, '/v2/surveys/get_survey_details')
    details_post_data = {}
    survey_details = []
    
    print 'Getting details for surveys...'
    for survey in survey_list:
        details_post_data['survey_id'] = survey['survey_id']
        details_response = sm_client.post(details_uri, data=json.dumps(details_post_data))
        details_json = details_response.json()
        survey_details.append(details_json)
        if SM_QUERIES_PER_SEC > 0:
            sleep(1/SM_QUERIES_PER_SEC)
    
    # Create a master answer dataframe that builds a single entry for every unique question-answer.  This dictionary will be the lookup table for answers to questions 
    
    question_answer_table = []
    survey_subjectIDs = []
    
    for survey in survey_details:
        surveyID = survey['data']['survey_id']
        if survey['data']['custom_variables'] != []:
            subjectIDQ = survey['data']['custom_variables'][0]['question_id']
            survey_subjectIDs.append({'survey_id':surveyID, 'question_id':subjectIDQ})
        for page in survey['data']['pages']:
            for question in page['questions']:
                question_elements = {}
                question_elements['survey_id'] = surveyID
                question_elements['page_id'] = page['page_id']
                question_elements['question_id'] = question['question_id']
                question_elements['heading'] = question['heading']
                question_elements['family'] = question['type']['family']
                question_elements['subtype'] = question['type']['subtype']

                answers = []
                for answer in question['answers']:
                    answers.append(answer)
                question_elements['answers'] = answers
                question_answer_table.append(copy.deepcopy(question_elements))
                #if len(question['answers']) > 0:
                #    for answer in question['answers']:
                #        answer_elements = {}
                #        for key, value in answer.iteritems():
                #            answer_elements[key]=value
                #        question_elements.update(copy.deepcopy(answer_elements))
                #        question_answer_table.append(copy.deepcopy(question_elements))
                #else:
                #    question_answer_table.append(copy.deepcopy(question_elements))
    
    #Create a sessionID questionID lookup table
    sessions = []
    for survey_detail in survey_details:
        try:
            sessionIDquestionID = survey_detail['data']['custom_variables'][0]['question_id']
            sessions.append({'survey_id':survey_detail['data']['survey_id'],
                             'title':survey_detail['data']['title']['text'],
                             'question_id':survey_detail['data']['custom_variables'][0]['question_id']})
        except IndexError:
            sessionIDquestionID = 0
    
    # Start dumping sessionID table and answer table into Mongo
    mongoclient = pymongo.MongoClient()
    db = mongoclient.answers
    
    print 'Adding sessionID table to DB'
    db.drop_collection('sessions')
    db.create_collection('sessions')
    db.sessions.insert_many(sessions)

    # Create a master answer table database
    print 'Adding question and answer table to DB'
    db.drop_collection('answer_table')
    db.create_collection('answer_table')
    db.answer_table.insert_many(question_answer_table)
    
    # Get SM responses and dump those into Mongo also
    print 'Getting participant responses...'
    respondent_uri = "%s%s" % (HOST, '/v2/surveys/get_respondent_list')
    respondent_post_data = {}
    respondent_post_data['fields'] = ['date_start', 'date_modified', 'status', 'custom_id']
    respondent_post_data['start_modified_date'] = '2013-01-01 00:00:00'
    response_uri = "%s%s" % (HOST, '/v2/surveys/get_responses')
    response_post_data = {}
    
    # cycle through all the surveys and collect responses
    survey_responses = []
    survey_respondents = []
    for survey in survey_list:
        respondent_post_data['survey_id'] = survey['survey_id']
        respondent_response = sm_client.post(respondent_uri, data=json.dumps(respondent_post_data))
        respondent_response_json = respondent_response.json()
        respondent_ids = []
    
        for respondent in respondent_response_json['data']['respondents']:
            if respondent['status'] == 'completed':
                respondent_ids.append(respondent['respondent_id'])
                survey_respondents.append(respondent)
        if len(respondent_ids) > 0:
            response_post_data['survey_id'] = survey['survey_id']
            response_post_data['respondent_ids'] = respondent_ids
            responses_response = sm_client.post(response_uri, data=json.dumps(response_post_data))
            responses_json = responses_response.json()
            survey_responses.append(responses_json)
    
    print 'Adding respondents to DB'
    db.drop_collection('respondents')
    db.create_collection('respondents')
    
    db.respondents.insert_many(survey_respondents)

    print 'Adding responses to DB'
    db.drop_collection('responses')
    db.create_collection('responses')
    
    for survey_response in survey_responses:
        db.responses.insert_many(survey_response['data'])
    
    # create table of user hash / session ID
    hashes = []
    response_hashes = []
    for survey_var in survey_subjectIDs:
        survey_id = survey_var["survey_id"]
        question_id = survey_var["question_id"]
        for response in db.responses.find():
            for question in response["questions"]:
                if question["question_id"] == question_id:
                    for answer in question["answers"]:
                        hash_answer = {}
                        hash_answer['survey_id'] = survey_id
                        hash_answer['question_id'] = question_id
                        hash_answer['response_id'] = response['_id']
                        hash_answer['respondent_id'] = response['respondent_id']
                        hash_answer['user_hash'] = answer['text']
                        hashes.append(hash_answer)
                        #db.responses.update_one({'_id', response['_id']},
                        #    {'$set': {'user_hash':hash_answer['user_hash']}})

    print 'Adding user hashes to DB'
    db.drop_collection('user_hashes')
    db.create_collection('user_hashes')
    db.user_hashes.insert_many(hashes)
        
    # ## Import config file into new collection
    
    print 'Adding varname lookup table to DB'
    varnames = []
    with open('./configs/' + survey_name + '_ConfigFile.csv') as configfile:
        reader = csv.DictReader(configfile)
        for row in reader:
            varnames.append({'question_id':row['Question ID'], 
                             'answer_id':row['Answer ID'], 
                             'varname':row['varnames']})
    
    db.drop_collection('varnames')
    db.create_collection('varnames')
    db.varnames.insert_many(varnames)

    # ## Import time variable names
    print 'Adding time_varnames lookup table to DB'
    time_varnames = []
    with open('./configs/' + survey_name + '_TimeConfig.csv') as timefile:
        reader = csv.DictReader(timefile)
        for row in reader:
            time_varnames.append({'survey_id':row['Survey ID'], 
                                 'time_id':row['time_id'], 
                                 'varname':row['varnames']})
    
    db.drop_collection('time_varnames')
    db.create_collection('time_varnames')
    db.time_varnames.insert_many(time_varnames)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='create database of surveys that match the name and date')
    parser.add_argument('--name', default="", dest='name',
                   help='Name of survey, default is all')
    parser.add_argument('--date', default=None, dest='date',
                   help='Date and time of last read, default is None')
    args = parser.parse_args()

    ret = run(args.name, args.date)
