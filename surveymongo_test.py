# ## Test connections between collections

import pymongo, copy
mongoclient = pymongo.MongoClient()
db = mongoclient.answers

def collect_responses(session_id):
    responses = []
    for response in db.responses.find({'questions.answers.text':session_id}):
        for question in response['questions']:
            response_details = {}
            question_id = question['question_id']
            # print '(Question ID:)', question_id
            response_details['question_id'] = copy.copy(question_id)

            # get the question heading
            try:
                heading = db.answer_table.find_one({'question_id':question_id})['heading']
            except TypeError:
                heading = 'sessionID question'
            # print '(Question:)', heading
            response_details['heading'] = copy.copy(heading)
            
            # get the question details
            question_elements = db.answer_table.find_one({'question_id':question_id})
            try:
                family = question_elements['family']
                subtype = question_elements['subtype']
            except TypeError:
                family = 'SID'
                subtype = 'open'
            # print '(Family:)', family 
            # print '(Subtype:)', subtype
            response_details['question_family'] = copy.copy(family)
            response_details['question_subtype'] = copy.copy(subtype)
            
            # get the varnames
            try:
                varname = db.varnames.find_one({'question_id':question_id})['varname']
            except:
                varname = 'none'
            # print '(Varname:)', varname
            response_details['question_varname'] = copy.copy(varname)
            
            # switch on question family and print responses
            if family == 'matrix':
                for answer in question['answers']:
                    for row in db.answer_table.find({'answer_id':answer['row']}):
                        key = row['text']
                    for col in db.answer_table.find({'answer_id':answer['col']}):
                        position = col['position']
                        text = col['text']
                    # print '(Answer:)', key, value, '-', text
                    response_details['answer_key'] = copy.copy(key)
                    response_details['answer_position'] = copy.copy(position)
                    response_details['answer_text'] = copy.copy(text)
            elif family == 'open_ended':
                for answer in question['answers']:
                    text = answer['text']
                    # print '(Answer:)', answer['text']
                    response_details['answer_text'] = copy.copy(text)
            elif family == 'single_choice':
                for answer in question['answers']:
                    for row in db.answer_table.find({'answer_id':answer['row']}):
                        position = row['position']
                        text = row['text']
                        # print '(Answer:)', position, '-', text
                        response_details['answer_position'] = copy.copy(position)
                        response_details['answer_text'] = copy.copy(text)
            else:
                # print question['answers']
                response_details['answer_details'] = copy.copy(question['answers'])

            # print '\n'
            responses.append(copy.deepcopy(response_details))

    return responses