import pymongo

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
    responses_dict = {}
    responses_dict['user_hash'] = user_hash
    for response in db.responses.find({'user_hash':user_hash}):
        # get response times
        respondent_info = db.respondents.find_one({'respondent_id':response['respondent_id']})
        start_date = respondent_info['start_date']
        end_date = respondent_info['end_date']
        for question in response['questions']:
            # get responses to questions
            question_details = db.questions.find_one({'question_id':question['question_id']})
            if question_details != None:
                if 'survey_id' in question_details:
                    survey_id = question_details['survey_id']
                    start_date_varname = db.time_varnames.find_one({'survey_id':survey_id, 'time_id':'start'})['varname']
                    end_date_varname = db.time_varnames.find_one({'survey_id':survey_id, 'time_id':'end'})['varname']
                    responses_dict.update({start_date_varname:start_date, end_date_varname:end_date})
                for answer in question['answers']:
                    if question_details['family'] in ['open_ended']:
                        if question_details['subtype'] in ['multi']:
                            answer_varname = db.varnames.find_one({'answer_id':answer['row']})['varname']
                        else:
                            answer_varname = db.varnames.find_one({'question_id':question['question_id']})['varname']
                        answer_response = answer['text']
                    elif question_details['subtype'] in ['menu']:
                        answer_response = db.answers.find_one({'answer_id':answer['col_choice']})['position']
                        answer_varname = db.varnames.find_one({'answer_id':answer['row']})['varname']
                    else:
                        answer_varname = db.varnames.find_one({'answer_id':answer['row']})['varname']
                        if question_details['family'] in ['matrix']:
                            answer_response = db.answers.find_one({'answer_id':answer['col']})['position']
                        else:
                            answer_response = db.answers.find_one({'answer_id':answer['row']})['position']
                    responses_dict.update({answer_varname:str(answer_response)})
    return responses_dict

