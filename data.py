from mongo import lagou, analyst
import requests
import json
import time
import datetime
import pymongo
import os
from config import data_config, handle_config

proxies = {'socks': '127.0.0.1:9050'}


class KeyWord(object):
    url = 'http://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false'
    data = {'first': False, 'pn': 1, 'kd': ''}

    def __init__(self, keyword):
        self.keyword = keyword
        self.data['kd'] = self.keyword

    def response2json(self):
        result = requests.post(url=self.url, data=self.data, proxies=proxies)
        data = json.loads(result.text)
        return data

    def tojson(self, data):
        return json.dumps(data)


    def get_total_num(self):
        result = self.response2json()
        self.count = result['content']['positionResult']['totalCount']
        self.pageSize = result['content']['pageSize']
        return self.count

    def get_page_no(self):
        # result = self.response2json()
        # table = mongo('history')
        # table.insert({'name': result['content']['positionResult']['queryAnalysisInfo']['positionName'],
        #               'count': result['content']['positionResult']['totalCount'],
        #               'timestamp': datetime.datetime.utcnow()})
        div = divmod(self.get_total_num(), self.pageSize)
        if div[1] == 0:
            return div[0]
        else:
            return div[0] + 1

    def update_all_data(self):
        table = lagou(self.keyword)
        page_count = self.get_page_no()
        id_list = self.get_id_list()
        add_count = 0
        for i in range(1, page_count + 1):
            print('%s: %s/%s' % (self.keyword, i, page_count))
            self.data['pn'] = i
            res = self.response2json()
            result = res['content']['positionResult']['result']
            for item in result:
                if item['publisherId'] in id_list:
                    id_list.remove(item['publisherId'])
                else:
                    table.insert(item)
                    add_count += 1
            time.sleep(data_config.download_interval)
        # print('del num', len(id_list))
        table = lagou('history')
        table.insert({'name': self.keyword, 'timestamp': datetime.datetime.utcnow(),
                      'count': self.count, 'add_count': add_count, 'del_count': len(id_list)
                      })
        for i in id_list:
            table.remove({'positionId': i})
        print('update 0k')

    def get_id_list(self):
        table = lagou(self.keyword)
        result = table.find({}, {'positionId': 1, '_id': 0})
        id_list = [i for i in result]
        return id_list

    def del_redundancy(self):
        table = lagou(self.keyword)
        all = [i['positionId'] for i in table.find({}, {'_id': 0, 'positionId': 1})]
        distinct = table.distinct('positionId')
        for i in distinct:
            all.remove(i)
        for i in all:
            table.delete_one({'positionId': i})
        print('del redundancy ok, del total: %s' % len(all))
        # for i in result:
        #     table.remove({'positionId': i})
        # print('del 0k')

    def last_update_more_than(self, days=14):
        table = lagou('history')
        result = table.find({'name': self.keyword}).sort('timestamp', pymongo.DESCENDING)
        # return result[1]['timestamp']
        # print(result.count())
        if result.count() == 0:
            return True
        else:
            return datetime.datetime.utcnow() - result[0]['timestamp'] > datetime.timedelta(days)

    def analyst_all(self):
        analyst_item = ['jobNature', 'education', 'workYear']
        for key in analyst_item:
            data = self.analyst_one(key)
            self.analyst_save(key, data)
        self.analyst_save('salary', self.analyst_salary())
        self.analyst_save('city', self.analyst_city())

    def analyst_save(self, key, data):
        target = analyst(self.keyword)
        target.insert({'name': key, 'data': data, 'time': datetime.datetime.today()})
        try:
            if not os.path.exists('static/data/%s/' % self.keyword):
                os.mkdir('static/data/%s/' % self.keyword)
            with open('static/data/%s/%s' % (self.keyword, key), 'w') as f:
                f.write(self.tojson(data))
        except:
            print('directory permission denied')

    def analyst_one(self, key):
        source = lagou(self.keyword)
        # target = analyst(self.keyword)
        result = source.find({}, {'_id': 0, key: 1})
        # print(self.keyword, key, result.count())
        key_list = []
        for i in result:
            key_list.append(i[key])
        key_set = set(key_list)
        # print(key_set)
        data = {}
        for i in key_set:
            data[i] = key_list.count(i)
        return data

    def analyst_salary(self):
        temp_data = self.analyst_one('salary')
        data = {'1-5k': 0, '6-10k': 0, '11-15k': 0, '16-20k': 0, '21-25k': 0, '26-30k': 0, '30k以上': 0}
        for item in temp_data.keys():
            if '-' in item:
                lower, upper = item.split('-')
                sal = int((int(lower[:-1]) + int(upper[:-1])) / 2)
            else:
                sal = int(item.split('k')[0])
            if 1 < sal < 5:
                data['1-5k'] += temp_data[item]
            elif 6 < sal < 10:
                data['6-10k'] += temp_data[item]
            elif 11 < sal < 15:
                data['11-15k'] += temp_data[item]
            elif 16 < sal < 20:
                data['16-20k'] += temp_data[item]
            elif 21 < sal < 25:
                data['21-25k'] += temp_data[item]
            elif 26 < sal < 30:
                data['26-30k'] += temp_data[item]
            elif 30 < sal:
                data['30k以上'] += temp_data[item]
        return data

    def analyst_city(self):
        temp_data = self.analyst_one('city')
        data = {'其他': 0}
        total = sum(temp_data.values())
        for city in temp_data.keys():
            if temp_data[city] / total >= 0.02:
                data[city] = temp_data[city]
            else:
                data['其他'] += temp_data[city]
        return data


def all_job_analyst():
    table = lagou('history')
    data = []
    for job in handle_config.moniter:
        result = table.find({'name': job}).sort('timestamp', pymongo.DESCENDING)
        data.append({'text': result[0]['name'], 'size': result[0]['count']})
    with open('static/data/all_job', 'w') as f:
        f.write(json.dumps(data))