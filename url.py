# -*- coding: utf-8 -*-
# @Time    : 2018/3/8 10:08
# @Author  : famu
# @File    : url.py
# @Software: PyCharm

import urllib
import urllib2
import re
import base64
import os

SUB_RE         = "<.*?>"

HOUSE_LIST_RE   = "<ul class=\"listUl\">(?P<list>.*?)<li id=\"bottom_ad_li\">.*?(<a class=\"next\" href=\"(?P<next_url>.*?)\">.*?)?</li>.*?</ul>"
FIND_ITEM_RE    = "<li logr=\"(?P<tid>.*?)\".*?sortid=.*?>(?P<data>.*?)</li>"
IMG_LIST_RE     = "<div class=\"img_list\">.*?<a href=\"(?P<url>.*?)\".*?</a>.*?<span class=\"picNum\">(?P<picNum>.*?)</span>.*?</div>"
DES_RE          = "<div class=\"des\">.*?<h2>.*?<a .*?>(?P<desc>.*?)</a>.*?</h2>.*?<p class=\"room\">(?P<room>.*?)</p>.*?<p class=\"add\">(?P<add>.*?)</p>.*?<p class=\"geren\">(?P<geren>.*?)</p>.*?</div>"
LISTLIRIGHT_RE  = "<div class=\"listliright\">.*?<div class=\"sendTime\">(?P<sendTime>.*?)</div>.*?<div class=\"money\">(?P<money>.*?)</div>.*?</div>"

HOUSE_TITLE     = ("tid", "url", "picNum", "desc", "room", "geren", "add", "sendTime", "money")

def GetUrl(type=None, area=None, size=None, sale=None, deco=None):
        """
        :param type:    来源：个人房源，经纪人，品牌公寓
        :param area:    区域：罗湖，福田，南山，盐田，宝安，龙岗
        :param size:    大小：一室，二室，三室，四室，四室以上
        :param sale:    租房：整租，合租
        :param deco:    装修：毛坯，简单装修，中等装修，精装修，豪华装修
        :return: url地址
        """

        base_url = "http://sz.58.com/"
        area_dct = {
                "罗湖"		: "luohu",
                "福田"		: "futian",
                "南山"		: "nanshan",
                "盐田"		: "yantian",
                "宝安"		: "baoan",
                "龙岗"		: "longgang",
                "布吉"		: "buji",
                "坪山新区" 	: "pingshanxinqu",
                "光明新区"	: "guangmingxinqu",
                "龙华新区"	: "szlhxq",
                "大鹏新区"	: "dapengxq",
                "深圳周边"	: "shenzhenzhoubian",
        }
        size_dct = {
                "一室"		: "j1",
                "二室"		: "j2",
                "三室"		: "j3",
                "四室"		: "j4",
                "四室以上"	: "j5",
        }
        sale_dct = {
                "合租"    : "hezu",
                "整租"    : "zufang",
        }
        decoration_dct = {
                "毛坯"		: "f1",
                "简单装修"	: "f2",
                "中等装修"	: "f3",
                "精装修"		: "f4",
                "豪华装修"	: "f5",
        }
        type_dct = {
                "个人房源"	: "0",
                "经纪人"	        : "1",
                "品牌公寓"	: "2",
        }
        return "http://sz.58.com/chuzu/0/"


def GetHtml(url):
        fname = base64.b64encode(url) + ".html"
        if os.path.isfile(fname):
                with open(fname, "r") as f:
                        return f.read()
        else:
                request = urllib2.Request(url)
                response = urllib2.urlopen(request)
                content = response.read()
                SaveFile(fname, content)
                return content

def SaveFile(fname, fcontent):
        with open(fname, "w") as f:
                f.write(fcontent)


def AnalyzeHtml(content):
        html_data = re.search(HOUSE_LIST_RE, content, re.S)
        if html_data == None:
                return

        house_list = html_data.group("list")

        data_list = []

        item_list = re.finditer(FIND_ITEM_RE, house_list, re.S)

        for item in item_list:
                tid = item.group("tid")
                url, picNum, desc, room, geren, add, sendTime, money = None, None, None, None, None, None, None, None,
                item_data = item.group("data").replace("&nbsp;", "").replace(",", "，")
                img_list = re.search(IMG_LIST_RE, item_data, re.S)
                if img_list:
                        url = img_list.group("url")
                        picNum = img_list.group("picNum")

                desc_list = re.search(DES_RE, item_data, re.S)
                if desc_list:
                        desc = desc_list.group("desc")
                        room = desc_list.group("room")
                        geren = desc_list.group("geren")
                        add = desc_list.group("add")

                listlirgith_list = re.search(LISTLIRIGHT_RE, item_data, re.S)
                if listlirgith_list:
                        sendTime = listlirgith_list.group("sendTime")
                        money = listlirgith_list.group("money")


                data_list.append((tid, url, picNum, desc, room, geren, add, sendTime, money))

        try:
                next_url = html_data.group("next_url")
        except:
                next_url = ""

        return next_url, data_list


def StringHouse(house):
        return re.sub("[\t\s\n\r]", "", re.sub(SUB_RE, "",",".join(house), flags=re.S), flags=re.S) + "\n"


if __name__ == "__main__":
        baseUrl = GetUrl("个人房源", "福田", "一室", "整租")
        fname = base64.b64encode(baseUrl) + ".csv"

        with open(fname, "w") as f:
                f.write(StringHouse(HOUSE_TITLE))

        url = baseUrl
        for i in xrange(20):
                content = GetHtml(url)
                url, house_list = AnalyzeHtml(content)

                with open(fname, "a") as f:
                        for house in house_list[1:]:
                                try:
                                        f.write(StringHouse(house))
                                except:
                                        print house
                                        url = None
                                        break
                if url == None:
                        break

        print "end"
