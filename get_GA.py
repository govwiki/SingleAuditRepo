import argparse
import configparser
import os
import sys
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'GA'

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
    argparser.add_argument("start_year")
    argparser.add_argument("end_year")
    args = argparser.parse_args()

    config = configparser.ConfigParser()
    config.read('conf.ini')

    downloads_path = config.get('general', 'downloads_path', fallback='/tmp/downloads/')
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    elif not os.path.isdir(downloads_path):
        print('ERROR: downloads_path parameter points to file!')
        sys.exit(1)

    crawler = Crawler(config, 'georgia')
    crawler.get(config.get('georgia', 'url'))
    crawler.select_option('#edit-field-fiscal-year-value-min-year', args.start_year)
    crawler.select_option('#edit-field-fiscal-year-value-max-year', args.end_year)
    last_option = 0
    option_selected = True
    while option_selected:
        crawler.deselect_all('select[multiple="multiple"]')
        for i in range(last_option, last_option + 10):
            option_selected = crawler.select_option_by_index('select[multiple="multiple"]', i)
        last_option += 10
        crawler.click('#edit-submit-financial-documents-advanced')
        all_pages_crawled = False
        while not all_pages_crawled:
            for row in crawler.get_elements('tbody tr'):
                url = crawler.get_attr('.file a', 'href', root=row)
                name = crawler.get_text('a', root=row)
                year = crawler.get_text('.date-display-single', root=row)
                crawler.download(url, '{}|{}.pdf'.format(name, year))
                crawler.upload_to_ftp('{}|{}.pdf'.format(name, year))
            try:
                crawler.click('.pager-next a')
            except Exception:
                all_pages_crawled = True
    crawler.close()
