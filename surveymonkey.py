import json
import requests

#************************** functions *****************************************

# get_survey_list retrieves a list of surveys using authentication provided above
# input: 	survey_name - a string that references the OT; can be partial
#			client - the client that makes the requests connection
# output: survey_list - a json object that contains a list of surveys with title and id
def get_survey_list(client, survey_name):
	HOST = "https://api.surveymonkey.net"
	SURVEY_LIST_ENDPOINT = "/v2/surveys/get_survey_list"
	survey_uri = "%s%s" % (HOST, SURVEY_LIST_ENDPOINT)
	
	survey_post_data = {}
	data = '{}'
	survey_post_data["title"] = survey_name
	survey_post_data["fields"] = ["title"] 
	
	survey_response = client.post(survey_uri, data=json.dumps(survey_post_data), verify=True)
	survey_response_json = survey_response.json()
	survey_list = survey_response_json["data"]["surveys"]
	return survey_response_json

# get_respondent_list retrieves a list of respondent id's for a given survey
# input: 	uri - a string that is the survey monkey api uri endpoint for
#			survey_id - the id of the survey; use get_survey_list to obtain a survey_id
# output:  
def get_respondent_list(client, survey_id, start_date=None):
	if start_date is None:
		start_date = '2013-01-01 00:00:00'

	HOST = "https://api.surveymonkey.net"
	RESPONDENT_LIST_ENDPOINT = "/v2/surveys/get_respondent_list"
	respondent_uri = "%s%s" % (HOST, RESPONDENT_LIST_ENDPOINT)

	respondent_post_data = {}
	data = '{}'
	respondent_post_data["survey_id"] = survey_id
	respondent_post_data["start_date"] = start_date
	respondent_post_data["fields"] = ["ip_address", "date_start", "date_modified", "custom_id", "email", "recipient_id"]
	
	respondents_response = client.post(respondent_uri, data=json.dumps(respondent_post_data))
	respondents_response_json = respondents_response.json()
	respondents_ids = respondents_response_json["data"]["respondents"]
	return respondents_response_json

# get_responses retrieves the answers submitted by subjects to the OT questions
# input:
# output: 
def get_responses(client, survey_id, respondent_ids):
	HOST = "https://api.surveymonkey.net"
	RESPONSE_ENDPOINT = "/v2/surveys/get_responses"
	response_uri = "%s%s" % (HOST, RESPONSE_ENDPOINT)

	response_post_data = {}
	data = {}
	response_post_data["survey_id"] = survey_id
	response_post_data["respondent_ids"] = respondent_ids
	response_post_data["page_size"] = 1000
	
	response_response = client.post(response_uri, data=json.dumps(response_post_data))
	response_response_json = response_response.json()
	responses = response_response_json["data"]
	return response_response_json

# get_survey_details retrieves the survey questions
# input
# output
def get_survey_details(client, survey_id):
	HOST = "https://api.surveymonkey.net"
	DETAILS_ENDPOINT = "/v2/surveys/get_survey_details"
	details_uri = "%s%s" % (HOST, DETAILS_ENDPOINT)

	response_post_data = {}
	data = '{}'
	response_post_data["survey_id"] = survey_id
	response_survey_details = client.post(details_uri, data=json.dumps(response_post_data))
	response_survey_details_json = response_survey_details.json()
	# details = response_survey_details["data"]
	return response_survey_details_json