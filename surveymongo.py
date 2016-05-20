import pymongo
from bson.objectid import ObjectId
import unicodedata

def setup_client():
	client = pymongo.MongoClient()
	return client

def teardown_client(client):
	client.close()

def get_question_details(question_id):
	client = setup_client()
	db = client.answers
	question_details = db.answer_table.find_one({'question_id':question_id})
	teardown_client(client)
	return question_details

def get_survey_details(survey_id):
	survey_details = []
	client = setup_client()
	db = client.answers
	cursor = db.answer_table.find({'survey_id':survey_id})
	for survey_detail in cursor:
		survey_details.append(survey_detail)
	teardown_client(client)
	return survey_details
 
def get_responses(session_id):
	responses = []
	client = setup_client()
	db = client.answers
	for response in db.responses.find({'questions.answers.text':session_id}):
		responses.append(response)
	return responses

def get_responses_dict(db, user_hash):
    print 'Getting responses from: ', user_hash
    responses_dict = {}
    responses_dict['user_hash'] = user_hash

    response_ids = db.user_hashes.find({'user_hash':user_hash})
    responses = []
    if response_ids != None:
        for r in response_ids:
            responses.append(db.responses.find_one({'_id':r['response_id']}))

    #for response in db.responses.find({'user_hash':user_hash}):
    for response in responses:
        # get response times
        respondent_info = db.respondents.find_one({'respondent_id':response['respondent_id']})
        start_date = respondent_info['date_start']
        end_date = respondent_info['date_modified']
        for question in response['questions']:
            # get responses to questions
            #question_details = db.questions.find_one({'question_id':question['question_id']})
            question_details = db.answer_table.find_one({'question_id':question['question_id']})
            #print question_details
            if question_details != None:
                if 'survey_id' in question_details:
                    survey_id = question_details['survey_id']
                    if db.sessions.find_one({'survey_id':survey_id}) == None:
                        print 'response to missing survey #%s' % survey_id
                        continue
                    if db.time_varnames.find_one({'survey_id':survey_id, 'time_id':'1'}) == None:
                        title = db.sessions.find_one({'survey_id':survey_id})['title']
                        print 'missing time config for survey #%s (%s)' % (survey_id, title)
                        continue
                    start_date_varname = db.time_varnames.find_one({'survey_id':survey_id, 'time_id':'1'})['varname']
                    end_date_varname = db.time_varnames.find_one({'survey_id':survey_id, 'time_id':'0'})['varname']
                    responses_dict.update({start_date_varname:start_date, end_date_varname:end_date})
                for answer in question['answers']:
                    if question_details['family'] in ['open_ended']:
                        if question_details['subtype'] in ['multi']:
                            answer_varname = db.varnames.find_one({'answer_id':answer['row']})['varname']
                        else:
                            answer_varname = db.varnames.find_one({'question_id':question['question_id']})['varname']
                        answer_response = answer['text']
                    elif question_details['subtype'] in ['menu']:
                        #user_choice = {}
                        #try:
                        #    user_choice = [x for x  in question_details['answers'] if x['answer_id'] == answer['col_choice']][0]
                        #except:
                        #    print '***************************'
                        #    print response
                        #    print question
                        #    print answer
                        #    print question_details['answers']
                        #    user_choice = [x for x  in question_details['answers'] if x['answer_id'] == answer['col_choice']]
                        #    print user_choice
                        #    raise
                        unrolled = []
                        for choice in question_details['answers']:
                            try:
                                for inner_choice in choice['items']:
                                    unrolled.append(inner_choice)
                            except KeyError:
                                unrolled.append(choice)
                        user_choice = [x for x  in unrolled if x['answer_id'] == answer['col_choice']][0]

                        answer_response = user_choice['position']
                        #answer_response = db.answers.find_one({'answer_id':answer['col_choice']})['position']
                        answer_varname = db.varnames.find_one({'answer_id':answer['row']})['varname']
                    else:
                        answer_varname = ''
                        if question_details['subtype'] == 'rating':
                            answer_varname = db.varnames.find_one({'answer_id':answer['col']})['varname']
                        else:
                            answer_varname = db.varnames.find_one({'answer_id':answer['row']})['varname']

                        if question_details['family'] in ['matrix']:
                            user_choice = [x for x  in question_details['answers'] if x['answer_id'] == answer['col']][0]
                            answer_response = user_choice['position']
                            #if 'confidence' in question_details['heading']:
                            #    print 'Y:', question_details['subtype']
                            #else:
                            #    print 'N:', question_details['subtype']
                            #    print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
                            #    print question_details
                            #    print answer
                            #    print user_choice
                            #    print answer_varname
                            #    print answer_response
                            #print user_choice
                            #print answer
                            #answer_response = db.answers.find_one({'answer_id':answer['col']})['position']
                        else:
                            user_choice = [x for x  in question_details['answers'] if x['answer_id'] == answer['row']][0]
                            if user_choice['type'] == 'row':
                                answer_response = [x for x  in question_details['answers'] if x['answer_id'] == answer['row']][0]['position']
                            elif user_choice['type'] == 'other':
                                answer_response = answer['text']
                            else:
                                raise AnswerTypeError
                     
                            #answer_response = db.answers.find_one({'answer_id':answer['row']})['position']
                    #if 'CON' in answer_varname:
                    #    print answer_varname, answer_response
                    try:
                        responses_dict.update({answer_varname:unicodedata.normalize('NFKD',answer_response).encode('ascii','ignore')})
                    except TypeError:
                        responses_dict.update({answer_varname:str(answer_response)})

 
    #print responses_dict
    return responses_dict

