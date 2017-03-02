import requests
import json
import copy
import argparse
import pymongo
import csv
from surveymongo_consts import SM_QUERIES_PER_SEC, SM_DATE_DEFAULT, SM_DATE_FILE, SM_CONFIG_PATH, SM_MAX_RESP
from time import sleep
import datetime
from os import path

def run(survey_name="", rebuild=False):
    date = ''
    mongoclient = pymongo.MongoClient()
    db = mongoclient.answers

    if rebuild or not path.isfile(SM_DATE_FILE):
        print 'Setting response date to default: ' + SM_DATE_DEFAULT
        date = SM_DATE_DEFAULT

        print 'Rebuilding Database from Scratch ...'
        db.drop_collection('respondents')
        db.create_collection('respondents')
        db.drop_collection('responses')
        db.create_collection('responses')
        db.drop_collection('user_hashes')
        db.create_collection('user_hashes')

        rebuild_db(survey_name)
        print 'Done!'
    else:
        f = open(SM_DATE_FILE)
        date = f.readline()
        print 'Updating responses from last read: ' + date

    print 'Updating response tables ...'
    get_responses(date)
    print 'Done!'

    #remove split seconds, they break survey monkey
    #now_str = "%s"%datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_date = db.respondents.find().sort('date_modified',pymongo.DESCENDING)[0]['date_modified']
    print 'Setting ' + SM_DATE_FILE + ' to ' + last_date
    #write last respondent date 
    with open(SM_DATE_FILE, "w") as f:
        f.write(last_date)


#################################################
def rebuild_db(survey_name):
    sm_client = requests.session()
    #sm_client.headers = {
