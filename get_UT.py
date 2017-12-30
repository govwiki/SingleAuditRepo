import argparse
import configparser
from utils import Crawler

ENTITY_TYPES = (
    'City',
    'County',
    'District Health',
    'Interlocal',
    'Local or Special Service District',
    'Mental Health',
    'School District or Charter School',
    'Town',
)


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
            crawler.download(url, 'UT {}.pdf'.format(entity).replace('/', ' '))
