# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 21:04:11 2019
e.g: http://data.eastmoney.com/bbsj/201806/lrb.html
获取东方财富配股数据和增发数据
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
def get_table(date, category_type,st,sr,sty,page):
    # 参数设置
    params = {
        # 'type': 'CWBB_LRB',
        'type': category_type,  # 表格类型,LRB为利润表缩写，必须
        'sty': sty,
        'st': st,   # 公告日期
        'sr': sr,   # 保持-1不用改动即可
        'p': page,  # 表格页数
        'ps': 50,   # 每页显示多少条信息
        'js': 'var LFtlXDqn={pages:(pc),data: [(x)]}',  # js函数，必须
        'stat':0,
        # 'rt': 51294261  可不用
    }
    #配股数据的请求网址
    #    http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?type=NS&sty=NSA&st=6&
    #           sr=-1&p=2&ps=50&js=var%20OVJfgZFA={pages:(pc),data:[(x)]}&rt=52236304
    #增发数据的请求网址
    #    http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?type=SR&sty=ZF&st=5&
    #           sr=-1&p=2&ps=50&js=var%20mxLwTGaH={pages:(pc),data:[(x)]}&stat=0&rt=52236182
    url = 'http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?'

    # print(url)
    response = requests.get(url, params=params).text
    #print(response)
    # 确定页数
    pat = re.compile('var.*?{pages:(\d+),data:.*?')
    page_all = re.search(pat, response)
    print(page_all.group(1))  # ok

    # 提取{},json.loads出错
    # pattern = re.compile('var.*?data: \[(.*)]}', re.S)

    # 提取出list，可以使用json.dumps和json.loads
    pattern = re.compile('var.*?data:(.*)}', re.S)
    items = re.search(pattern, response)
    # 等价于
    # items = re.findall(pattern,response)
    # print(items[0])
    data = items.group(1)
    data = json.loads(data)
    # data = json.dumps(data,ensure_ascii=False)

    return page_all, data,page

# 写入表头
# 方法1 借助csv包，最常用
def write_header(data,category):
    with open('{}.csv' .format(category), 'a', encoding='utf_8_sig', newline='') as f:
        if category == '增发数据':    #增发
            headers = list(['股票代码', '股票简称', '发行数量', '发行价格', '最新价格', '发行日期',
                            '待分类1', '待分类2', '待分类3', '待分类4', '待分类5', '待分类6', '待分类7',
                            '待分类8', '待分类9'])
        elif  category == '配股数据':
            headers = list(['待分类1', '待分类2', '股票代码', '股票简称', '配售代码', '配售简称', '配股比例',
                            '配股价格', '配股前总股本', '实际配售数量', '配股后总股本', '股权登记日', '配股缴款起始日',
                            '配股缴款截止日', '上市日', '除权基准日', '实际募资总额', '实际募资净额', '承销方式',
                            '配股详细资料日', '最新价格', '待分类3'])
        # print(headers)  # 测试 ok
        writer = csv.writer(f)
        writer.writerow(headers)

def write_table(data,page,category):
    print('\n正在下载第 %s 页表格' % page)
    for d in data:
        with open('{}.csv' .format(category), 'a', encoding='utf_8_sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(d.split(','))

def main(date, category_type,st,sr,sty,page):
    func = get_table(date, category_type,st,sr,sty,page)
    data = func[1]
    page = func[2]
    write_table(data,page,category)


if __name__ == '__main__':
    # 获取总页数，确定起始爬取页数
    for i in set_table():
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

    # 写入表头
    write_header(constant[1],category)
    start_time = time.time()  # 下载开始时间
    # 爬取表格主程序
    for page in range(start_page, end_page+1):
        main(date,category_type,st,sr,sty, page)

    end_time = time.time() - start_time  # 结束时间
    print('下载完成')
    print('下载用时: {:.1f} s' .format(end_time))