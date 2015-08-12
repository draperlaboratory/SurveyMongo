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

