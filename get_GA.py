import argparse
import configparser
import os
import sys
import urllib.parse
import urllib.request
from utils import Crawler


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("start_year")
    argparser.add_argument("end_year")
    args = argparser.parse_args()

    config = configparser.ConfigParser()
    config.read('conf.ini')

    downloads_path = config.get('general', 'downloads_path', fallback='/tmp/downloads/')
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    elif not os.path.isdir(downloads_path):
        print('ERROR: downloads_path parameter points to file!')
        sys.exit(1)

    crawler = Crawler(config, 'georgia')
    crawler.get(config.get('georgia', 'url'))
    crawler.select_option('#edit-field-fiscal-year-value-min-year', args.start_year)
    crawler.select_option('#edit-field-fiscal-year-value-max-year', args.end_year)
    last_option = 0
    option_selected = True
    while option_selected:
        crawler.deselect_all('select[multiple="multiple"]')
        for i in range(last_option, last_option + 10):
            option_selected = crawler.select_option_by_index('select[multiple="multiple"]', i)
        last_option += 10
        crawler.click('#edit-submit-financial-documents-advanced')
        all_pages_crawled = False
        while not all_pages_crawled:
            for url in crawler.get_attr('.file a', 'href', single=False):
                crawler.download(url, urllib.parse.unquote(url).split('/')[-1])
            try:
                crawler.click('.pager-next a')
            except Exception:
                all_pages_crawled = True
