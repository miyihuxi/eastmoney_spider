# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 21:04:11 2019
e.g: http://data.eastmoney.com/bbsj/201806/lrb.html
获取东方财富个股盈利预测数据
"""

import requests
import re
from multiprocessing import Pool
import json
import csv
import pandas as pd
import os
import time

# 设置文件保存在D盘eastmoney文件夹下
file_path = 'D:\\eastmoney'
if not os.path.exists(file_path):
    os.mkdir(file_path)
os.chdir(file_path)



# 1 设置表格爬取时期
def set_table():
    print('*' * 80)
    print('\t\t\t\t东方财富网报表下载')
    print('作者：高级农民工  2018.10.10')
    print('--------------')

    # 2 设置财务报表种类
    tables = int(
        input("请输入查询的报表种类对应的数字(1-增发数据；2-配股数据): \n"))

    dict_tables = {1: '增发数据', 2: '配股数据'}

    dict = {1: 'SR', 2: 'NS'}

    # js请求参数里的type，第1-4个表的前缀是'YJBB20_'，后3个表是'CWBB_'
    # 设置set_table()中的type、st、sr、filter参数
    if tables == 2:
        category_type = dict[tables]
        sty = 'NSA'
        st = 6
        sr = -1
    elif tables == 1:
        category_type = dict[tables]
        sty = 'ZF'
        st = 5
        sr = -1


    yield{
    'category':dict_tables[tables],
    'category_type':category_type,
    'sty':sty,
    'st':st,
    'sr':sr
    }

# 2 设置表格爬取起始页数
def page_choose(page_all):

    # 选择爬取页数范围
    start_page = input('请输入下载起始页数：\n')
    # 判断输入的是数值还是回车空格
    if start_page.isdigit():
        #如果是数值，取整数
        start_page = int(start_page)
    elif start_page == '':
        #如果是空，设为默认值12018
        start_page = int(1)

    nums = input('请输入要下载的页数，（若需下载全部则按回车）：\n')
    print('*' * 80)

    # 判断输入的是数值还是回车空格
    if nums.isdigit():
        end_page = start_page + int(nums)
    elif nums == '':
        end_page = int(page_all.group(1))
    else:
        print('页数输入错误')

    # 返回所需的起始页数，供后续程序调用
    yield{
        'start_page': start_page,
        'end_page': end_page
    }

# 3 表格正式爬取
def get_table(code):
    # 参数设置
    params = {
        'code': code,  # 股票代码格式为如：SZ000423
    }

    #个股盈利预测数据的请求网址
    #    http://f10.eastmoney.com/ProfitForecast/ProfitForecastAjax?code=SZ000423
    url = 'http://f10.eastmoney.com/ProfitForecast/ProfitForecastAjax?'

    # print(url)
    response = requests.get(url, params=params).text
    #print(response)

    data = json.loads(response)
    # data = json.dumps(data,ensure_ascii=False)

    return data['jgyc']['data'][0]

# 写入表头
# 方法1 借助csv包，最常用
def write_header(category):
    with open('{}.csv' .format(category), 'a', encoding='utf_8_sig', newline='') as f:
        headers = list(['jgmc', 'sy', 'syl', 'sy1', 'syl1', 'sy2', 'syl2', 'sy3', 'syl3', 'code'])
        writer = csv.writer(f)
        writer.writerow(headers)

def write_table(data,category):
        with open('{}.csv' .format(category), 'a', encoding='utf_8_sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(data)

def main(category, code):
    func = get_table(code)
    print(func)
    data = list(func.values())
    data.append(code)
    write_table(data,category)


if __name__ == '__main__':
    # 获取总页数，确定起始爬取页数
    '''for i in set_table():
        date = i.get('date')
        category = i.get('category')
        category_type = i.get('category_type')
        st = i.get('st')
        sr = i.get('sr')
        sty = i.get('sty')

    constant = get_table(date,category_type,st,sr,sty, 1)
    page_all = constant[0]

    for i in page_choose(page_all):
        start_page = i.get('start_page')
        end_page = i.get('end_page')
'''
    category = '机构预测盈利'
    code = 'SZ000423'
    # 写入表头
    write_header(category)
    start_time = time.time()  # 下载开始时间
    # 爬取表格主程序
    main(category, code)

    end_time = time.time() - start_time  # 结束时间
    print('下载完成')
    print('下载用时: {:.1f} s' .format(end_time))