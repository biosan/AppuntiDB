###############
### Imports ###
###############
from flask_restful import reqparse, Resource

######################
### Request Parser ###
######################
search_parser = reqparse.RequestParser()
search_parser.add_argument('query')
search_parser.add_argument('tags', action='append')
### TODO: Add to global config.
categories = ['teacher', 'university', 'subject', 'year']
for c in categories:
    search_parser.add_argument(c)
search_parser.add_argument('uid')

################
### Requests ###
################
class SearchAPI(Resource):
    def __init__(self, DB):
        self.DB = DB

    def get(self):
        args = search_parser.parse_args()
        cats = {c:args.get(c) for c in categories if args.get(c) != None}
        return self.DB.search(query    = args['query'],
                              tags     = args['tags'],
                              category = cats,
                              uid      = args['uid'])