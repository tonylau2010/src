from bs4 import BeautifulSoup
import requests
import re
from requests.exceptions import RequestException
from pymongo import MongoClient
import time
import random

def get_one_page(page, ip_list):
    url = "https://shenzhen.qfang.com/sale/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
        'Host': 'shenzhen.qfang.com',
        'Referer': 'https://www.qfang.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    newUrl = url + 'f' + str(page)
    proxy_ip = random.choice(ip_list)
    ip = {'https:':proxy_ip} # proxy ip needed for requests
    try:
        response = requests.get(newUrl, headers=headers, proxies=ip)
    except RequestException as e:
            print("error: " + response.status_code)

    soup = BeautifulSoup(response.text, 'html.parser')
    #  需要抓取： 小区名称， 面积大小， 均价， 以及详细信息的链接
    price_list = []
    for item in soup.select('div .show-price'):
        average_price = item.select('p')[0].text
        price_list.append(average_price)

    index = 0;
    result2 = []
    for item in soup.select('div .show-detail'):
        detailed_url = 'https://shenzhen.qfang.com/sale' + item.select('a')[0].get('href')
        # 在爬取面积的过程中，发现有数据缺失，原因为，有的存在第4个span tag中，有的存在第5个span tag中，所以先都取出来，然后用正则筛选
        regax = re.compile('(.*?)平米')
        result = item.select('span')[3].text + item.select('span')[4].text
        area = re.findall('(\d+(\.\d+)?)',re.findall(regax, result)[0])[0][0]
        community_name = (item.find_all(target = '_blank')[0].text).split(' ')[0]
        average_price = re.findall('(\d+(\.\d+)?)',price_list[index])[0][0]
        index += 1
        print("%s\t%s\t%s\t%s" % (community_name, area, average_price, detailed_url))
        result2.append({'小区名称': community_name, '住房面积(平方米)': area, '平均价格(每平方)': average_price, '详细信息链接': detailed_url})
    return result2


def read_ip():
    result = []
    with open('ip.txt', 'r', encoding='gb18030', newline='') as f:
        for line in f:
            result.append('http://'+line)
        return result

def store_in_db(result):
    conn = MongoClient('localhost', 27017)
    db = conn.test  # db name is test
    my_set = db.text_set  # set type
    my_set.insert(result)


def getdata(page, ip_list):
    for i in range(page):
        result = get_one_page(i, ip_list)
        store_in_db(result)
        print('data storgae from page '+str(i)+'complete!')
        if i >= 10 and i % 10 == 0:
            time.sleep(30)


def main(page):
    ip_list = read_ip()  # 读取文档中的ip
    getdata(page, ip_list)


if __name__ == '__main__':
    main(100)