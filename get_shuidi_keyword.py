# _*_ coding:utf-8 _*_
import pymysql
import re
import json
from lxml import etree
from tqdm import tqdm
from time import sleep
from random import randint
from urllib.parse import unquote
from urllib.parse import urlencode
from login_weibo import Login_weibo


class Get_shuidi_keywords(object):

    def __init__(self, username, password, **mysql_infor):
        self.username = username
        self.password = password
        self.mysql_infor = mysql_infor


    def get_loged_session(self):
        Login = Login_weibo(self.username, self.password)
        sess = Login.main()
        return sess

    def get_mysql_conn(self):
        conn = pymysql.connect(host=self.mysql_infor['host'],
                               port=self.mysql_infor['port'],
                               user=self.mysql_infor['user'],
                               passwd=self.mysql_infor['passwd'],
                               db=self.mysql_infor['db'],
                               charset=self.mysql_infor['charset'])
        return conn

    def make_format_data(self, json_data):
        data_infor = []
        data = json.loads(json_data)['data']
        cards = data['cards']
        card_group = cards[0]['card_group']
        for card in card_group:
            try:
                text = card['mblog']['text']
                tree = etree.HTML(text)
                title = tree.xpath('//a[@class="k"]/text()')[0]
                pattern = re.compile(r'&u=(.*?)&ep')
                shuidi_url = re.findall(pattern, text)[0]
                decode_url = unquote(shuidi_url)
                wt = re.compile(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}')
                key_word = re.findall(wt, decode_url)[0]
                data_infor.append((title, key_word))
                print(title,key_word)
            except Exception as e:
                print(e)
                continue
        self.write_to_mysql(data_infor)

    def write_to_mysql(self, data_list):
        conn = self.get_mysql_conn()
        cur = conn.cursor()
        sql = 'insert into shuidichou_keyword_new(title,key_word) values ("%s","%s")'
        for data in tqdm(data_list):
            cur.execute(sql % data)
            sleep(0.01)
        conn.commit()
        cur.close()
        conn.close()

    def main(self):
        home_url = r'https://m.weibo.cn/api/container/getIndex?'
        sess = self.get_loged_session()
        for i in range(1,300):
            request_data = {
                "containerid": "100103type=1&q=水滴筹",
                "title": "热门-水滴筹",
                "cardid": "weibo_page",
                "extparam": "title = 热门 & mid = & q = 水滴筹",
                "luicode": "10000011",
                "lfid": "100103type = 1 & q = 水滴筹",
                "page": str(i)
            }
            url = home_url + urlencode(request_data)
            json_data = sess.get(url).content.decode('gbk')
            self.make_format_data(json_data)
            sleep(randint(30,50)+4.7)
        sess.close()

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
    KW = Get_shuidi_keywords(username, password, **mysql_infor)
    KW.main()


