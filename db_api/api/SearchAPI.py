### Imports

from flask_restful import reqparse, Resource


### Request Parser
search_parser = reqparse.RequestParser()
search_parser.add_argument('query')
search_parser.add_argument('tags')
search_parser.add_argument('uid')

### Requests
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
        return self.DB.search(args['query'], tags, args['uid'])
