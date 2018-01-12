import argparse
import configparser
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'AK'

    def _get_remote_filename(self, local_filename):
        return 'General Purpose', '{} {}'.format(self.abbr, local_filename)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("year")
    args = argparser.parse_args()

    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'alaska')
    crawler.get(config.get('alaska', 'url'))

    crawler.select_option('#dropDown_Year', args.year)
    crawler.click('#MainContent_btnSearch')
    for row in crawler.get_elements('#MainContent_gvFinancialDocuments tr'):
        if crawler.get_elements('th', root=row):
            continue
        items = crawler.get_elements('td', root=row)
        if items[1].text.strip() in ('Certified Financial Statement', 'Audit'):
            url = crawler.get_attr('a', 'href', root=items[3])
            name = items[0].text
            year = items[2].text
            crawler.download(url, '{} {}.pdf'.format(name, year))
            crawler.upload_to_ftp('{} {}.pdf'.format(name, year))
    crawler.close()
