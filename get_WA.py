import argparse
import configparser
import os
import sys
from utils import Crawler as CoreCrawler
from selenium.webdriver.common.keys import Keys


class Crawler(CoreCrawler):
    abbr = 'WA'

    def _get_remote_filename(self, local_filename):
        entity_name, entity_type, year = local_filename[:-4].split('|')
        if entity_type == 'City_Town':
            name = entity_name.split(' of ')[1]
            directory = 'General Purpose'
        elif entity_type == 'County':
            name = entity_name
            directory = 'General Purpose'
        elif entity_type in ('School Districts', 'Educational Service District (ESD)'):
            name = entity_name
            directory = 'School District'
        elif 'Community' in entity_type and 'College' in entity_type:
            name = entity_name
            directory = 'Community College Districts'
        else:
            name = entity_name
            directory = 'Special District'
        filename = '{} {} {}.pdf'.format(self.abbr, name, year)
        return directory, filename


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("start_date")
    argparser.add_argument("end_date")
    args = argparser.parse_args()

    config = configparser.ConfigParser()
    config.read('conf.ini')

    downloads_path = config.get('general', 'downloads_path', fallback='/tmp/downloads/')
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    elif not os.path.isdir(downloads_path):
        print('ERROR: downloads_path parameter points to file!')
        sys.exit(1)

    crawler = Crawler(config, 'washington')
    crawler.get(config.get('washington', 'url'))
    crawler.send_keys('#DateReleasedStart', args.start_date + Keys.ESCAPE)
    crawler.send_keys('#DateReleasedEnd', args.end_date + Keys.ESCAPE)
    crawler.click('#SearchReportsBt')
    crawler.wait_for_displayed('#resultsContainer')
    current_page = int(crawler.get_text('.pageItemSel'))
    while True:
        for row in crawler.browser.find_elements_by_css_selector('#resultsContainer table.table tbody tr'):
            row_type = crawler.get_text('td[data-bind="text: AuditTypeName"]', root=row)
            if row_type.lower() not in ('financial', 'financial and federal'):
                continue
            entity_type = crawler.get_text('td[data-bind="text: GovTypeDesc"]', root=row)
            year = crawler.get_text('td[data-bind="dateString: DateReleased, datePattern: \'MM/dd/yyyy\'"]', root=row).split('/')[-1]
            a = crawler.get_elements('td:first-child a', root=row)[0]
            url = a.get_attribute('href')
            text = a.text
            crawler.download(url, '{}|{}|{}.pdf'.format(text, entity_type.replace('/', '_'), year))
            crawler.upload_to_ftp('{}|{}|{}.pdf'.format(text, entity_type.replace('/', '_'), year))
        current_page += 1
        try:
            crawler.click('#PagerPage{}'.format(current_page))
            crawler.wait_for_displayed('#resultsContainer')
        except Exception:
            break
    crawler.close()
