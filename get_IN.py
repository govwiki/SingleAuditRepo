import configparser
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'IN'

    def _get_remote_filename(self, local_filename):
        entity_type, entity_name, year = local_filename[:-4].split('|')
        if entity_type in ('City', 'Town'):
            directory = 'General Purpose'
            name = [w.capitalize() for w in entity_name.replace('{} OF '.format(entity_type.upper()), '').split(' ')]
        elif entity_type in ('State', 'County'):
            directory = 'General Purpose'
            name = [w.capitalize() for w in entity_name.split(' ')]
        elif entity_type in ('School', 'Charter School'):
            directory = 'School District'
            name = [w.capitalize() for w in entity_name.split(' ')]
        elif entity_type == 'Univercity':
            directory = 'Public Higher Education'
            name = [w.capitalize() for w in entity_name.split(' ')]
        else:
            directory = 'Special District'
            name = [w.capitalize() for w in entity_name.split(' ')]
        return directory, '{} {} {}.pdf'.format(self.abbr, ' '.join(name).replace('/', ' '), year)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'indiana')
    crawler.get(config.get('indiana', 'url'))

    while True:
        for row in crawler.get_elements('tbody tr'):
            try:
                url = crawler.get_attr('.sticky-text-adjustment a', 'href', root=row)
            except Exception:
                continue
            entity_type = crawler.get_text('td[ng-class="{ \'active\': $ctrl.criteria.sortColumn === \'unitType\' }"]', root=row)
            entity_name = crawler.get_text('td[ng-class="{ \'active\': $ctrl.criteria.sortColumn === \'unitName\' }"]', root=row)
            year = crawler.get_text('td[ng-class="{ \'active\': $ctrl.criteria.sortColumn === \'endDate\' }"]', root=row).split('-')[-1]
            filename = '{}|{}|{}.pdf'.format(entity_type, entity_name, year).replace('/', ' ')
            crawler.download(url, filename)
            crawler.upload_to_ftp(filename)
        try:
            crawler.click_xpath('//button[text()="Next"]')
        except Exception:
            break
    crawler.close()
