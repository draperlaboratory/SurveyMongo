#this is slow and dumb, probably should be deleted from repo
import json
import sys
from pprint import pprint
import get_respondent_ids
import get_responses
import get_survey_details
import get_survey_ids

#file generated by get_survey_names.sh before this runs 
with open("surveys.json") as f:
    data = json.load(f)
    for entry in data["data"]["surveys"]:
        title = entry["title"]
        print "Downloading data for", title
        with open("respondent_id_list.json", "a") as fout:
            temp = get_respondent_ids.run(title)
            print temp
            if temp != None: fout.write("%s"%temp)
        sys.exit()
        with open("responses.json", "a") as fout:
            temp = get_responses.run(title)
            if temp != None: fout.write("%s"%temp)
        with open("survey_details.json", "a") as fout:
            temp = get_survey_details.run(title)
            #print temp
            if temp != None: fout.write("%s"%temp)
        with open("survey_ids.json", "a") as fout:
            temp = get_survey_ids.run(title)
            if temp != None: fout.write("%s"%temp)
    #now process that data, or keep appending...