'''
respondent_id_list is numerous structures of respondent info in small arrays for no apparent reason 
respondens are answers to survey questions
survey_details is the details about the survey
survey_list is a redundent list of survey names

5th table is all survey questions indexed by Session ID hash

This method of updating the 5th table is not atomic - if someone adds data while this is running that data will be lost - though that should never happen as nobody should be adding data but me. $set could maybe avoid this.
'''
debug = False

from pymongo import MongoClient
import pprint
import json, sys

client = MongoClient() #replace with url later
db = client.test

#create 5th table with unique key
collection = db.session_table
collection.drop()
collection.create_index("subject_id", unique=True)

'''
build a list of respondents using SM respondent_id_list
'''
if debug: print "\nGet all respondents IDs:\n"
respondents = []
cursor = db.respondent_id_list.find({ },{"data.respondents.respondent_id": 1}) #no way to return just the fields, always nested deep
for document in cursor:
    for item in (document["data"]["respondents"]):
        respondents.append(item["respondent_id"])
if debug: print "respondents:", respondents
print "Respondents:", len(respondents)

'''
# from the list of respondent_ids find all the questions they answered from RESPONSES
'''
for respondent_id in respondents:
    if debug: print "\n\nRespondent ID =", respondent_id
    
    if debug: print "\nFind question_id and answers from respondent:", respondent_id
    questions_from_responses = []
    cursor = db.responses.find({"data.respondent_id": respondent_id})                   #search responses
    for document in cursor:
        for datum in document["data"]:
            for question in datum["questions"]:
                # this is an array of answers and a question_id
                questions_from_responses.append(question)
                '''
                #print "len =", len(question["answers"])
                if len(question["answers"]) != 1: 
                    print "***WARNING, database format has change, data may be dropped"
                    print "len =", len(question["answers"])
                    for entry in question["answers"]:
                        json.dump(entry, sys.stdout)
                        print
                answers.append( {"question_id": question["question_id"], "answers": question["answers"][0]}) #hard coded 0, OI am ASSUMING only one entry in array.. bad?
                '''
    #if debug == False: json.dump(questions, sys.stdout);
    #if debug == False: pprint.pprint(questions) # {u'row': u'7718418739', u'text': u'justinbeiber'}],
    '''
    [{u'answers': [{u'row': u'7718418737', u'text': u'Zulaydonado'},
               {u'row': u'7718418738', u'text': u'246'},
               {u'row': u'7718418739', u'text': u'justinbeiber'}],
    '''

    
    '''
    #now find the session ID hash in the survey_details
    '''
    subject_id = ""
    if debug: print "\nFind details about those questions and answers:\n"
    if debug: print "questions_from_responses", len(questions_from_responses)
    if debug: print questions_from_responses
    for question in questions_from_responses: #for every entry in the array of questions from responses(answers and question_id)
        #search for record with that question_id
        cursor = db.survey_details.find({"data.custom_variables.question_id": question["question_id"]}) 
        l = 0
        for document in cursor: #for the only return of that search
            l += 1
            if debug : print "Survey Title:\t\t", document["data"]["title"]["text"]
            if debug: print "Question_ID:\t", question["question_id"], #just to confirm we found it
            for cust_var in document["data"]["custom_variables"]: #for every custon var, i.e. subject ID and nothing else
                if len(question["answers"]) != 1: print "***WARNING invalid format of session ID info!"
                if debug: print
                if debug: print cust_var["variable_label"],"\t", question["answers"][0]["text"]#hardcoded [0]            
                #found subject_ID!
                subject_id = question["answers"][0]["text"]
            #all_answers = question["answers"]
            #print "all answers:", all_answers
            #print document
            
            
        if l > 1 : print "*** More than one match to question_id", question["question_id"]
    if subject_id == "": 
        print "Error: Could not find subject_id for respondent ID =", respondent_id
        continue
    '''
    #We have no extracted just the session ID from those responses, there are a lot of other answers in there.
    '''
    
    #load the existing document for this subject
    user_data = {"subject_id" : subject_id, "questions" : []}
    cursor = db.session_table.find({"subject_id": subject_id})
    for document in cursor: #there can be only one, due to unique key
        user_data = document

        
    '''
    entry in questions_from_responses:
    [{u'answers': [{u'row': u'7718418737', u'text': u'Zulaydonado'},
               {u'row': u'7718418738', u'text': u'246'},
               {u'row': u'7718418739', u'text': u'justinbeiber'}],
    '''        
        
        
        
    #After reading that structure we need to reset cursor and read the answer structure
    #goal: create 
    #   {subject_ID, [{question_id, heading, {answers}}, ... ]}
    for question in questions_from_responses: #for every question in the list of questions from responses.json for this respondent id

        '''
        skip = False
        for k in user_data["questions"]: #for question in existing 5th table entry
            #print question["question_id"], k["question_id"]
            if question["question_id"] == k["question_id"]: # if the question_id is already in there then quit. 
                #print "skipable "
                skip = True
                break # or continue?!?!?
        if skip: break
        '''
        cursor = db.survey_details.find({"data.pages.questions.question_id": question["question_id"]})# get every detail entry about this question 
        for document in cursor: #more than one?
            if debug: print
            for page in document["data"]["pages"]:
                for answers in page["questions"]:
                    if answers["question_id"] == question["question_id"]:                #if question_id from survey details == question_id from responses
                        if debug: print "\nQuestion_ID:\t", question["question_id"]
                        question_id = question["question_id"]
                        if debug: print "Heading:\t", repr(answers["heading"])
                        heading = repr(answers["heading"])
                        for answer in answers["answers"]:
                            if debug : pprint.pprint(answer)
                            #print ans["answer_id"],  answer
                            #if "row" in answer: 
                            # row 7718418739 has bieber...
                            #if answer["answer_id"] == "7718418739": 
                            #    print "!!!!!!!!!!!!!!"
                            #    print question["answers"]
                            for answer_entry in question["answers"]: #for an answer structure in the list of answers from the questions in the responses table
                                if debug: print "answer_entry = ", answer_entry
                                if answer["answer_id"] == "7718418739": print "answer_entry = ", answer_entry
                                #print "answer_entry = ", answer_entry
                                if (answer["answer_id"] == answer_entry["row"]):
                                    if debug: print "Answer:\t\t", answer
                                    if answer["answer_id"] == "7718418739": print "Answer:\t\t", answer
                                    user_data["questions"].append({"question_id":question_id, "heading":heading, "answer":answer_entry}) #not answer god damnit
                                    #user_data.update({"question_id":question_id, "heading":heading, "answer":answer})
                                    if "col" in question and (answer["answer_id"] == answer_entry["col"]): print "############"
                                elif "col" in question and (answer["answer_id"] == answer_entry["col"]):#question["answers"]["col"]):
                                    if debug: print "Answer:\t\t", answer
                                    #print "new data"
                                    user_data["questions"].append({"question_id":question_id, "heading":heading, "answer":answer_entry})
                                    #user_data.update({"question_id":question_id, "heading":heading, "answer":answer})
                                #add each of those to the array of answers
                                
        


    #print "..."
    #result = db.session_table.insert_one({"subject_id": subject_id, "questions": user_data})
    #print result.inserted_id
    
    #db.session_table.update({"subject_id": subject_id}, {"subject_id": subject_id,"questions": user_data}, upsert= True)
    result = db.session_table.update({"subject_id": subject_id}, user_data, upsert= True) #TODO: could just set the question field...
    #print result
    
    #print
    #cursor = db.session_table.find({"subject_id": subject_id})
    #for document in cursor:
    #    pprint.pprint(document)
#sys.exit()

print "5th table has been built"
    
    
#run a tell
print "find ="
cursor = db.session_table.find({"subject_id": "aa4360295e344a081fbf6cf81ede91"})
for document in cursor:
    pprint.pprint(document)
print len(user_data["questions"])

