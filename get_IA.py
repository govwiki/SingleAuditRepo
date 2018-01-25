import argparse
import configparser
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'IA'

    def _get_remote_filename(self, local_filename):
        entity_type, name = local_filename.split('|')
        if entity_type in ('City', 'County'):
            directory = 'General Purpose'
        elif entity_type == 'School':
            directory = 'School District'
        else:
            directory = 'Special District'
        return directory, '{} {}'.format(self.abbr, name.replace('/', ' '))


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'iowa')
    crawler.get(config.get('iowa', 'url'))

    crawler.select_option('#edit-field-audit-category-tid', 'Financial Statement')
    crawler.click('#edit-submit-audit-reports')
    while True:
        for row in crawler.get_elements('tbody tr'):
            try:
                url = crawler.get_attr('.file a', 'href', root=row)
            except Exception:
                continue
            cols = crawler.get_elements('td', root=row)
            entity_type = cols[1].text.strip()
            entity_name = cols[0].text.strip()
            year = cols[3].text.strip().split('/')[-1]
            filename = '{}|{} {}.pdf'.format(entity_type, entity_name, year)
            crawler.download(url, filename)
            crawler.upload_to_ftp(filename)
        try:
            crawler.click('.pager-next a')
        except Exception:
            break
    crawler.close()
