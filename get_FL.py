import argparse
import configparser
import urllib.parse
from utils import Crawler


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("start_year")
    argparser.add_argument("end_year")
    args = argparser.parse_args()
    years_range = range(int(args.start_year), int(args.end_year) + 1)

    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'florida')
    for url in config.get('florida', 'urls').split('\n'):
        crawler.get(url.strip())
        for state_url in crawler.get_attr('div.column1 a, div.column2 a', 'href', single=False):
            crawler.get(state_url)
            report_urls = crawler.get_attr('p.efile a', 'href', single=False)
            for url in report_urls:
                if int(url.split('/')[-1][:4]) + 1 in years_range:
                    crawler.download(url, urllib.parse.unquote(url).split('/')[-1])
