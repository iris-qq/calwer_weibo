# _*_ coding:utf-8 _*_
import requests
import pymongo
import json
from tqdm import tqdm
from time import sleep
from get_shuidi_keyword import Get_shuidi_keywords

class Get_shuidi_information(object):
    def __init__(self,mysql_conn,**mongo_infor):
        self.mysql_conn = mysql_conn
        self.mongo_infor = mongo_infor
        self.shuidi_url = r'https://api.shuidichou.com/api/cf/v4/get-funding-info'

    def get_key_words(self):
        conn = self.mysql_conn
        sql = 'select distinct key_word from shuidichou_keyword_new'
        with conn.cursor() as cur:
            cur.execute(sql)
            data_list = cur.fetchall()
        conn.close()
        return data_list

    def get_mongo_conn(self):
        conn = pymongo.MongoClient(
            self.mongo_infor['host'],
            self.mongo_infor['port']
        )
        return conn

    def write_to_mongo(self,infor):
        conn = self.get_mongo_conn()
        db = conn[self.mongo_infor['db']]
        db.shuidichou_user_information_new.insert(infor)
        conn.close()

    #获取加油的数据，加油的数量是一个单独的post请求
    def get_blessingCount(self,key_word):
        blessing_url = r'https://api.shuidichou.com/api/cf/v4/info-blessing/get'
        blessing_json = requests.post(blessing_url,data=key_word).text
        blessing_data = json.loads(blessing_json)
        blessing_num = blessing_data['data']['blessingCount']
        return blessing_num

    def main(self):
        key_words_list = self.get_key_words()
        for key_word in tqdm(key_words_list):
            post_data = {"infoUuid":key_word[0]}
            blessing_num = self.get_blessingCount(post_data)
            data = requests.post(self.shuidi_url,data=post_data).text
            dict_data = json.loads(data)
            dict_data['data']['blessingCount']=blessing_num
            self.write_to_mongo(dict_data)
            print('正在写入数据，请稍后....')
            sleep(1.5)


if __name__ == '__main__':
    username = ''
    password = ''
    mysql_infor = {
        'host': 'localhost',
        'port': 3306,
        'user': 'wqq',
        'passwd': '123456',
        'db': 'pachong',
        'charset': 'utf8'
    }
    mongo_infor = {
        'host':'localhost',
        'port':27017,
        'db':'local'
    }
    conn = Get_shuidi_keywords(username,password,**mysql_infor).get_mysql_conn()
    GI = Get_shuidi_information(conn,**mongo_infor)
    GI.main()
