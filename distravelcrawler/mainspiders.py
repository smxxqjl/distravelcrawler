# -*- coding: utf-8 -*-
import json
import os
from os.path import exists
import requests
import re
import urllib
import json
import urllib2

from scrapy_redis.spiders import RedisSpider

if not exists('trip_data'):
    os.mkdir('trip_data')


class MySpider(RedisSpider):
    name = 'mainspider_redis'
    redis_key = 'disspider:start_urls'

    def new_parser(self, response):
        print '--------------------ctrip here----------------'
        place = re.findall('<title>(.*?)旅游', response.body)[0]
        travel_list = response.xpath('//div[@class="product_sublist flag_product flag_schedule  "]')

        for travel in travel_list:
            package_name = travel.xpath("div//a[@class='small_title']/text()").extract()[0]
            money = travel.xpath("div//strong/text()").extract()[0]
            json_string = ''
            for json_part in travel.xpath('./textarea/text()'):
                json_string = json_string + json_part.extract()
            ctrip_json = json.loads(json_string)
            data = {
                'destination': place,
                'go_way': '',
                'price': money,
                'hotel': '',
                'interests': ctrip_json['PackageName'],
                'data_start': '',
                'data_end': '',
                'comment': ctrip_json['Score'],
                'website': 'ctrip'
            }
        print 'waefwehaofeaw' + len(response.xpath('//a[@class="down "]'))
        if len(response.xpath('//a[@class="down "]')) == 1:
            sel = response.xpath('//a[@class="down "]')
            url = sel.xpath("@href").extract()[0]
            url = response.urljoin(url)
            print url + 'is to crawled'
            yield scrapy.Request(url, callback=self.new_ctrip_parser)

    def ctrip_parser(self, response):
        print 'ctrip here'
        content = response.body.decode('gbk').encode('utf-8')
        place = re.findall('<title>(.*?)旅游', content)[0]
        writefile = open('trip_data/' + place, 'w')
        travel_plans_json = re.findall('({"Key".*?"RecTagIDs":""})', content)
        travel_plans_dict_list = []
        print 'ctrip' + place

        for plan_json in travel_plans_json:
            travel_plans_dict_list.append(json.loads(plan_json))

        for plan_dict in travel_plans_dict_list:
            des_url = str(plan_dict['Url'])
            if des_url[0] == '/':
                des_url = 'http://vacations.ctrip.com/around/' + des_url.split('/')[2]
            # print str(urllib2.urlopen(des_url).read().decode('gbk').encode('utf8'))
            if 'freetravel' not in des_url:
                package_list = re.findall('<title>(.*?)</title>'.encode('utf-8'),
                                          str(urllib2.urlopen(des_url, timeout=3).read().decode('gbk').encode(
                                              'utf8')))
            else:
                package_list = re.findall('<title>(.*?)</title>'.encode('utf-8'),
                                          str(urllib2.urlopen(des_url, timeout=3).read().decode('utf-8').encode(
                                              'utf8')))
            package_name = package_list[0]
            data = {
                'destination': place,
                'go_way': '',
                'price': plan_dict['MinPrice'],
                'hotel': '',
                'interests': '',
                'data_start': '',
                'data_end': '',
                'comment': plan_dict['CommentText'],
                'website': 'ctrip'
            }
            data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            writefile.write(data + '\n')

    def qunar_parser(self, response):
        url = response.url
        place = re.findall('&fhLimit=0%2C20&q=(.*?)&d=', url)[0]
        place = urllib.unquote(place).decode('utf-8')
        print place + 'the url is' + url
        mainjson = requests.get(response.url).json()
        groupcount = mainjson['data']['limit']['groupCount']
        writefile = open('trip_data/' + place, 'w')
        page = 0
        count = 1
        while page < groupcount:
            temp_re = requests.get(url)
            mainjson = temp_re.json()
            maindata = mainjson['data']['list']['results']
            for littlejson in maindata:
                hotelinfo = ''
                interests = ''
                traffic = ''
                for subhotel in littlejson['hotelInfo']:
                    hotelinfo = hotelinfo + '+' + subhotel['name']
                for subinterest in littlejson['sights']:
                    interests = interests + '+' + subinterest
                for subtraffic in littlejson['summary']['traffic']:
                    traffic = traffic + subtraffic
                data = {
                    'destination': place,
                    'title': littlejson['title'],
                    'go_way': traffic,
                    'price': littlejson['price'],
                    'hotel': hotelinfo,
                    'interests': interests,
                    'data_start': '',
                    'data_end': '',
                    'comment': '',
                    'website': 'qunar'
                }
                data = json.dumps(data, ensure_ascii=False).encode('utf-8')
                writefile.write(data + '\n')
            url = url.replace('lm=' + str(page * 20) + '%2C20', 'lm=' + str((page + 1) * 20) + '%2C20')
            page = page + 1
            count = count + 1

    def parse(self, response):
        if 'dujia.qunar.com' in response.url:
            print 'ignore'
            #self.qunar_parser(response)
        elif 'ctrip.com' in response.url:
            self.ctrip_parser(response)
        else:
            print 'unknown type of url'
