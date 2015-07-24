import get_respondent_ids, get_responses, get_survey_details, get_survey_ids
import datetime

now = datetime.datetime.now()
print ("Current date & time = %s" % now)

try:
    f = open("date.txt", "r") #open date file if it exists
    date = f.readln()
except:
    date = '2015-07-22 00:00:00'
print (date)

#todo: get names of surveys and share it, save 2 out of 1269 transfers
#todo: there may also be some coherence with respondents

with open("respondent_id_list.json", "w") as f:
    f.write("%s"%get_respondent_ids.run(name="", date=date))

with open("get_responses.json", "w") as f:
    f.write("%s"%get_responses.run(name="", date=date))

with open("survey_details.json", "w") as f:
    f.write("%s"%get_survey_details.run(name="", date=date))
  

#get today's date
with open("date.txt", "w") as f:
    #write today's date to file
    f.write("%s"%date)

print ("Total execution time for download script: %s"%(datetime.datetime.now()-now))