import argparse
import configparser
import os
import sys
from utils import Crawler
from selenium.webdriver.common.keys import Keys


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("start_date")
    argparser.add_argument("end_date")
    args = argparser.parse_args()

    config = configparser.ConfigParser()
    config.read('conf.ini')

    downloads_path = config.get('general', 'downloads_path', fallback='/tmp/downloads/')
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    elif not os.path.isdir(downloads_path):
        print('ERROR: downloads_path parameter points to file!')
        sys.exit(1)

    crawler = Crawler(config, 'washington')
    crawler.get(config.get('washington', 'url'))
    crawler.send_keys('#DateReleasedStart', args.start_date + Keys.ESCAPE)
    crawler.send_keys('#DateReleasedEnd', args.end_date + Keys.ESCAPE)
    crawler.click('#SearchReportsBt')
    crawler.wait_for_displayed('#resultsContainer')
    current_page = int(crawler.get_text('.pageItemSel'))
    while True:
        for row in crawler.browser.find_elements_by_css_selector('#resultsContainer table.table tbody tr'):
            row_type = row.find_element_by_css_selector('td[data-bind="text: AuditTypeName"]').text
            if row_type.lower() not in ('financial', 'financial and federal'):
                continue
            a = row.find_element_by_css_selector('td:first-child a')
            url = a.get_attribute('href')
            text = a.text
            crawler.download(url, '{} {}.pdf'.format(text, row_type))
        current_page += 1
        try:
            crawler.click('#PagerPage{}'.format(current_page))
            crawler.wait_for_displayed('#resultsContainer')
        except Exception:
            break
