import configparser
import os
import sys
from datetime import datetime

from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'NC'

    def _get_remote_filename(self, local_filename):
        year, name = local_filename[:-4].split('#$')
        directory = 'Public Higher Education'
        filename = '{} {} {}.pdf'.format(self.abbr, '-'.join(name.split('-')[:-1]).strip(), year)
        return directory, filename, year


if __name__ == '__main__':
    script_name = 'get_NC.py'
    start_time = datetime.utcnow()
    result = 1
    error_message = ""

    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'north_carolina', script_name, error_message)
    config_file = str(crawler.dbparams)
    try:
        crawler.script_name = script_name
        downloads_path = crawler.get_property('downloads_path', 'north_carolina')
        if not os.path.exists(downloads_path):
            os.makedirs(downloads_path)
        elif not os.path.isdir(downloads_path):
            print('ERROR: downloads_path parameter points to file!')
            sys.exit(1)
        crawler.get(config.get('north_carolina', 'url'))
        current_page = 1
        while True:
            for row in crawler.get_elements('.GridviewRow,.GridviewAlternatingRow'):
                name = crawler.get_text('td[align="left"]', root=row)
                if 'university' in name.lower():
                    url = crawler.get_attr('a[target="_blank"]', 'href', root=row)
                    year = crawler.get_text('td:last-child', root=row).split('/')[-1]
                    filename = '{}#${}.pdf'.format(year, name)
                    downloaded = crawler.download(url, filename)
                    if downloaded:
                        # crawler.upload_to_ftp(filename)
                        if os.path.exists(os.path.join(downloads_path, filename)):
                            os.remove(os.path.join(downloads_path, filename))
                        if not os.path.exists(os.path.join(downloads_path, filename)):
                            print('Removed {}'.format(filename))
            try:
                current_page += 1
                print(current_page)
                if current_page % 10 != 1 and current_page != 1:
                    crawler.browser.find_element_by_link_text(str(current_page)).click()
                else:
                    crawler.browser.find_elements_by_link_text('...')[-1].click()
            except Exception:
                break
    except Exception as e:
        result = 0
        error_message = str(e)
    finally:
        end_time = datetime.utcnow()
        crawler.db.log(script_name, start_time, end_time, config_file, result, error_message)
        crawler.close()
