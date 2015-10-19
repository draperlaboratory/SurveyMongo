# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 09:49:47 2015

@author: dantraviglia
"""

import pymongo
mongoclient = pymongo.MongoClient()
db = mongoclient.answers

user_hash = '8b52f75bde2d0b7e6742e2736dccf7'

for response in db.responses.find({'user_hash':user_hash}):
    for question in response['questions']:
#         print(question)
        question_details = db.answer_table.find_one({'question_id':question['question_id']})
        if question_details != None:
            print(question_details['family'], ':', question_details['subtype'])
            print(question_details['heading'])
            for answer in question['answers']:
                if question_details['family'] != 'open_ended':
                    answer_details = db.answer_table.find_one({'answer_id':answer['row']})
                    answer_varname = db.varnames.find_one({'answer_id':answer['row']})
                    if question_details['family'] == 'matrix':
                        answer_response = db.answer_table.find_one({'answer_id':answer['col']})
                    else:
                        answer_response = answer_details
                else:
                    answer_response['position'] = '0'
                    answer_details['text'] = 'open'
                    answer_varname['varname'] = 'none'
                print(answer_details['text'], ' : ', answer_response['position'], ' - ', answer_varname['varname'])
        print('\n')