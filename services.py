# -*- coding: utf-8 -*-
import urllib.request, urllib.parse
# import urllib2
import logging
import time
from bs4 import BeautifulSoup
from datetime import datetime

URL_PREFIX = u'http://www.google.com.tw/search?'

BAIDU_PREFIX = u'http://www.baidu.com/s?'

def get_soup_from_link(link):
    """ Get the beautiful soup parsed content from link """
    # link = urllib.parse.unquote(link)
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    req = urllib.request.Request(link, headers=hdr)
    res = urllib.request.urlopen(req)
    html = res.read()
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def get_final_url(link):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    req = urllib.request.Request(link, headers=hdr)
    res = urllib.request.urlopen(req)
    return res.geturl()

class TimeRange(object):
    """Time Range
    Time range for searching result
    """
    HOUR = 'h'
    DAY = 'd'
    WEEK = 'w'
    MONTH = 'm'
    YEAR = 'y'
    CUSTOM = 'cdr'

class SearchGenre(object):
    """Search Genre
    Searching for image, video or news
    """
    NEWS = 'nws'

class Site(object):
    HUANQIU = 'huanqiu.com'
    GUANCHA = 'guancha.cn'

class BaiduSearchBuilder(object):
    def __init__(self, keyword):
        self.keyword = keyword
        self.genre = SearchGenre.NEWS
        self.pagination = 0
        self.time_range = TimeRange.DAY
        self.sort_by_date = True
        self.show_duplicated = True

    @classmethod
    def from_data(cls, data):
        if 'keyword' not in data:
            raise Exception('No keyword specified')
        if 'time_range' not in data:
            raise Exception('No time_range specified')
        result = cls(data['keyword'])
        if data['time_range'] == TimeRange.CUSTOM:
            start_from = datetime.strptime(data['start_at'], '%Y-%m-%d')
            end_at = datetime.strptime(data['end_at'], '%Y-%m-%d')
            result.set_time_range(data['time_range'], start_from, end_at)
        else:
            result.set_time_range(data['time_range'])
        if 'pagination' in data:
            result.set_pagination(int(data['pagination']))
        print(result.get_url())
        return result

    def set_time_range(self, time_range, start_from=None, end_at=None):
        if time_range == TimeRange.CUSTOM:
            self.time_range = TimeRange.CUSTOM
            self.start_from = start_from.timestamp()
            self.end_at = end_at.timestamp()
        else:
            self.time_range = time_range
        return self

    def set_pagination(self, start):
        self.pagination = start
        return self

    def get_url(self):
        data = {
            'wd': urllib.parse.quote(self.keyword),
            'oq': urllib.parse.quote(self.keyword),
            'ie': 'utf-8',
            'gpc': urllib.parse.quote('stf={:.0f},{:.0f}|stftype=2'.format(self.start_from, self.end_at)),
        }
        if self.pagination > 0:
            data['pn'] = self.pagination
        link = BAIDU_PREFIX + urllib.parse.urlencode(data)
        return urllib.parse.unquote(link)

    def get_news_links(self, page=1):
        """ Get the news link from the search result
        We make a request to the google search, and parse the response html page
        """
        pagination = 10 * (page - 1)
        result = []
        self.set_pagination(pagination)
        soup = get_soup_from_link(self.get_url())
        more_result = False
        if not soup.select('div.result'):
            if u'百度安全验证' in soup.title.text:
                logging.warning('Block by Baidu!')
            return result, more_result
        else:
            for news_card in soup.select('div.result'):
                link = news_card.a['href']
                link = get_final_url(link)
                # if 'cardu.com' in link:
                #     continue
                title = news_card.a.text
                posted_at = news_card.find('span', class_='newTimeFactor_before_abs').text
                result.append({
                    'link': link,
                    'title': title,
                    'posted_at': posted_at
                })
                if news_card.find(class_='card-section'):
                    for card in news_card.find_all(class_='card-section'):
                        title = card.a.text
                        link = card.a['href']
                        result.append({
                            'link': link,
                            'title': title
                        })
            if soup.select('a#pnnext'):
                more_result = True
        return result, more_result


class GoogleSearchBuilder(object):
    """ Google Search Builder
    Construct the search url
    """

    def __init__(self, keyword):
        self.keyword = keyword
        self.genre = SearchGenre.NEWS
        self.pagination = 0
        self.time_range = None
        self.sort_by_date = True
        self.show_duplicated = True

    @classmethod
    def from_data(cls, data):
        if 'keyword' not in data:
            raise Exception('No keyword specified')
        if 'time_range' not in data:
            raise Exception('No time_range specified')
        result = cls(data['keyword'])
        if data['time_range'] == TimeRange.CUSTOM:
            start_from = datetime.strptime(data['start_at'], '%Y-%m-%d')
            end_at = datetime.strptime(data['end_at'], '%Y-%m-%d')
            result.set_time_range(data['time_range'], start_from, end_at)
        else:
            result.set_time_range(data['time_range'])
        if 'pagination' in data:
            result.set_pagination(int(data['pagination']))
        print(result.get_url())
        return result

    def set_time_range(self, time_range, start_from=None, end_at=None):
        if time_range == TimeRange.CUSTOM:
            self.time_range = TimeRange.CUSTOM
            self.start_from = start_from
            self.end_at = end_at
        else:
            self.time_range = time_range
        return self

    def set_pagination(self, start):
        self.pagination = start
        return self

    def set_sort_by_date(self, sort_by_date):
        self.sort_by_date = sort_by_date
        return self

    def _get_tbs(self):
        data = []
        if self.time_range == TimeRange.CUSTOM:
            data.append('cdr:1')
            data.append('cd_min:' + self.start_from.strftime('%m/%d/%Y'))
            data.append('cd_max:' + self.end_at.strftime('%m/%d/%Y'))
        else:
            data.append('qdr:{0}'.format(self.time_range))
        if self.sort_by_date:
            data.append('sbd:1')
        if self.show_duplicated and self.time_range != TimeRange.CUSTOM:
            data.append('nsd:1')
        return ','.join(data)

    def get_url(self):
        data = {
            'q': urllib.parse.quote_plus(self.keyword),
            # 'tbm': self.genre,
            # 'hl': 'zh-TW'
        }
        if self.time_range is not None:
            data['tbs'] = self._get_tbs()
        if self.pagination > 0:
            data['start'] = self.pagination
        link = URL_PREFIX + urllib.parse.urlencode(data)
        return urllib.parse.unquote(link)

    def get_news_links(self, page=1):
        """ Get the news link from the search result
        We make a request to the google search, and parse the response html page
        """
        pagination = 10 * (page - 1)
        result = []
        self.set_pagination(pagination)
        soup = get_soup_from_link(self.get_url())
        more_result = False
        if not soup.select('div.g'):
            if soup.select('#captcha'):
                logging.warning('Block by Google!')
            return result, more_result
        else:
            for news_card in soup.select('div.g'):
                link = news_card.a['href']
                # if 'cardu.com' in link:
                #     continue
                title = news_card.find('div', attrs={
                  'role': 'heading'
                })
                title = news_card.h3.text
                posted_at = news_card.find('span', class_='f').text
                result.append({
                    'link': link,
                    'title': title,
                    'posted_at': posted_at
                })
                if news_card.find(class_='card-section'):
                    for card in news_card.find_all(class_='card-section'):
                        title = card.a.text
                        link = card.a['href']
                        result.append({
                            'link': link,
                            'title': title
                        })
            if soup.select('a#pnnext'):
                more_result = True
        return result, more_result
