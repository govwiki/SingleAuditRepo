import configparser
import os
import sys
import urllib.parse
from utils import Crawler


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'arizona')
    crawler.get(config.get('arizona', 'url_1'))
    while True:
        for row in crawler.browser.find_elements_by_css_selector('div.views-row'):
            row_type = row.find_element_by_css_selector('.views-field-field-audit-type').text
            if 'financial audit' in row_type.lower() or 'single audit' in row_type.lower():
                url = row.find_element_by_css_selector('strong a').get_attribute('href')
                crawler.download(url, urllib.parse.unquote(url).split('/')[-1])
        try:
            crawler.click('.next a')
        except Exception:
            break
    crawler.get(config.get('arizona', 'url_2'))
    while True:
        for row in crawler.browser.find_elements_by_css_selector('div.views-row'):
            row_type = row.find_element_by_css_selector('.views-field-field-audit-type').text
            if 'financial audit' in row_type.lower() or 'single audit' in row_type.lower():
                url = row.find_element_by_css_selector('strong a').get_attribute('href')
                crawler.download(url, urllib.parse.unquote(url).split('/')[-1])
        try:
            crawler.get(crawler.get_attr('.next a', 'href'))
        except Exception:
            break
