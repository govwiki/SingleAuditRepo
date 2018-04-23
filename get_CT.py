import argparse
import configparser
import os
import sys
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'CT'

    def _get_remote_filename(self, local_filename):
        entity_name, entity_type, year = local_filename[:-4].split('|')
        if entity_type == 'Municipality':
            directory = 'General Purpose'
        elif entity_type == 'Non-Profit':
            directory = 'Non-Profit'
        else:
            directory = 'Special District'
        filename = '{} {} {}.pdf'.format(self.abbr, entity_name, year)
        return directory, filename


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("year")
    args = argparser.parse_args()

    config = configparser.ConfigParser()
    config.read('conf.ini')

    downloads_path = config.get('general', 'downloads_path', fallback='/tmp/downloads/')
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    elif not os.path.isdir(downloads_path):
        print('ERROR: downloads_path parameter points to file!')
        sys.exit(1)

    crawler = Crawler(config, 'connecticut')
    crawler.get(config.get('connecticut', 'url'))

    crawler.send_keys('#ctl00_ContentPlaceHolder1_TextBoxDate', args.year)
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

        print("All files downloaded for {}".format(entity_type))
        path = downloads_path + 'CT'
        file_names = os.listdir(path)
        for filename in file_names:
            real_name = filename.split('Audit Report')[0]
            year = real_name.split(' ')[0]
            name = real_name.replace(year, '').title().strip()
            os.rename(os.path.join(path, filename),
                      os.path.join(path, '{}|{}|{}.pdf'.format(name, entity_type, year)))
            print("Renamed {} to {}".format(filename, '{}|{}|{}.pdf'.format(name, entity_type, year)))
            crawler.upload_to_ftp('{}|{}|{}.pdf'.format(name, entity_type, year))
            os.remove(os.path.join(path, '{}|{}|{}.pdf'.format(name, entity_type, year)))
            if not os.path.exists(os.path.join(path, '{}|{}|{}.pdf'.format(name, entity_type, year))):
                print('Removed {}'.format('{}|{}|{}.pdf'.format(name, entity_type, year)))
    crawler.close()
