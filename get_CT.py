import argparse
import configparser
import os
import sys
from utils import Crawler as CoreCrawler
from datetime import datetime
from time import sleep

class Crawler(CoreCrawler):
    abbr = 'CT'

    def _get_remote_filename(self, local_filename):
        entity_name, entity_type, year = local_filename[:-4].split('@#')
        if entity_type == 'Municipality':
            directory = 'General Purpose'
        elif entity_type == 'Non-Profit':
            directory = 'Non-Profit'
        else:
            directory = 'Special District'
        filename = '{} {} {}.pdf'.format(self.abbr, entity_name, year)
        return directory, filename, year


if __name__ == '__main__':
    script_name = 'get_CT.py'
    start_time = datetime.utcnow()
    result = 1
    error_message = ""
    
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--year", default = None, required = False)
    args = argparser.parse_args()
    
    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'connecticut')
    config_file = str(crawler.dbparams)
    crawler.script_name = script_name
    
    downloads_path = crawler.get_property('downloads_path', 'connecticut')
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    elif not os.path.isdir(downloads_path):
        print('ERROR: downloads_path parameter points to file!')
        sys.exit(1)
    
    try:
        url = crawler.get_property('url','connecticut')
        crawler.get(url)

        year = args.year or crawler.get_property('upload_date', 'connecticut')
    
        crawler.send_keys('#ctl00_ContentPlaceHolder1_TextBoxDate', year)
        crawler.select_option('#ctl00_ContentPlaceHolder1_DropDownListDateExpression', '>=')
    
        entity_type_list = ['Municipality', 'Non-Profit', 'Other']
    
        for entity_type in entity_type_list:
            print('Current entity type:{}'.format(entity_type))
            crawler.select_option('#ctl00_ContentPlaceHolder1_DropDownListEntityType', entity_type)
            crawler.click('#ctl00_ContentPlaceHolder1_ButtonSearch')
    
            for row in crawler.get_elements('#ctl00_ContentPlaceHolder1_GridViewReports tr'):
                if crawler.get_elements('th', root=row):
                    continue
                items = crawler.get_elements('td', root=row)
                name = items[2].text
                items[0].click()
                counter = 10000
                finished = False
                while not finished and counter > 0:
                    sleep(3)
                    finished = True
                    for filename in os.listdir(downloads_path):
                        if filename.endswith(".crdownload") or filename.endswith(".tmp"):
                            print('waiting for file ' + filename)
                            counter-=1
                            finished = False
                sleep(3)
            print("All files downloaded for {}".format(entity_type))
            path = downloads_path 
            file_names = os.listdir(path)
            for filename in file_names:
                if not filename.endswith(".pdf"):
                    continue
                file_id = crawler.db.saveFileStatus(script_name = script_name, file_original_name = filename, file_status = 'Downloaded')
                real_name = filename.split('Audit Report')[0]
                year = real_name.split(' ')[0]
                name = real_name.replace(year, '').title().strip()
                new_file_name = '{}@#{}@#{}.pdf'.format(name, entity_type, year)
                os.rename(os.path.join(path, filename),
                          os.path.join(path, new_file_name))
                crawler.db.saveFileStatus(id = file_id, script_name = script_name, file_original_name = new_file_name, file_status = 'Downloaded')
                print("Renamed {} to {}".format(filename, new_file_name))
                crawler.upload_to_file_storage(new_file_name)
                os.remove(os.path.join(path, new_file_name))
                if not os.path.exists(os.path.join(path, new_file_name)):
                    print('Removed {}'.format(new_file_name))
    except Exception as e:
            result = 0
            error_message = str(e)
    finally:
        end_time = datetime.utcnow()
        crawler.db.log(script_name, start_time, end_time, config_file, result, error_message)
        crawler.close()
