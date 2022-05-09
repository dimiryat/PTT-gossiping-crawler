# -*- coding: utf-8 -*-
"""
Created on Mon May  9 10:49:21 2022

@author: DennisLin
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import re

PTT_URL = 'https://www.ptt.cc'

def get_web_page(url):
    resp = requests.get(url=url, cookies={'over18':'1'})
    if resp.status_code != 200:
        print("Invalid url : ", resp.url)
        return None
    else:
        return resp.text

def get_articles(dom, date):
    soup = BeautifulSoup(dom, 'html5lib')
    
    paging_div = soup.find('div', 'btn-group btn-group-paging')
    prev_url = paging_div.find_all('a')[1]['href']
    articles = []
    
    divs = soup.find_all('div', 'r-ent')
    for d in divs:
        if d.find('div', 'date').text.strip() == date:
            push_count = 0
            push_str = d.find('div', 'nrec').text
            if push_str:
                try:
                    push_count = int(push_str)
                except ValueError:
                    if push_str == '爆':
                        push_count = 99
                    elif push_str.startswith('X'):
                        push_count = -10
            if d.find('a'):
                href = d.find('a')['href']
                title = d.find('a').text
                #author = d.find('div', 'author').text if d.find('div', 'author') else ''
                if d.find('div', 'author'):
                    author = d.find('div', 'author').text
                else:
                    author = ''
                articles.append({
                    'title':title,
                    'href':href,
                    'push_count':push_count,
                    'author':author
                    })
    return articles, prev_url
    
if __name__=="__main__":
    threshold = 99
    target_string = ""
    current_page = get_web_page(PTT_URL + '/bbs/Gossiping/index.html')
    if current_page:
        articles = []
        today = time.strftime("%m/%d").lstrip('0')
        current_articles, prev_url = get_articles(current_page, today)
        while current_articles:
            articles += current_articles
            current_page = get_web_page(PTT_URL + prev_url)
            current_articles, prev_url = get_articles(current_page, today)
    
    print("今天有", len(articles), "篇文章")
    print("熱門文章(> %d 推)" % threshold)
    for a in articles:
        if int(a['push_count']) >= threshold:
            if target_string:
                if target_string in a['title']:
                    print(a)
            else:
                print(a)
    with open('gossiping.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, sort_keys=True, ensure_ascii=False)