#	"Authorization" : "bearer paTBz61kMlD0mPWrsaHR3921EuYbHlBvqU0GDZQ.5nahBvB1GbdZpbh2WnOzXY4S1m4CvPfPmXO9cABCSafzRjNeH9zln7ik1mnK.DPSQSI=", 
#	"Content-Type" : "application/json"
#}
    with open("private_key.txt", "r") as f:
        sm_client.headers = json.loads(f.readline())
        #sm_client.params = json.loads(f.readline())

    HOST = "https://api.surveymonkey.net"
    SURVEY_LIST_ENDPOINT = "/v3/surveys"

    # Get a list of all surveys
    # https://api.surveymonkey.net/v3/surveys?per_page=1000&title=MOT
    print 'Getting a list of surveys... '
    survey_uri = "%s%s" % (HOST, SURVEY_LIST_ENDPOINT)
    survey_post_data = {}

    if survey_name != "":
        survey_post_data["per_page"] = 1000
        survey_post_data["title"] = survey_name
        
    else:
        survey_post_data["per_page"] = 1000

    survey_response = sm_client.get(survey_uri, params=survey_post_data)

    print 'survey_post_data = ', json.dumps(survey_post_data)

    # check this following result to proceed without errors
    survey_response.headers 
    try:
        survey_response_json = survey_response.json()
        #print survey_response_json
    except:
        print "Exception occurred"
        print sys.exc_info()[0]
        print "survey_name =", survey_name
        print "survey_response =", survey_response
        raise

    # data: [{href, nickname, id, title}, {}, {}]
    survey_list = survey_response_json["data"]

    # Get the details for all the surveys
    # https://api.surveymonkey.net/v3/surveys/69948779/details
    details_uri = "%s%s" % (HOST, '/v3/surveys/')
    survey_details = []
    
    print 'Getting details for surveys...'
    for survey in survey_list:
        details_uri = "%s%s%s%s" % (HOST, '/v3/surveys/',  survey['id'], '/details')
        details_response = sm_client.get(details_uri)
        details_json = details_response.json()
        survey_details.append(details_json)
        if SM_QUERIES_PER_SEC > 0:
            sleep(1/SM_QUERIES_PER_SEC)
    
    # Create a master answer dataframe that builds a single entry for every unique question-answer.  This dictionary will be the lookup table for answers to questions 
    
    question_answer_table = []
    
    for survey in survey_details:
        surveyID = survey['id']
        
        for page in survey['pages']:
            for question in page['questions']:
                question_elements = {}
                question_elements['survey_id'] = surveyID
                question_elements['page_id'] = page['id']
                question_elements['question_id'] = question['id']
                question_elements['heading'] = question['headings'][0]['heading']
                question_elements['family'] = question['family']
                question_elements['subtype'] = question['subtype']

                answers = []
                if 'answers' in question:
                    if question['family']=='single_choice':
                        for answer in question['answers']['choices']:
                            answer_elements = {}
                            answer_elements['text'] = answer['text']
                            answer_elements['answer_id'] = answer['id']
                            answer_elements['type'] = "row"
                            answer_elements['visible'] = answer['visible']
                            answer_elements['position'] = answer['position']

                            answers.append(copy.deepcopy(answer_elements))

                        if 'other' in question['answers']:
                            answer_elements = {}
                            answer_elements['text'] = question['answers']['other']['text']
                            answer_elements['answer_id'] = question['answers']['other']['id']
                            answer_elements['type'] = "other"
                            answer_elements['visible'] = question['answers']['other']['visible']
                            answer_elements['apply_all_rows'] = question['answers']['other']['apply_all_rows']

                            answers.append(copy.deepcopy(answer_elements))

                    elif question['family']=='multiple_choice':
                        for answer in question['answers']['choices']:
                            answer_elements = {}
                            answer_elements['text'] = answer['text']
                            answer_elements['answer_id'] = answer['id']
                            answer_elements['type'] = "row"
                            answer_elements['visible'] = answer['visible']
                            answer_elements['position'] = answer['position']

                            answers.append(copy.deepcopy(answer_elements))

                    elif (question['family']=='matrix') and (question['subtype'] in ['single', 'rating', 'ranking']):
                        for answer in question['answers']['rows']:
                            answer_elements = {}
                            answer_elements['text'] = answer['text']
                            answer_elements['answer_id'] = answer['id']
                            answer_elements['type'] = "row"
                            answer_elements['visible'] = answer['visible']
                            answer_elements['position'] = answer['position']

                            answers.append(copy.deepcopy(answer_elements))

                        for answer in question['answers']['choices']:
                            answer_elements = {}
                            answer_elements['text'] = answer['text']
                            answer_elements['answer_id'] = answer['id']
                            answer_elements['type'] = "col"
                            answer_elements['visible'] = answer['visible']
                            answer_elements['position'] = answer['position']

                            answers.append(copy.deepcopy(answer_elements))

                    elif (question['family']=='matrix') and (question['subtype']=='menu'):
                        for answer in question['answers']['rows']:
                            answer_elements = {}
                            answer_elements['text'] = answer['text']
                            answer_elements['answer_id'] = answer['id']
                            answer_elements['type'] = "row"
                            answer_elements['visible'] = answer['visible']
                            answer_elements['position'] = answer['position']

                            answers.append(copy.deepcopy(answer_elements))

                        for answer in question['answers']['cols']:
                            answer_elements = {}
                            answer_elements['text'] = answer['text']
                            answer_elements['answer_id'] = answer['id']
                            answer_elements['type'] = "col"
                            answer_elements['visible'] = answer['visible']
                            answer_elements['position'] = answer['position']
                            answer_elements['items'] = []
                            for answer_choice in answer['choices']:
                                answer_choice_elements = {}
                                answer_choice_elements['text'] = answer_choice['text']
                                answer_choice_elements['answer_id'] = answer_choice['id']
                                answer_choice_elements['type'] = "col_choice"
                                answer_choice_elements['visible'] = answer_choice['visible']
                                answer_choice_elements['position'] = answer_choice['position']
                                answer_elements['items'].append(copy.deepcopy(answer_choice_elements))

                            answers.append(copy.deepcopy(answer_elements))

                    elif (question['family']=='open_ended') and (question['subtype'] in ['multi', 'numerical']):
                        for answer in question['answers']['rows']:
                            answer_elements = {}
                            answer_elements['text'] = answer['text']
                            answer_elements['answer_id'] = answer['id']
                            answer_elements['type'] = "row"
                            answer_elements['visible'] = answer['visible']
                            answer_elements['position'] = answer['position']

                            answers.append(copy.deepcopy(answer_elements))

                    else:
                        answers = []    # open_ended, single and presentation, descriptive_text

                question_elements['answers'] = answers
                question_answer_table.append(copy.deepcopy(question_elements))
    
    #Create a sessionID questionID lookup table
    sessions = []
    for survey_detail in survey_details:
        try:
            #sessions.append({'survey_id':survey_detail['data']['survey_id'],
            #                 'title':survey_detail['data']['title']['text'],
            #                 'question_id':survey_detail['data']['custom_variables'][0]['question_id']})
            sessions.append({'survey_id':survey_detail['id'],
                             'title':survey_detail['title'],
                             'question_id':survey_detail['id']})
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
    
        
    # ## Import config file into new collection
    
    print 'Adding varname lookup table to DB'
    varnames = []
    with open(SM_CONFIG_PATH + survey_name + '_ConfigFile.csv') as configfile:
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

