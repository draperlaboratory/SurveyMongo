# ## Test connections between collections

import pymongo
mongoclient = pymongo.MongoClient()
db = mongoclient.answers

for response in db.responses.find({'questions.answers.text':'bbd89b5513f27da801bcca6bf4279e::413'}):
    for question in response['questions']:
        question_id = question['question_id']
        print '(Question ID:)', question_id

        # get the question heading
        try:
            heading = db.answer_table.find_one({'question_id':question_id})['heading']
        except TypeError:
            heading = 'sessionID question'
        print '(Question:)', heading
        
        # get the question details
        question_elements = db.answer_table.find_one({'question_id':question_id})
        try:
            family = question_elements['family']
            subtype = question_elements['subtype']
        except TypeError:
            family = 'SID'
            subtype = 'open'
        print '(Family:)', family 
        print '(Subtype:)', subtype
        
        # get the varnames
        try:
            varname = db.varnames.find_one({'question_id':question_id})['varname']
        except:
            varname = 'none'
        print '(Varname:)', varname
        
        # switch on question family and print responses
        if family == 'matrix':
            for answer in question['answers']:
                for row in db.answer_table.find({'answer_id':answer['row']}):
                    key = row['text']
                for col in db.answer_table.find({'answer_id':answer['col']}):
                    value = col['position']
                    text = col['text']
                print '(Answer:)', key, value, '-', text
        elif family == 'open_ended':
            for answer in question['answers']:
                print '(Answer:)', answer['text']
        elif family == 'single_choice':
            for answer in question['answers']:
                for row in db.answer_table.find({'answer_id':answer['row']}):
                    print '(Answer:)', row['position'], '-', row['text']
        else:
            print question['answers']

        print '\n'