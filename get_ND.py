import configparser
import urllib.parse
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'ND'

    def _get_remote_filename(self, local_filename):
        entity_type, name = local_filename[:-4].split('|')
        year, name = name[:4], name[5:]
        if entity_type == 'Cities':
            directory = 'General Purpose'
            name = name.split(',')[0]
        elif entity_type == 'Counties':
            directory = 'General Purpose'
        elif entity_type == 'School Districts':
            directory = 'School District'
        elif entity_type == 'Special Education Districts':
            directory = 'School District'
        else:
            directory = 'Special District'
        filename = '{} {} {}.pdf'.format(self.abbr, name, year)
        return directory, filename


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'north_dakota')
    crawler.get(config.get('north_dakota', 'url'))

    for entity_type_url in crawler.get_attr('.content a', 'href', single=False):
        crawler.get(entity_type_url)
        entity_type = crawler.get_text('h1')
        for entity_url in crawler.get_attr('.content a', 'href', single=False):
            if entity_url is None or '#' in entity_url:
                continue
            crawler.get(entity_url)
            entity_name = crawler.get_text('h1')
            for row in crawler.get_elements('.content .field'):
                try:
                    name = crawler.get_text('h3', root=row)
                except Exception:
                    continue
                url = crawler.get_attr('a', 'href', root=row)
                filename = '{}|{}.pdf'.format(entity_type, name)
                crawler.download(url, filename)
                crawler.upload_to_ftp(filename)
    crawler.close()
