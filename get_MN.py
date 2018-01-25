import configparser
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'MN'

    def _get_remote_filename(self, local_filename):
        year, name = local_filename[:-4].split('|')
        name = name.split(' Financial Statements')[0]
        if name.endswith('County'):
            directory = 'General Purpose'
        else:
            directory = 'Special District'
        filename = '{} {} {}.pdf'.format(self.abbr, name, year)
        return directory, filename


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'minnesota')
    crawler.get(config.get('minnesota', 'url'))

    for elem in crawler.get_elements('#content *'):
        if len(elem.text) == 4 and elem.text.isdigit():
            year = elem.text
        else:
            report_urls = crawler.get_attr('a', 'href', single=False, root=elem)
            crawler.open_new_tab()
            for href in report_urls:
                crawler.get(href)
                name = crawler.get_text('#ctl00_Header_h1Title')
                if 'Financial Statements' in name:
                    url = crawler.get_attr('#content a', 'href')
                    filename = '{}|{}.pdf'.format(year, name).replace('/', ' ')
                    crawler.download(url, filename)
                    crawler.upload_to_ftp(filename)
            crawler.close_current_tab()
    crawler.close()
