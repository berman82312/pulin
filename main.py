# coding=utf-8
import csv
import json
import os
import datetime

from selenium.webdriver import Chrome
from services import BaiduSearchBuilder, GoogleSearchBuilder, TimeRange, Site

driver = Chrome()
driver.implicitly_wait(10)
driver.get('http://www.baidu.com/s?wd=%E5%B0%BC%E6%B3%8A%E5%B0%94%20%E6%92%A4%E4%BE%A8%20site%3Ahuanqiu.com&oq=%E5%B0%BC%E6%B3%8A%E5%B0%94%20%E6%92%A4%E4%BE%A8%20site%3Ahuanqiu.com&ie=utf-8&gpc=stf%3D1425168000%2C1433030400%7Cstftype%3D2')

directory = './result-{}/'.format(datetime.datetime.now().strftime('%Y-%m-%d'))
os.mkdir(directory)

search_terms = []
with open('search.json') as json_file:
  search_terms = json.load(json_file)

for search in search_terms:
  data = {
    'keyword': "{} site:{}".format(search['keyword'], Site.HUANQIU),
    'time_range': TimeRange.CUSTOM,
    'start_at': search['start_at'],
    'end_at': search['end_at']
  }
  build = BaiduSearchBuilder.from_data(data)
  search_url = build.get_url()
  news_list = []

  while search_url:
    driver.get(search_url)
    results = driver.find_elements_by_class_name('result')

    try:
      next_page = driver.find_element_by_partial_link_text(u'下一页')
    except:
      next_page = None

    for result in results:
      news_list.append({
        'title': result.find_element_by_tag_name('h3').text,
        'link': result.find_element_by_tag_name('h3').find_element_by_tag_name('a').get_attribute('href'),
        'time': result.find_element_by_class_name('newTimeFactor_before_abs').text
      })

    search_url = next_page.get_attribute('href') if next_page else None

  for news in news_list:
    driver.get(news['link'])
    news['link'] = driver.current_url

  file_name = "{}.csv".format(search['sheet_title'])

  file_path = os.path.join(directory, file_name)

  with open(file_path, 'a', newline='') as output:
    writer = csv.writer(output)
    writer.writerow([
      u'日期',
      u'標題',
      u'連結'
    ])
    for news in news_list:
      writer.writerow([
        news['time'],
        news['title'],
        news['link']
      ])

driver.close()
