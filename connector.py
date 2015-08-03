from surveymongo_test import collect_responses

responses = collect_responses('bbd89b5513f27da801bcca6bf4279e::413')

for new_response in responses:
    for key, value in new_response.iteritems():
        print key, ':', value
    print '\n'