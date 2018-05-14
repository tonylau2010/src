from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException
from pymongo import MongoClient
import time
import random


def get_one_page(page, ip_list):
    url = "https://sz.lianjia.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Host': 'sz.lianjia.com',
        'Referer': 'https://www.lianjia.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    newUrl = url + 'ershoufang/' + 'pg' + str(page)

    proxy_ip = random.choice(ip_list)
    ip = {'https:':proxy_ip} # proxy ip needed for requests
    try:
        response = requests.get(newUrl, headers=headers, proxies=ip)
    except RequestException as e:
        print("error: " + response.status_code)

    soup = BeautifulSoup(response.text, 'html.parser')

    #  需要抓取： 小区名称， 面积大小， 均价， 以及详细信息的链接
    result = []
    for item in soup.select('li .clear'):
        detailed_info = item.select('div .houseInfo')[0].text
        community_name = detailed_info.split('|')[0].strip()
        area = detailed_info.split('|')[2].strip()
        average_price = item.select('div .unitPrice span')[0].text
        detailed_url = item.select('a')[0].get('href')
        # print("%s\t%s\t%s\t%s"%(community_name, area, average_price, detailed_url))
        result.append({'community_name':community_name, 'area':area, 'average_price':average_price, 'detailed_url':detailed_url})
    return result


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
            time.sleep(100)


def main(page):
    ip_list = read_ip() #读取文档中的ip
    getdata(page, ip_list)



if __name__ == '__main__':
    main(100)
