# _*_ coding:utf-8 _*_
import pandas as pd
import os
import time
import pymongo

class Put_to_Excel(object):

    def __init__(self,workbook_path=None,**mongo_infor):
        self.workbook_path = workbook_path
        self.mongo_infor = mongo_infor

    def get_mongo_conn(self):
        conn = pymongo.MongoClient(
            self.mongo_infor['host'],
            self.mongo_infor['port']
        )
        return conn

    def get_data(self):
        conn = self.get_mongo_conn()
        db = conn[self.mongo_infor['db']]
        data = db.shuidichou_user_information_new.find({}, {
            "data.baseInfo.infoId": 1,
            "data.baseInfo.targetAmount": 1,
            "data.baseInfo.amount": 1,
            "data.baseInfo.donationCount": 1,
            "data.baseInfo.beginTime": 1,
            "data.baseInfo.endTime": 1,
            "data.shareCount": 1,
            "data.treatmentInfo.diseaseName": 1,
            "data.blessingCount": 1
        })
        conn.close()
        return data

    def write_in_excel(self):
        home_link = r'https://www.shuidichou.com/cf/contribute/{}?channel=wx_ckr_task_weibo'
        data_list = self.get_data()
        jiexi_data = []
        for data in data_list:
            signle_person_data = []
            #疾病名称
            signle_person_data.append(data['data']['treatmentInfo']['diseaseName'])
            #开始时间
            start_loc_time = time.localtime(int(data['data']['baseInfo']['beginTime']/1000))
            start_time = time.strftime("%Y-%m-%d %H:%M:%S",start_loc_time)
            signle_person_data.append(start_time)
            #结束时间
            end_loc_time = time.localtime(int(data['data']['baseInfo']['endTime']/1000))
            end_time = time.strftime("%Y-%m-%d %H:%M:%S", end_loc_time)
            signle_person_data.append(end_time)
            #目标筹款金额
            signle_person_data.append(data['data']['baseInfo']['targetAmount'])
            #已筹金额
            signle_person_data.append(data['data']['baseInfo']['amount'])
            #捐款次数
            signle_person_data.append(data['data']['baseInfo']['donationCount'])
            #转发次数
            signle_person_data.append(data['data']['shareCount'])
            #加油次数
            signle_person_data.append(data['data']['blessingCount'])
            #项目链接
            signle_person_data.append(home_link.format(data['data']['baseInfo']['infoId']))
            jiexi_data.append(signle_person_data)
        index = ['diseaseName','beginTime','endTime','targetAmount','amount','donationCount','shareCount','blessingCount','link']
        jiexi_dataframe = pd.DataFrame(jiexi_data,columns = index)
        if not self.workbook_path:
            home_path = os.path.dirname(__file__)
            self.workbook_path = os.path.join(home_path,'data.xlsx')
        jiexi_dataframe.to_excel(self.workbook_path,sheet_name='user_infor',index=None)


if __name__ == '__main__':
    excel_path = ''
    mongo_infor = {
        'host': 'localhost',
        'port': 27017,
        'db': 'local'
    }
    PE = Put_to_Excel(workbook_path=excel_path,**mongo_infor)
    data = PE.write_in_excel()