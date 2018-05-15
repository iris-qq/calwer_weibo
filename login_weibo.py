# _*_ coding:utf-8 _*_
import requests
import base64
import re
import json
import rsa
import binascii
from datetime import datetime
from urllib.parse import quote_plus
from urllib.parse import urlencode

class Login_weibo(object):
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.sess = requests.session()
        self.wei_requests_url = r'https://login.sina.com.cn/sso/prelogin.php?'
        self.main_request_url = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        self.headers ={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
        }
    
    def get_wei_requests(self):
        timestamp_13 = int(datetime.timestamp(datetime.now())*1000)
        username = self.get_username()
        wei_form_data ={
            "entry": "weibo",
            "callback": "sinaSSOController.preloginCallBack",
            "su": username,
            "rsakt": "mod",
            "checkpin": "1",
            "client": "ssologin.js(v1.4.19)",
            "_": timestamp_13
        }
        parse_data = urlencode(wei_form_data)
        wei_html = requests.get(self.wei_requests_url+parse_data).text
        wt = re.compile(r'\w+\((.*?)\)')
        wei_data = json.loads(re.findall(wt,wei_html)[0])
        return wei_data

    def get_username(self):
        username_quote = quote_plus(self.username)
        username = base64.b64encode(username_quote.encode('utf-8')).decode('utf-8')
        return username

    def get_password(self, servertime, nonce, pubkey):
        """对密码进行 RSA 的加密"""
        rsaPublickey = int(pubkey, 16)
        key = rsa.PublicKey(rsaPublickey, 65537)  # 创建公钥
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(self.password)  # 拼接明文js加密文件中得到
        message = message.encode("utf-8")
        passwd = rsa.encrypt(message, key)  # 加密
        passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制。
        return passwd


    def get_requests_data(self):
        username = self.get_username()
        timestamp_11 = int(datetime.timestamp(datetime.now()))
        wei_reqeust_data = self.get_wei_requests()
        nonce = wei_reqeust_data['nonce']
        rsakv = wei_reqeust_data['rsakv']
        servertime = wei_reqeust_data['servertime']
        pubkey = wei_reqeust_data['pubkey']
        sp = self.get_password(servertime,nonce,pubkey)
        main_form_data = {
            "entry": "weibo",
            "gateway": "1",
            "from":"" ,
            "savestate": "7",
            "qrcode_flag": False,
            "useticket": "1",
            "pagerefer": "https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F",
            "vsnf": "1",
            "su": username,
            "service": "miniblog",
            "servertime": timestamp_11,
            "nonce": nonce,
            "pwencode": "rsa2",
            "rsakv": rsakv,
            "sp": sp,
            "sr": "1280*720",
            "encoding": "UTF-8",
            "prelt": "102",
            "url": "https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype": "META"
                }
        return main_form_data

    def main(self):
        post_data = self.get_requests_data()
        html = self.sess.post(self.main_request_url,data = post_data,headers=self.headers).content.decode('gbk')
        login_status = self.login_test(html)
        if login_status:
            return self.sess

    #微博登录请求，三次跳转
    def login_test(self, login_page):
        pattern = r'location\.replace\([\'"](.*?)[\'"]\)'
        callback_url = re.findall(pattern, login_page)[0]
        login_index = self.sess.get(callback_url, headers=self.headers).text
        callback_url1 = re.findall(pattern,login_index)[0]
        login_infor = self.sess.get(callback_url1,headers = self.headers).text
        domain_pattern = r'"userdomain":"(.*?)"'
        userdomain = re.findall(domain_pattern, login_infor)[0]
        weibo_url = "https://weibo.com/" + userdomain
        weibo_page = self.sess.get(weibo_url, headers=self.headers).text
        weibo_pattern = "<em class=(.*?)>(.*?)<(.*?)>"
        user_name = re.findall(weibo_pattern, weibo_page)[9][1]
        if user_name != None:
            print(u'登录成功:' + user_name)
            return True
        else:
            print(u'登录失败')
            return False
