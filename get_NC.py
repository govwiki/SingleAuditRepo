import configparser
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'NC'

    def _get_remote_filename(self, local_filename):
        year, name = local_filename[:-4].split('|')
        directory = 'Public Higher Education'
        filename = '{} {} {}.pdf'.format(self.abbr, '-'.join(name.split('-')[:-1]).strip(), year)
        return directory, filename


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'north_carolina')
    crawler.get(config.get('north_carolina', 'url'))

    current_page = 1
    while True:
        for row in crawler.get_elements('.GridviewRow,.GridviewAlternatingRow'):
            name = crawler.get_text('td[align="left"]', root=row)
            if 'university' in name.lower():
                url = crawler.get_attr('a[target="_blank"]', 'href', root=row)
                year = crawler.get_text('td:last-child', root=row).split('/')[-1]
                filename = '{}|{}.pdf'.format(year, name)
                crawler.download(url, filename)
                crawler.upload_to_ftp(filename)
        try:
            current_page += 1
            print(current_page)
            if current_page % 10 != 1 and current_page != 1:
                crawler.browser.find_element_by_link_text(str(current_page)).click()
            else:
                crawler.browser.find_elements_by_link_text('...')[-1].click()
        except Exception:
            break
    crawler.close()
