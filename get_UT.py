import argparse
import configparser
from utils import Crawler as CoreCrawler


ENTITY_TYPES = (
    'City',
    'County',
    'District Health',
    'Interlocal',
    'Local and Special Service District',
    'Mental Health',
    'School District or Charter School',
    'Town',
)


class Crawler(CoreCrawler):
    abbr = 'UT'

    def _get_remote_filename(self, local_filename):
        entity_name, entity_type, year = local_filename[:-4].split('|')
        if entity_type in ('City' 'Town'):
            directory = 'General Purpose'
            name = entity_name.replace(' Town', '').replace(' City', '')
        elif entity_type in ('City' 'Town'):
            directory = 'General Purpose'
            name = entity_name
        elif entity_type == 'School District or Charter School':
            directory = 'School District'
            name = entity_name
        else:
            directory = 'Special District'
            name = entity_name
        filename = '{} {} {}.pdf'.format(self.abbr, name, year)
        return directory, filename


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("year")
    args = argparser.parse_args()

    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'utah')
    crawler.get(config.get('utah', 'url'))

    for entity_type in ENTITY_TYPES:
        crawler.select_option('form[method="post"] .entityTypeSelect', entity_type)
        for entity in crawler.get_text('form[method="post"] .entitySelect option', single=False):
            if entity.startswith('--'):
                continue
            crawler.select_option('form[method="post"] .entitySelect', entity)
            try:
                crawler.select_option('form[method="post"] .yearSelect', args.year)
                crawler.select_option('form[method="post"] .documentSelect', 'Financial Report')
            except Exception:
                continue
            crawler.click('.btn.btnUploadDetails.btnSearch')
            url = crawler.get_attr('tbody.reportData a', 'href')
            crawler.download(url, '{}|{}|{}.pdf'.format(entity, entity_type, args.year).replace('/', ' '))
            crawler.upload_to_ftp('{}|{}|{}.pdf'.format(entity, entity_type, args.year).replace('/', ' '))
    crawler.close()
