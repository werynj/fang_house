# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import urllib.request
from fangtianxia.items import ApartmentItem
from fangtianxia.items import BuildingdetailItem
from fangtianxia.items import BuildingItem
import os
import codecs
import json

class FangtianxiaPipeline(object):
    # __init__方法是可选的，做为类的初始化方法
    def __init__(self):
        # 创建了一个文件
        # self.filename = open("teacher.json", "w")
        pass

    # process_item方法是必须写的，用来处理item数据
    def process_item(self, item, spider):

        if item.__class__.__name__ == 'ApartmentItem':
            print("output1")
            data = dict(item)
            print(data)
            path = 'G:\\房天下\\'+data['city']+'\\'+data['area']+'\\'+data['building']+"\\"+"Apartment_layout"
            # 判断结果
            if not (os.path.exists(path)):
                os.makedirs(path)

            if data['imgname'] != '' and data['imgurl'] != '':
                data['imgname'] =data['imgname'].replace('/','_').replace('\\','_')\
                    .replace('*','_').replace('#','_').replace('?','_').replace(' ','_')
                imgname =path +'\\'+data['imgname']
                imgurl = data['imgurl']
                print("image:",imgname,imgurl)
                urllib.request.urlretrieve(imgurl, imgname)

        if item.__class__.__name__ == 'BuildingdetailItem':
            print("output2")
            data = dict(item)
            print(data)
            path = 'G:\\房天下\\'+data['city']+'\\'+data['area']+'\\'+data['building']
            # 判断结果
            if not (os.path.exists(path)):
                os.makedirs(path)

            filename = path +"\\"+data['building']+".txt"
            file = codecs.open(filename, "w+", encoding="utf-8")
            content = json.dumps(data['basicinfo'], ensure_ascii=False) + "\n"
            file.write(content)
            file.close()

            filename = path + "\\" + data['building'] + ".json"
            file = codecs.open(filename, "w+", encoding="utf-8")
            content = json.dumps(data['basicinfo'], ensure_ascii=False) + "\n"
            file.write(content)
            file.close()

            filename = path + "\\" + 'link.txt'
            file = codecs.open(filename, "w+", encoding="utf-8")
            content = data['link']
            file.write(content)
            file.close()

        if item.__class__.__name__ == 'BuildingItem':
            print("output3")
            data = dict(item)
            print(data)
            path = 'G:\\房天下\\'+data['city']+'\\'+data['area']+'\\'+data['building']+"\\"+"Design_sketch"
            # 判断结果
            if not (os.path.exists(path)):
                os.makedirs(path)

            if data['imgname'] != '' and data['imgurl'] != '':
                for i in range(len(data['imgurl'])):
                    data['imgname'][i] = data['imgname'][i].replace('/','_').replace('\\','_')\
                    .replace('*','_').replace('#','_').replace('?','_').replace(' ','_')
                    imgname =path +'\\'+data['imgname'][i]+str(i)+'.jpg'
                    imgurl = data['imgurl'][i]
                    print("image:",imgname,imgurl)
                    urllib.request.urlretrieve(imgurl, imgname)
        return item

    # close_spider方法是可选的，结束时调用这个方法
    def close_spider(self, spider):
        # self.file.close()
        pass
