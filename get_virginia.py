import argparse
import configparser
import os
import sys
import urllib.parse
import urllib.request
from utils import Crawler
from selenium.webdriver.common.keys import Keys


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--year")
    argparser.add_argument("--category")
    args = argparser.parse_args()

    config = configparser.ConfigParser()
    config.read('conf.ini')

    downloads_path = config.get('general', 'downloads_path', fallback='/tmp/downloads/')
    if not os.path.exists(downloads_path):
        os.mkdir(downloads_path)
    elif not os.path.isdir(downloads_path):
        print('ERROR: downloads_path parameter points to file!')
        sys.exit(1)

    crawler = Crawler(config)
    crawler.get(config.get('virginia', 'url'))
    if args.year:
        crawler.send_keys('#ASPxPageControl1_Grid1_ob_Grid1FilterContainer_ctl02_ob_Grid1FilterControl0', args.year)
        crawler.send_keys('#ASPxPageControl1_Grid1_ob_Grid1FilterContainer_ctl02_ob_Grid1FilterControl0', Keys.ENTER)
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
            r = urllib.request.urlopen(url)
            with open(os.path.join(config.get('general', 'downloads_path', fallback='/tmp/downloads/'), urllib.parse.unquote(url).split('/')[-1]), 'wb') as f:
                f.write(r.read())
            urls_downloaded.append(url)
        crawler.click_xpath('//div[@class="ob_gPBC"]/img[contains(@src, "next")]/..')
    crawler.close()
