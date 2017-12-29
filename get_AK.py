import argparse
import configparser
import urllib.parse
from utils import Crawler


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("year")
    args = argparser.parse_args()

    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'alaska')
    crawler.get(config.get('alaska', 'url'))

    crawler.select_option('#dropDown_Year', args.year)
    crawler.click('#MainContent_btnSearch')
    for row in crawler.get_elements('#MainContent_gvFinancialDocuments tr'):
        if crawler.get_elements('th', root=row):
            continue
        items = crawler.get_elements('td', root=row)
        if items[1].text.strip() in ('Certified Financial Statement', 'Audit'):
            url = crawler.get_attr('a', 'href', root=items[3])
            crawler.download(url, urllib.parse.unquote(url).split('/')[-1])
