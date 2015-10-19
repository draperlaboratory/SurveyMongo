import requests
import surveymonkey
import sys
import pandas

client = requests.session()
client.headers = {
	"Authorization" : "bearer paTBz61kMlD0mPWrsaHR3921EuYbHlBvqU0GDZQ.5nahBvB1GbdZpbh2WnOzXY4S1m4CvPfPmXO9cABCSafzRjNeH9zln7ik1mnK.DPSQSI=", 
	"Content-Type" : "application/json"
}
client.params = {
	"api_key": "rsjhxbgh8sbjkxytn7fdkvdu" 
}

i=0
survey_name = ''
for s in sys.argv:
	if i != 0 :
		survey_name = survey_name + str(s) + ' '
	i = i + 1

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
surveydetailsdf.to_csv('UT_time.csv', encoding='utf-8')
