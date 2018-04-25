# -*- coding:utf-8 -*-
import scrapy
from time import sleep
import urllib.request
from fangtianxia.items import ApartmentItem
from fangtianxia.items import BuildingdetailItem
from fangtianxia.items import BuildingItem
import time
import re
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
import codecs

class FangSpider(scrapy.Spider):
    name = 'fang'
    allowed_domains = ['fang.com']
    filename = "./fangtianxia/CITY1.ini"

    lines = []
    fd = codecs.open(filename)
    links = fd.read()
    print(links)
    link = links.split()

    fd.close()
    start_urls = link
    # start_urls = ['http://newhouse.hs.fang.com/house/s/']
    print("link", start_urls, len(link))
    start=0
    end = '/'
    url = start_urls[0] + 'b9'

    def parse(self, response):
        print("start")
        print(response.url,len(response.url))
        self.url = response.url + 'b9'
        print("url",self.url)

        href = response.xpath('//div[@id="sjina_C01_47"]//a/@href').extract()[-1]
        print("href",href,type(href))
        end = int(href[-3:-1])

       #pages
        if self.start <= end:
            self.start += 1
            print("pagelink:",self.url+ str(self.start) + self.end)
            yield scrapy.Request(self.url + str(self.start) + self.end, callback=self.parse_item)

    def parse_item(self, response):
        print("page list")
        # print(end)
        links = response.xpath('//div[@class="nlc_details"]//div[@class="nlcd_name"]/a/@href').extract()
        names = response.xpath('//div[@class="nlc_details"]//div[@class="nlcd_name"]/a/text()').extract()
        print("ab",links,len(links),names)
        name=[]
        for i in names:
            i=i.strip()#.replace('\t','').replace('\n','').replace(' ','')
            name.append(i)
        print("name",name)

        #buildings
        for link in links:
            print(link)
            yield scrapy.Request(link, callback=self.parse_items)


    def parse_items(self, response):
        print("debug02")
        # print(response.url)

        # href = response.xpath('//div[@id="header-wrap"]//a[contains(text(),"楼盘相册")]/@href').extract()[0]
        # if href != []:
        #     print("continue")
        #     print("href1", href)
            # yield scrapy.Request(href, callback=self.parse_photo)

        html = response.body.decode('gb18030')
        doc = pq(html)
        photourl = doc('#header-wrap a:contains("楼盘相册")').attr('href')
        if photourl:
            yield scrapy.Request(photourl, callback=self.parse_photo)
            print("photourl", photourl)


        href3 = response.xpath('//div[@id="header-wrap"]//a[contains(text(),"楼盘详情")]/@href').extract()
        if href3 != []:
            print("href3", href3[0])
            href = href3[0]
            yield scrapy.Request(href, callback=self.parse_housedetail)

    def parse_photo(self, response):
        print("debug03")
        item = BuildingItem()
        # print(response.body.decode('gbk'))
        # href1 = response.xpath('//*[@id="suofang"]//span[contains(text(),"效果图")]/../@href').extract()
        # print("href1", href1)
        # if href1 != []:
        #     href = href1[0]
        #     yield scrapy.Request(href, callback=self.parse_housesphoto)

        doc = pq(response.body.decode('gb18030'))
        buildingurl = doc('#suofang a:contains("效果图")').attr('href')
        print("buildingurl", buildingurl)
        if buildingurl:
            yield scrapy.Request(buildingurl, callback=self.parse_housesphoto)

        href2 = response.xpath('//*[@id="suofang"]//span[contains(text(),"户型")]/../@href').extract()
        print("href2", href2)
        if href2 != []:
            href = href2[0]
            yield scrapy.Request(href, callback=self.parse_housetypephoto)

    def parse_housesphoto(self, response):
        print("debug041")
        item = BuildingItem()
        html = response.body.decode('gb18030')
        list = []
        name = []
        doc = pq(html)

        url1 = doc('#gaoqinglist > li  a   img')
        name1 = doc('#gaoqinglist > li  a   p')
        print('url1', url1, name1)
        for url in url1.items():
            link = url.attr('src')
            link = link[:-10] + '850x576.jpg'
            print("line2l", link)
            list.append(link)
        for url in name1.items():
            print("line2l", url.text())
            name.append(url.text())

        city = doc('.header_mnav>p > a:nth-child(2)')
        item['city'] = city.text()[0:-2]
        area = doc('.header_mnav>p > a:nth-child(3)')
        item['area'] = area.text()[0:-2]
        building = doc('.header_mnav>p > a:nth-child(4)')
        item['building'] = building.text()
        item['imgurl'] = list
        item['imgname'] = name
        print(item)


        yield item

        # if list != []:
        #     for href in list:
        #         yield scrapy.Request(href, callback=self.parse_saveimage)

    def parse_housetypephoto(self, response):
        print("debug042")
        links = response.xpath('//*[@id="huxinsy_E04_08"]/a/@href').extract()
        print("href", links)
        if links != []:
            for link in links:
                yield scrapy.Request(link, callback=self.parse_saveimage)

    def parse_saveimage(self, response):
        print("debug05")
        item = ApartmentItem()
        item['city'] = response.xpath('//*[@class="header_mnav"]/p/a[2]/text()').extract()[0][0:-2]
        item['area'] = response.xpath('//*[@class="header_mnav"]/p/a[3]/text()').extract()[0][0:-2]
        item['building'] = response.xpath('//*[@class="header_mnav"]/p/a[4]/text()').extract()[0]
        src = response.xpath('//*[@id="_D02_03"]/img/@src').extract()
        imagename1 = response.xpath('//*[@id="hxName"]/text()').extract()
        imagename2 = response.xpath('//*[@id="jushi"]/text()').extract()
        print("image", imagename1,imagename2,src)

        if imagename1 != [] and imagename2 != []:
            item['imgname'] = imagename1[0] + '_' + imagename2[0]+'.jpg'
        if src != []:
            item['imgurl'] = src[0]

        print("item",item)

        yield item

    def parse_housedetail(self, response):
        print("debug06")
        item = BuildingdetailItem()
        html = response.body.decode('gb18030')

        # filename="test.html"
        # with open(str(filename), "wb+") as f:
        #     f.write(response.body)
            # href = response.xpath('//div[@id="orginalNaviBox"]/*[@id="xfptxq_B03_16"]/@href').extract()
        doc = pq(html)
        set = []
        value = []
        basc = {}

        line1r = doc('div.main-left > div:nth-child(1) > ul > li:nth-child(2) > div.list-right > span')
        basc["项目特色"] = line1r.text()

        val = doc(' ul>li div.list-right-text')  # div.list-right-text
        for li in val.items():
            value.append(li.text())
        basc["开发商"] = value[0]
        basc["楼盘地址"] = value[1]
        print("value", value, len(value), value[0])

        value.clear()
        val = doc('.main-item table> tr:nth-child(2)> td:nth-child(2) ')
        for li in val.items():
            print("val", li.text())
            value.append(li.text())
        if value != []:
            basc["预售许可证"] = value[0]
            print("value", value, len(value), value[0])

        set.clear()
        value.clear()
        line2l = doc(".main-item ul>li  div.list-left")  # doc('.main-item ul.list div.list-left')
        # print('line1l',line1l,type(line1l))
        for li in line2l.items():
            print("line2l", li.text())
            set.append(li.text())
        print('/n/....................')

        line2r = doc('.main-item   ul>li div.list-right')  # doc('.main-item ul.list div.list-left')
        # print('test02',line1l,type(line1l))
        for li in line2r.items():
            value.append(li.text())
        print("lenth", len(set), len(value))

        num = len(set)

        if set != [] and value != []:
            basc[set[0][0:-1]] = value[0]
            for i in range(2, 6):
                basc[set[i][0:-1]] = value[i]
            for i in range(8, 13):
                basc[set[i][0:-1]] = value[i - 2]
            for i in range(16, 25):
                basc[set[i][0:-1]] = value[i - 4]

        text = doc('.main-item  p.intro')  # doc('.main-item ul.list div.list-left')
        # print('text', text.text())
        basc["项目简介"] = text.text()

        print(basc, len(basc))
        item['basicinfo'] = basc

        city = doc('.header_mnav>p > a:nth-child(2)')
        item['city'] = city.text()[0:-2]
        area = doc('.header_mnav>p > a:nth-child(3)')
        item['area'] = area.text()[0:-2]
        building = doc('.header_mnav>p > a:nth-child(4)')
        item['building'] = building.text()
        link = doc('.header_mnav>p > a:nth-child(4)').attr('href')
        item['link'] = link
        print("city.text()",item)

        yield item






