import argparse
import configparser
import os
import sys
import urllib.parse
import urllib.request
from utils import Crawler as CoreCrawler
from selenium.webdriver.common.keys import Keys


class Crawler(CoreCrawler):
    abbr = 'VA'

    def _get_remote_filename(self, local_filename):
        if ' CAFR' not in local_filename or ' memo ' in local_filename:
            return None
        directory = 'School District' if 'Schools' in local_filename else 'General Purpose'
        filename = '{} {}'.format(
            self.abbr, local_filename.replace(' CAFR', '').replace(' reissue', '')
        )
        return directory, filename


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--year")
    argparser.add_argument("--category")
    args = argparser.parse_args()

    config = configparser.ConfigParser()
    config.read('conf.ini')

    downloads_path = config.get('general', 'downloads_path', fallback='/tmp/downloads/')
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    elif not os.path.isdir(downloads_path):
        print('ERROR: downloads_path parameter points to file!')
        sys.exit(1)

    crawler = Crawler(config, 'virginia')
    crawler.get(config.get('virginia', 'url'))
    if args.year:
        crawler.send_keys('#ASPxPageControl1_Grid1_ob_Grid1FilterContainer_ctl02_ob_Grid1FilterControl0', args.year + Keys.ENTER)
    if args.category:
        crawler.click('#ob_iDdlddlCategoriesTB')
        crawler.click_xpath('//div[@id="ob_iDdlddlCategoriesItemsContainer"]//ul[@class="ob_iDdlICBC"]//li/b[text() = "{}"]/..'.format(args.category))

    urls_downloaded = []
    download_complete = False
    while not download_complete:
        urls = crawler.get_attr('a.blacklink', 'href', single=False)
        for url in urls:
            if url in urls_downloaded:
                download_complete = True
                break
            crawler.download(url, urllib.parse.unquote(url).split('/')[-1])
            crawler.upload_to_ftp(urllib.parse.unquote(url).split('/')[-1])
            urls_downloaded.append(url)
        crawler.click_xpath('//div[@class="ob_gPBC"]/img[contains(@src, "next")]/..')
    crawler.close()
