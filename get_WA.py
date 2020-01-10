import argparse
import configparser
import os
import sys
from datetime import datetime
import re

import PyPDF4
from selenium.webdriver.common.keys import Keys

from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'WA'

    def _get_remote_filename(self, local_filename):
        entity_name, entity_type, year = local_filename[:-4].split('|')
        if entity_type == 'City_Town':
            name = entity_name.split(' of ')[1]
            directory = 'General Purpose'
        elif entity_type == 'County':
            name = entity_name
            directory = 'General Purpose'
        elif entity_type in ('School Districts', 'Educational Service District (ESD)'):
            name = entity_name
            directory = 'School District'
        elif 'Community' in entity_type and 'College' in entity_type:
            name = entity_name
            directory = 'Community College Districts'
        else:
            name = entity_name
            directory = 'Special District'
        filename = '{} {} {}.pdf'.format(self.abbr, name, year)
        return directory, filename, year


if __name__ == '__main__':
    script_name = 'get_WA.py'
    start_time = datetime.utcnow()
    result = 1
    error_message = ""

    argparser = argparse.ArgumentParser()
    argparser.add_argument("start_date")
    argparser.add_argument("end_date")
    args = argparser.parse_args()

    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'washington')
    try:
        config_file = str(crawler.dbparams)
        crawler.script_name = script_name
        downloads_path = crawler.get_property('downloads_path', 'washington')
        if not os.path.exists(downloads_path):
            os.makedirs(downloads_path)
        elif not os.path.isdir(downloads_path):
            print('ERROR: downloads_path parameter points to file!')
            sys.exit(1)
        crawler.get(config.get('washington', 'url'))
        crawler.send_keys('#FromDate', args.start_date + Keys.ESCAPE)
        crawler.send_keys('#ToDate', args.end_date + Keys.ESCAPE)
        crawler.click('#primarySearchButton')
        crawler.wait_for_displayed('#gridContainer')
        while True:
            for row in crawler.browser.find_elements_by_css_selector(
                    '#grid > div.k-grid-content.k-auto-scrollable table tbody tr'):
                items = row.find_elements_by_tag_name('td')
                entity_type = items[1].text
                row_type = items[3].text
                if row_type.lower() not in ('financial', 'financial and federal'):
                    continue
                a = row.find_elements_by_tag_name('a')[0]
                url = a.get_attribute('href')
                text = a.text
                year = items[4].text.split('/')[-1]
                file_name = '{}|{}|{}.pdf'.format(text, entity_type.replace('/', '_'), year)
                downloaded = crawler.download(url, file_name, year)
                if downloaded:
                    reader = PyPDF4.PdfFileReader(downloads_path + file_name)
                    page = reader.getPage(0)
                    print(page.extractText().split('\n'))
                    for line in page.extractText().split('\n'):
                        if re.search(r'period', line):
                            year = line[-4:]
                            break
                    new_file_name = '{}|{}|{}.pdf'.format(text, entity_type.replace('/', '_'), year)
                    os.rename(os.path.join(downloads_path, file_name),
                              os.path.join(downloads_path, new_file_name))
                    crawler.upload_to_ftp(new_file_name)
                    # ----------------Files deleting
                    # if os.path.exists(os.path.join(downloads_path, new_file_name)):
                    #     os.remove(os.path.join(downloads_path, new_file_name))
                    # if not os.path.exists(os.path.join(downloads_path, new_file_name)):
                    #     print('Removed {}'.format(new_file_name))
            try:
                crawler.browser.find_element_by_css_selector(
                    '#grid > div.k-pager-wrap.k-grid-pager.k-widget.k-floatwrap > a:nth-child(4) > span').click()
                crawler.wait_for_displayed('#gridContainer')
            except Exception as e:
                print("All files are uploaded")
                break
    except Exception as e:
        print(e)
        result = 0
        error_message = str(e)
    finally:
        end_time = datetime.utcnow()
        crawler.db.log(script_name, start_time, end_time, config_file, result, error_message)
        crawler.close()
