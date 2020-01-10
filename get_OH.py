import configparser
import os
import re
import sys
from datetime import datetime
from time import sleep

from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'OH'

    def _get_remote_filename(self, local_filename):
        entity_name, year = local_filename[:-4].split('@#')
        directory = 'FinancialAudit'
        filename = '{} {} {}.pdf'.format(self.abbr, entity_name, year)
        return directory, filename, year


if __name__ == '__main__':
    script_name = 'get_OH.py'
    start_time = datetime.utcnow()
    result = 1
    error_message = ""
    config_file = ""

    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'ohio', script_name, error_message)
    error_message = crawler.error_message
    try:
        if error_message != "":
            raise Exception(error_message)
        config_file = str(crawler.dbparams)

        downloads_path = crawler.get_property('downloads_path', 'ohio')
        if not os.path.exists(downloads_path):
            os.makedirs(downloads_path)
        elif not os.path.isdir(downloads_path):
            print('ERROR: downloads_path parameter points to file!')
            sys.exit(1)
        crawler.get(config.get('ohio', 'url'))
        crawler.select_option('#ddlReportType', 'Financial Audit')
        crawler.click('#btnSubmitSearch')
        urls = []
        for row in crawler.get_elements('#dgResults tr'):
            if (row.text != 'Entity Name County Report Type Entity Type Report Period Release Date'):
                a = row.find_element_by_tag_name('a')
                attribute = a.get_attribute('href')
                print(attribute)
                urls.append(attribute)
        for url in urls:
            crawler.get(url)
            pdf_url = crawler.get_elements('#hlReport')
            pdf_url[0].click()
            counter = 10000
            finished = False
            while not finished and counter > 0:
                sleep(3)
                finished = True
                for filename in os.listdir(downloads_path):
                    if filename.endswith(".crdownload") or filename.endswith(".tmp"):
                        print('waiting for file ' + filename)
                        counter -= 1
                        finished = False
            sleep(3)
        print("All files downloaded")
        path = downloads_path
        file_names = os.listdir(path)
        for filename in file_names:
            if not filename.endswith(".pdf"):
                continue
            file_id = crawler.db.saveFileStatus(script_name=script_name, file_original_name=filename,
                                                file_upload_path=path,
                                                file_status='Downloaded')
            year = re.findall(r'[0-9]+', filename)
            real_name = filename.replace('_', '').split(year[0])[0]
            year = '20' + year[0]
            new_file_name = '{}@#{}.pdf'.format(real_name, year)
            os.rename(os.path.join(path, filename),
                      os.path.join(path, new_file_name))
            print("Renamed {} to {}".format(filename, new_file_name))
            crawler.upload_to_ftp(new_file_name)
            if os.path.exists(os.path.join(path, new_file_name)):
                os.remove(os.path.join(path, new_file_name))
            if not os.path.exists(os.path.join(path, new_file_name)):
                print('Removed {}'.format(new_file_name))
    except Exception as e:
        result = 0
        error_message = str(e)
        print(e)
    finally:
        end_time = datetime.utcnow()
        crawler.db.log(script_name, start_time, end_time, config_file, result, error_message)
        crawler.close()
