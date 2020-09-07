# coding=utf-8
import csv
import json
import os
import datetime
import time

from selenium.webdriver import Chrome
from services import GoogleSearchBuilder

driver = Chrome()

inputFile = os.path.join('./demo/', 'input.json')

search_terms = []
with open(inputFile) as json_file:
  search_terms = json.load(json_file)

for search in search_terms:
  builder = GoogleSearchBuilder(search)
  search_url = builder.get_url()
  material_links = []
  page = 1

  while search_url and page <= 2:
    time.sleep(5)
    driver.get(search_url)
    results = driver.find_elements_by_class_name('g')

    try:
      next_page = driver.find_element_by_id('pnnext')
    except:
      next_page = None

    for result in results:
      material_links.append({
        'title': result.find_element_by_tag_name('h3').text,
        'link': result.find_element_by_class_name('r').find_element_by_tag_name('a').get_attribute('href'),
      })

    search_url = next_page.get_attribute('href') if next_page else None

    if search_url is not None:
      page += 1

  # for material in material_links:
  #   driver.get(material['link'])
  #   material['link'] = driver.current_url

  output_filename = 'result-{}.json'.format(search)

  file_path = os.path.join('./demo/', output_filename)

  with open(file_path, 'a', encoding="utf-8") as output:
    json.dump(material_links, output, ensure_ascii=False)

  # file_name = "{}.csv".format(search['sheet_title'])

  # file_path = os.path.join(directory, file_name)

  # with open(file_path, 'a', newline='') as output:
  #   writer = csv.writer(output)
  #   writer.writerow([
  #     u'日期',
  #     u'標題',
  #     u'連結'
  #   ])
  #   for news in news_list:
  #     writer.writerow([
  #       news['time'],
  #       news['title'],
  #       news['link']
  #     ])

driver.close()
