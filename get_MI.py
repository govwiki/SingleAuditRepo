import configparser
import os
import sys
from utils import Crawler as CoreCrawler


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
        filename = '{} {} {}.pdf'.format(self.abbr, entity_name, year)
        return directory, filename, year


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf.ini')

    downloads_path = config.get('general', 'downloads_path', fallback='/tmp/downloads/')
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    elif not os.path.isdir(downloads_path):
        print('ERROR: downloads_path parameter points to file!')
        sys.exit(1)

    crawler = Crawler(config, 'michigan')
    crawler.get(config.get('michigan', 'url'))

    county_list = []
    for county in crawler.get_elements('#ddlCounty option'):
        if 'Select County' in county.text:
            continue
        county_list.append(county.text)

    for county in county_list:
        print('Current Selected County:{}'.format(county))
        crawler.select_option('#ddlCounty', county)
        crawler.select_option('#ddlDocument', 'Audit-Financial Report')

        crawler.click('#btnSearch')

        for row in crawler.get_elements('#dgWEB_MF_DOC tr'):
            items = crawler.get_elements('td', root=row)
            year = items[0].text
            if year == 'Year':
                continue
            name = items[1].text
            entity_type = items[2].text
            url = crawler.get_attr('a', 'href', root=items[3])

            if (entity_type not in name) and (entity_type == 'County' or entity_type == 'Village' or entity_type == 'Charter Township'):
                name = '{} {}'.format(name, entity_type)
            if entity_type == 'Township':
                if entity_type in name:
                    name = '{} ({} County)'.format(name, county.split('-')[0].title())
                else:
                    name = '{} {} ({} County)'.format(name, entity_type, county.split('-')[0].title())

            crawler.download(url, '{}#${}#${}.pdf'.format(name, entity_type, year))
            crawler.upload_to_ftp('{}#${}#${}.pdf'.format(name, entity_type, year))

    crawler.close()
