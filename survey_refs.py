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
	print("Unable to find " + survey_name)
	exit(0)

surveydetails = []

for survey in survey_list['data']['surveys']:
	print('Processing '+survey['title'])
	survey_details = {}
	survey_details[survey['survey_id']] = surveymonkey.get_survey_details(client, survey['survey_id'])

	# surveydetailsdf = pandas.DataFrame(columns=['Survey ID', 'Page', 'Page heading', 'Question ID', 'Question Heading', 'Answer ID', 'Answer Text'])

	# uncomment this next line for separate files
	# surveydetails = []
	pages = survey_details[survey['survey_id']]['data']['pages']
	for page in pages:
		for question in page['questions']:
			if 'answers' in question and len(question['answers']) > 0:
				answers = question['answers']
			else:
				answers = [{'answer_id':'1', 'text':'open_ended?'}]
			for answer in answers:
				surveydetails.append({'Survey Title':survey['title'],
					'Survey ID':survey['survey_id'], 
					'Page':page['position'], 
					'Page Heading':page['heading'], 
					'Question type':question['type']['family']+':'+question['type']['subtype'],
					'Question ID':question['question_id'], 
					'Question Heading':question['heading'], 
					'Answer ID':answer['answer_id'], 
					'Answer Text':answer['text']})

surveydetailsdf = pandas.DataFrame(surveydetails)
surveydetailsdf.sort(columns=['Page'], inplace=True)
surveydetailsdf.reset_index(inplace=True)
cols = ['Survey ID', 'Page', 'Page Heading', 'Question type', 'Question ID', 'Question Heading', 'Answer ID', 'Answer Text']
surveydetailsdf = surveydetailsdf[cols]
surveydetailsdf.to_csv('UT.csv', encoding='utf-8')
