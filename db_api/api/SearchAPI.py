###############
### Imports ###
###############
from flask_restful import reqparse, Resource
from db_api.extensions import logger
import sys

######################
### Request Parser ###
######################
search_parser = reqparse.RequestParser()
search_parser.add_argument('query')
###search_parser.add_argument('tags', action='append')
search_parser.add_argument('tags')
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
        print('Categories: {}'.format(cats), file=sys.stderr)
        return self.DB.search(query    = args['query'],
                              tags     = args['tags'],
                              category = cats,
                              uid      = args['uid'])
"""

class SearchAPI(Resource):
    def __init__(self, DB, resource='all'):
        self.DB = DB
        self.search_resource = resource

    def get(self):
        args = search_parser.parse_args()
        tags = args['tags']
        if tags != '' and tags != None:
            tags = tags.split(';')
        print('args[tags] = ', tags)
        return self.DB.search(query=args['query'], tags=tags, uid=args['uid'])
        """
