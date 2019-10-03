import configparser
import os
import sys
from utils import Crawler as CoreCrawler
from datetime import datetime
import argparse
from time import sleep
import re


class Crawler(CoreCrawler):
    abbr = 'MI'

    def _get_remote_filename(self, local_filename):
        entity_name, entity_type, year = local_filename[:-4].split('#$')
        if (entity_type == 'County') or (entity_type == 'City') or \
                (entity_type == 'Township') or (entity_type == 'Village'):
            directory = 'General Purpose'
        elif entity_type == 'Community College':
            directory = 'Community College District'
        else:
            directory = 'Special District'
        entity_name = re.sub(r"(\s*\(.*\))","",entity_name)
        filename = '{} {} {}.pdf'.format(self.abbr, entity_name, year)
        return directory, filename, year


if __name__ == '__main__':
    script_name = 'get_MI.py'
    start_time = datetime.utcnow()
    result = 1
    error_message = ""
    config_file = ""

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--year", default = None, required = False)
    args = argparser.parse_args()
        
    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'michigan', script_name, error_message)
    error_message = crawler.error_message
    try:
        if error_message!="":
            raise Exception(error_message)
        config_file = str(crawler.dbparams)
        
        downloads_path = crawler.get_property('downloads_path', 'michigan')
        if not os.path.exists(downloads_path):
            os.makedirs(downloads_path)
        elif not os.path.isdir(downloads_path):
            print('ERROR: downloads_path parameter points to file!')
            sys.exit(1)
        
        
        crawler.get(crawler.get_property('url','michigan'))
    
        county_list = []
        for county in crawler.get_elements('#ddlCounty option'):
            if 'Select County' in county.text:
                continue
            county_list.append(county.text)
    
        for county in county_list:
            print('Current Selected County:{}'.format(county))
            crawler.select_option('#ddlCounty', county)
            crawler.select_option('#ddlDocument', 'Audit-Financial Report')
            if args.year:
                crawler.send_keys('#txtYear', args.year)
    
            crawler.click('#btnSearch')
            
            sleep(1)
            crawler.close_dialog()
    
            for row in crawler.get_elements('#dgWEB_MF_DOC tr'):
                items = crawler.get_elements('td', root=row)
                year = items[0].text
                if year == 'Year':
                    continue
                name = items[1].text.replace("/","-")
                entity_type = items[2].text
                url = crawler.get_attr('a', 'href', root=items[3])
    
                if (entity_type not in name) and (entity_type == 'County' or entity_type == 'Village' or entity_type == 'Charter Township'):
                    name = '{} {}'.format(name, entity_type)
                if entity_type == 'Township':
                    if entity_type in name:
                        name = '{} ({} County)'.format(name, county.split('-')[0].title())
                    else:
                        name = '{} {} ({} County)'.format(name, entity_type, county.split('-')[0].title())
    
                file_name = '{}#${}#${}.pdf'.format(name, entity_type, year)
                downloaded = crawler.download(url, file_name)
                if downloaded:
                    crawler.upload_to_ftp(file_name)
                file_path = os.path.join(crawler.get_property('downloads_path', 'michigan'),file_name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    if not os.path.exists(file_path):
                        print('Removed {}'.format(file_path))
    except Exception as e:
            result = 0
            error_message = str(e)
    finally:
        end_time = datetime.utcnow()
        crawler.db.log(script_name, start_time, end_time, config_file, result, error_message)
        crawler.close()
