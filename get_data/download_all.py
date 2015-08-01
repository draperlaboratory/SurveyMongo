import get_respondent_ids, get_responses, get_survey_details, get_survey_ids
import datetime, json
import sys

now = datetime.datetime.now()
print ("Current date & time = %s" % now)

try:
    f = open("date.txt") #open date file if it exists
    date = f.readline()
    print "Last update on:", date
    f.close()
except IOError as e:
    #print "I/O error({0}): {1}".format(e.errno, e.strerror)
    date = '2011-07-22 00:00:00'
    print "date.txt not found, using default date", date
    #print sys.exc_info()[0]
    
#todo: get names of surveys and share it, save 2 out of 1269 transfers
#todo: there may also be some coherence with respondents

with open("respondent_id_list.json", "w") as f:
    ret = get_respondent_ids.run(name="", date=date)
    for item in ret:
        json.dump(item, f)

with open("responses.json", "w") as f:
    ret = get_responses.run(name="", date=date)
    for item in ret:
        json.dump(item, f)

with open("survey_details.json", "w") as f:
    ret = get_survey_details.run(name="", date=date)
    for item in ret:
        json.dump(item, f)


#get today's date
with open("date.txt", "w") as f:
    #write today's date to file
    f.write("%s"%now.strftime("%Y-%m-%d %H:%M:%S"))#remove split seconds, they break survey monkey

print ("Total execution time for download script: %s"%(datetime.datetime.now()-now))