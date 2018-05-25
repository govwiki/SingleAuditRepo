import argparse
import configparser
import os
import sys
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'MSRB'

    def _get_remote_filename(self, local_filename):
        name, year = local_filename[:-4].split('|')
        entity_type, entity_name = name.split(': ')
        if entity_type == 'City':
            directory = 'General Purpose'
            name = entity_name
        elif entity_type == 'County':
            directory = 'General Purpose'
            if '(' in entity_name:
                entity_name = entity_name[entity_name.index('(') + 1: entity_name.index(')')]
            name = '{} County'.format(entity_name)
        elif entity_type == 'School District':
            directory = 'School District'
            name = '{} Schools'.format(entity_name)
        elif entity_type == 'State':
            directory = 'General Purpose'
            name = 'State of {}'.format(entity_name)
        filename = '{} {} {}.pdf'.format(self.abbr, name, year)
        return directory, filename


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("start_date")  # ex. 5/18/2018
    argparser.add_argument("end_date")  # ex. 5/18/2018
    args = argparser.parse_args()

    config = configparser.ConfigParser()
    config.read('conf.ini')

    downloads_path = config.get('general', 'downloads_path', fallback='/tmp/downloads/')
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    elif not os.path.isdir(downloads_path):
        print('ERROR: downloads_path parameter points to file!')
        sys.exit(1)

    crawler = Crawler(config, 'msrb')
    crawler.get(config.get('msrb', 'url'))

    if crawler.assert_exists('#ctl00_mainContentArea_disclaimerContent_yesButton') is None:
        crawler.click('#ctl00_mainContentArea_disclaimerContent_yesButton')
    # Accepted Terms of Service

    crawler.click('#disclosuresFilter')
    crawler.send_keys('#postingDateFrom', args.start_date)
    crawler.send_keys('#postingDateTo', args.end_date)

    for row in crawler.get_elements('#financialFilingGridView itemstyle'):
        text = crawler.get_text('label', root=row)
        if text == 'Audited Financial Statements or CAFR':
            crawler.click('#financialFilingCheckBox', root=row)
            print(text)
            break

    crawler.click('#runSearchButton')

    # Check it rendered all data properly
    count = crawler.get_text('#counterLabel')
    print(count)

    crawler.select_option('#lvDocuments_length select', '100')

    for row in crawler.get_elements('#lvDocuments tbody tr'):
    	url = None  # need to implement
    	name = None  # need to implement
    	year = None  # need to implement

    crawler.close()
