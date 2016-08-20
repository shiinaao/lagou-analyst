import pymongo

host = 'localhost'
port = 27017
dbname = 'lagou'
analystdb = 'analyst'


class mongo(object):

    def __init__(self, dbname):
        self.client = pymongo.MongoClient(host=host, port=port)
        self.db = self.client[dbname]

    def __call__(self, table):
        return self.db[table]


lagou = mongo('lagou')
analyst = mongo('analyst')