#################################################
def get_responses(start_date):
    mongoclient = pymongo.MongoClient()
    db = mongoclient.answers

    sm_client = requests.session()
    with open("private_key.txt", "r") as f:
        sm_client.headers = json.loads(f.readline())

    HOST = "https://api.surveymonkey.net"
    SURVEY_LIST_ENDPOINT = "/v3/surveys/"

    # Get SM responses and dump those into Mongo also
    print 'Getting participant responses...'
    # https://api.surveymonkey.net/v3/surveys/69948779/responses?per_page=1000&status=completed
    respondent_uri = "%s%s" % (HOST, '/v2/surveys/get_respondent_list')
    # respondent_post_data['fields'] = ['date_start', 'date_modified', 'status', 'custom_id']

    # https://api.surveymonkey.net/v3/surveys/66869844/responses/bulk?per_page=100&page=1
    response_uri = "%s%s" % (HOST, '/v2/surveys/get_responses')
    response_post_data = {}
    response_post_data['per_page'] = 100
    response_post_data['status'] = 'completed'
    response_post_data['start_created_at'] = start_date
    response_post_data['start_modified_at'] = '2013-01-01 00:00:00'
    
    # cycle through all the surveys and collect responses
    survey_list = db.sessions.find()
    responses_rawdata = []

    survey_responses = []
    survey_respondents = []
    n_s = 0

    response_total_count = 0

    for survey in survey_list:
        n_s = n_s + 1
        print "  Survey", n_s, "of", survey_list.count()

        sent = 1    # page 1
        response_post_data['page'] = sent

        response_uri = "%s%s%s%s" % (HOST, '/v3/surveys/', survey['survey_id'], '/responses/bulk')
        responses_response = sm_client.get(response_uri, params=response_post_data)
        responses_json = responses_response.json()

        responses_total = responses_json['total']
        response_total_count = response_total_count + responses_total

        print "    Response page ", sent, " (100 per page) of ", responses_total
        print "        uri=",response_uri,", params=",response_post_data
        print "        response_json[data].length=",len(responses_json['data'])
        # save raw responses
        #print "*** Bulk response:",responses_json
        #responses_rawdata.extend(responses_json['data'])
        for rdata in responses_json['data']:
            responses_rawdata.append(copy.deepcopy(rdata))

        print "        response_rawdata.length=",len(responses_rawdata)

        # check for more pages
        while sent*100 < responses_total:
            sent = sent+1
            response_post_data['page'] = sent

            print "    Response page ", sent, " (100 per page) of ", responses_total
            print "        uri=",response_uri,", params=",response_post_data
            print "        response_json[data].length=",len(responses_json['data'])

            response_uri = "%s%s%s%s" % (HOST, '/v3/surveys/', survey['survey_id'], '/responses/bulk')
            responses_response = sm_client.get(response_uri, params=response_post_data)
            responses_json = responses_response.json()

            # save raw responses
            #print "*** Bulk response:",responses_json
            #responses_rawdata.extend(responses_json['data'])
            for rdata in responses_json['data']:
                responses_rawdata.append(copy.deepcopy(rdata))

            print "        response_rawdata.length=",len(responses_rawdata)

    print 'Total Response is ', response_total_count
    print 'responses_rawdata has ', len(responses_rawdata), ' entries'

    # process respondent and response elements
    for response in responses_rawdata:
        if 'sid' in response['custom_variables']:
            respondent_elements={}
            respondent_elements['respondent_id'] = response['id']
            respondent_elements['date_start'] = response['date_created']
            respondent_elements['date_modified'] = response['date_modified']
            respondent_elements['status'] = "completed"
            respondent_elements['custom_id'] = ""
            # respondent list
            survey_respondents.append(copy.deepcopy(respondent_elements))

            response_elements={}
            response_elements['respondent_id'] = response['id']
            response_elements['questions'] = []

            # add session id
            session_answer = {}
            session_answer['answers'] = []
            session_answer['answers'].append({'text':response['custom_variables']['sid'], 'row':0})
            session_answer['question_id'] = response['survey_id']
            response_elements['questions'].append(copy.deepcopy(session_answer))

            # add answers
            for page in response['pages']:
                for question in page['questions']:
                    user_answer = {}
                    user_answer['question_id'] = question['id']
                    # convert answers based on question family
                    user_answer['answers'] = []
                    if 'answers' in question:
                        for answer in question['answers']:
                            answer_elements = {}
                            # matrix, menu
                            if ('row_id' in answer) and ('col_id' in answer) and ('choice_id' in answer):
                                answer_elements['row'] = answer['row_id']
                                answer_elements['col'] = answer['col_id']
                                answer_elements['col_choice'] = answer['choice_id']
                                user_answer['answers'].append(copy.deepcopy(answer_elements))
                            # matrix, single / rating / ranking
                            elif ('row_id' in answer) and ('choice_id' in answer):
                                answer_elements['row'] = answer['row_id']
                                answer_elements['col'] = answer['choice_id']
                                user_answer['answers'].append(copy.deepcopy(answer_elements))
                            # single_choice, multiple_choice
                            elif ('choice_id' in answer):
                                answer_elements['row'] = answer['choice_id']
                                user_answer['answers'].append(copy.deepcopy(answer_elements))
                            # single_choice (other)
                            elif ('other_id' in answer):
                                answer_elements['row'] = answer['other_id']
                                answer_elements['text'] = answer['text']
                                user_answer['answers'].append(copy.deepcopy(answer_elements))
                            # open_ended, multi / numerical
                            elif ('text' in answer) and ('row_id' in answer):
                                answer_elements['text'] = answer['text']
                                answer_elements['row'] = answer['row_id']
                                user_answer['answers'].append(copy.deepcopy(answer_elements))
                            # open_ended, single
                            elif ('text' in answer):
                                answer_elements['text'] = answer['text']
                                answer_elements['row'] = "0"
                                user_answer['answers'].append(copy.deepcopy(answer_elements))

                    response_elements['questions'].append(copy.deepcopy(user_answer))
            # response list
            survey_responses.append(copy.deepcopy(response_elements))

    print 'Respondent array len = ', len(survey_respondents), '; Response array len = ', len(survey_responses)

    print 'Adding respondents to DB'
    print '    contained ' + str(db.respondents.count()) + ' respondents ...'
    
    #for respondent in survey_respondents:
    #    # {respondent_id, date_start, date_modified, status, custom_id}
    #    db.respondents.find_one_and_replace({'respondent_id':respondent['respondent_id']},respondent,upsert=True)
    if survey_respondents != []:
        db.respondents.insert_many(survey_respondents)

    print '    ... now has ' + str(db.respondents.count()) + ' respondents.'

    print 'Adding responses to DB'
    print '    contained ' + str(db.responses.count()) + ' responses ...'
    new_responses = []
    for survey_response in survey_responses:
        new_responses.append(survey_response)

    if new_responses != []:
        db.responses.insert_many(new_responses)

    print '    ... now has ' + str(db.responses.count()) + ' responses.'
    
    # create table of user hash / session ID
    hashes = []
    response_hashes = []
    for response in new_responses:
        hash_answer = {}
        hash_answer['response_id'] = response['_id']
        hash_answer['respondent_id'] = response['respondent_id']
        for raw_response in responses_rawdata:
            if response['respondent_id'] == raw_response['id']:
                hash_answer['survey_id'] = raw_response['survey_id']
                hash_answer['question_id'] = raw_response['survey_id']
                hash_answer['user_hash'] = raw_response['custom_variables']['sid']
        hashes.append(copy.deepcopy(hash_answer))       

    print 'Collected hashes array len=', len(hashes)

    print 'Adding user hashes to DB'
    print '    contained ' + str(db.user_hashes.count()) + ' hashes ...'
    if hashes != []:
        db.user_hashes.insert_many(hashes)
    print '    ... now has ' + str(db.user_hashes.count()) + ' hashes.'

#################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='create database of surveys that match the name and date')
    parser.add_argument('--name', default="", dest='name',
                   help='Name of survey, default is all')
    parser.add_argument('--rebuild', action='store_true',
                   help='Rebuild DB despite presence of ./date.txt')
    #parser.add_argument('--date', default=None, dest='date',
    #               help='Date and time of last read, default is None')
    args = parser.parse_args()

    ret = run(args.name, args.rebuild)
