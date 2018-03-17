# -*- coding: utf-8 -*-
# @Time    : 2018/3/8 10:08
# @Author  : famu
# @File    : url.py
# @Software: PyCharm

import urllib
import urllib.request
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

def GetUrl(area=None, sale=None, type=None, size=None, deco=None, min_money=0, max_money=5000):
        """
        :param area:    区域：罗湖，福田，南山，盐田，宝安，龙岗
        :param sale:    租房：整租，合租
        :param type:    来源：个人房源，经纪人，品牌公寓
        :param size:    大小：一室，二室，三室，四室，四室以上
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
        if area:
            base_url += area_dct.get(area, "") + "/"

        sale_dct = {
                "合租"    : "hezu",
                "整租"    : "zufang",
        }
        if sale:
            base_url += sale_dct.get(sale, "chuzu") + "/"
        type_dct = {
                "个人房源"	: "0",
                "经纪人"	    : "1",
                "品牌公寓"	: "2",
        }
        if type:
            base_url += type_dct.get(type, "") + "/"
        decoration_dct = {
                "毛坯"		: "f1",
                "简单装修"	: "f2",
                "中等装修"	: "f3",
                "精装修"		: "f4",
                "豪华装修"	: "f5",
        }
        base_url += decoration_dct.get(deco, "")
        size_dct = {
                "一室"		: "j1",
                "二室"		: "j2",
                "三室"		: "j3",
                "四室"		: "j4",
                "四室以上"	: "j5",
        }
        base_url += size_dct.get(size, "") + "/"
        base_url += "?minprice=%d_%d"%(min_money, max_money)

        return base_url


def GetHtml(url):
        fname = "html/" + str(base64.b64encode(url.encode('utf-8')), "utf-8").replace("/", "") + ".html"
        if os.path.isfile(fname):
                with open(fname, "r", encoding="utf-8") as f:
                        return f.read()
        else:
                request = urllib.request.Request(url)
                response = urllib.request.urlopen(request)
                content = response.read().decode('utf-8')
                SaveFile(fname, content)
                return content

def SaveFile(fname, fcontent):
        with open(fname, "w", encoding="utf-8") as f:
                f.write(fcontent)


def AnalyzeHtml(content):
        html_data = re.search(HOUSE_LIST_RE, content, re.S)
        if html_data == None:
                return None, None

        house_list = html_data.group("list")

        data_list = []

        item_list = re.finditer(FIND_ITEM_RE, house_list, re.S)

        for item in item_list:
                tid = item.group("tid")
                url, picNum, desc, room, geren, add, sendTime, money = "", "", "", "", "", "", "", "",
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
        baseUrl = GetUrl(area="福田", sale="整租", type="经纪人", size="一室", deco=None, min_money=1400, max_money=2600)
        fname = str(base64.b64encode(baseUrl.encode('utf-8')), "utf-8").replace("/", "") + ".csv"

        with open(fname, "w") as f:
                f.write(StringHouse(HOUSE_TITLE))

        url = baseUrl
        for i in range(100):
                content = GetHtml(url)
                url, house_list = AnalyzeHtml(content)
                print(i, url)
                with open(fname, "a") as f:
                        for house in house_list[1:]:
                                f.write(StringHouse(house))
                if url == None:
                        break

        print("end")
