import configparser
from utils import Crawler as CoreCrawler
import re
from datetime import datetime
import os
import sys


class Crawler(CoreCrawler):
    abbr = 'AZ'

    def _get_remote_filename(self, local_filename):
        entity_type, year = local_filename[:-4].split('@#')
        directory = ''
        filename = '{} {} {}.pdf'.format(self.abbr, entity_type, year)
        return directory, filename, year


if __name__ == '__main__':
    script_name = 'get_AZ.py'
    start_time = datetime.utcnow()
    result = 1
    error_message = ""
    config_file = ""

    config = configparser.ConfigParser()
    config.read('conf.ini')
    file_name = ''

    crawler = Crawler(config, 'arizona', script_name, error_message)
    error_message = crawler.error_message
    try:
        if error_message != "":
            raise Exception(error_message)
        config_file = str(crawler.dbparams)

        downloads_path = crawler.get_property('downloads_path', 'arizona')
        if not os.path.exists(downloads_path):
            os.makedirs(downloads_path)
        elif not os.path.isdir(downloads_path):
            print('ERROR: downloads_path parameter points to file!')
            sys.exit(1)

        crawler.get(config.get('arizona', 'url'))
        td_e = crawler.get_elements('td')
        for x in range(5, len(td_e)):
            td_e = crawler.get_elements('td')
            a = td_e[x].find_element_by_tag_name('a')
            file_name = crawler.get_text('a', root=td_e[x])
            year = crawler.get_text('span', root=td_e[x])[5:]
            a.click()
            files = crawler.get_elements('span.file')
            url_a = files[0].find_element_by_tag_name('a')
            url = url_a.get_attribute('href')
            crawler.back()
            downloaded = crawler.download(url, '{}@#{}.pdf'.format(file_name[:re.search('June',
                                                                                        file_name).start()].replace(
                ' ', ''), year))
            if downloaded:
                crawler.upload_to_file_storage(
                    '{}@#{}.pdf'.format(file_name[:re.search('June',
                                                             file_name).start()].replace(
                        ' ', ''), year))
    except Exception as e:
        result = 0
        error_message = str(e)
        print(error_message)
    finally:
        end_time = datetime.utcnow()
        crawler.db.log(script_name, start_time, end_time, config_file, error_message)
        crawler.close()
