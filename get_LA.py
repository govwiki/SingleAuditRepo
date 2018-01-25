import configparser
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'LA'

    def _get_remote_filename(self, local_filename):
        if local_filename.startswith('City of '):
            directory = 'General Purpose'
            name = local_filename.replace('City of ', '')
        else:
            if 'Inc.' in local_filename or 'Foundation' in local_filename:
                directory = 'Non-Profit'
            else:
                directory = 'Special District'
            name = local_filename
        filename = '{} {}'.format(self.abbr, name)
        return directory, filename


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'loisiana')
    crawler.get(config.get('loisiana', 'url').strip())
    hrefs_clicked = []
    for url in crawler.get_attr('#parishes a', 'href', single=False)[:-1]:
        loaded = False
        while not loaded:
            crawler.get(url)
            loaded = True
            for box in crawler.get_elements('div.box'):
                href = crawler.get_attr('a', 'href', root=box)
                if href in hrefs_clicked:
                    continue
                loaded = False
                hrefs_clicked.append(href)
                crawler.click('a', root=box)
                crawler.wait_for_displayed('tr.even')
                while True:
                    for row in crawler.get_elements('tbody tr'):
                        year = crawler.get_text('.sorting_1', root=row).split('/')[-1]
                        crawler.download(
                            crawler.get_attr('a', 'href', root=row),
                            '{} {}.pdf'.format(crawler.get_text('b', root=row), year)
                        )
                        crawler.upload_to_ftp('{} {}.pdf'.format(crawler.get_text('b', root=row), year))
                    try:
                        crawler.assert_exists('li.next.disabled')
                        break
                    except Exception:
                        crawler.click('li.next a')
                break
    crawler.close()
