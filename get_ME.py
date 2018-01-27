import configparser
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'ME'

    def _get_remote_filename(self, local_filename):
        return 'General Purpose', '{} {}'.format(self.abbr, local_filename)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'maine')
    crawler.get(config.get('maine', 'url'))

    header = crawler.get_text('th', single=False)
    while True:
        for row in crawler.get_elements('tbody tr'):
            items = crawler.get_elements('td', root=row)
            entity_name = items[0].text
            for i, h in enumerate(header):
                if h.isdigit():
                    try:
                        url = crawler.get_attr('a', 'href', root=items[i])
                        year = h
                        filename = '{} {}.pdf'.format(entity_name, year).replace('/', ' ')
                        crawler.download(url, filename)
                        crawler.upload_to_ftp(filename)
                    except Exception:
                        pass
        try:
            crawler.click_xpath('//button[text()="Next"]')
        except Exception:
            break
    crawler.close()
