from mongo import lagou, analyst
import requests
import json
import time
import datetime
import re

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

    def get_page_no(self):
        result = self.response2json()
        # table = mongo('history')
        # table.insert({'name': result['content']['positionResult']['queryAnalysisInfo']['positionName'],
        #               'count': result['content']['positionResult']['totalCount'],
        #               'timestamp': datetime.datetime.utcnow()})
        self.count = result['content']['positionResult']['totalCount']
        div = divmod(self.count, result['content']['pageSize'])
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
            time.sleep(2)
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
        result = table.distinct('positionId')
        # print(result)
        print(len(result))
        # for i in result:
        #     table.remove({'positionId': i})
        # print('del 0k')

    def analyst_all(self):
        analyst_item = ['city', 'salary', 'jobNature', 'education', 'workYear']
        for key in analyst_item:
            data = self.analyst_one(key)
            self.analyst_save(key, data)
        self.analyst_salary()

    def analyst_save(self, file, data):
        target = analyst(self.keyword)
        target.insert({'data': data, 'time': datetime.datetime.utcnow()})
        try:
            with open('static/data/'+file, 'w') as f:
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
        self.analyst_save('salary', data)