import configparser
import os
import datetime
import sys
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'AR'

    def _get_remote_filename(self, local_filename):
        entity_name, entity_type, year = local_filename[:-4].split('|')
        if (entity_type == 'Counties') or (entity_type == 'Cities'):
            directory = 'General Purpose'
        elif (entity_type == 'Education') or (entity_type == 'Higher Education'):
            directory = 'Public Higher Education'
        elif entity_type == 'Public Schools':
            directory = 'School District'
        else:
            directory = 'Special District'
        filename = '{} {} {}.pdf'.format(self.abbr, entity_name.title(), year)
        return directory, filename


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf.ini')

    downloads_path = config.get('general', 'downloads_path', fallback='/tmp/downloads/')
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    elif not os.path.isdir(downloads_path):
        print('ERROR: downloads_path parameter points to file!')
        sys.exit(1)

    crawler = Crawler(config, 'arkansas')
    crawler.get(config.get('arkansas', 'url'))

    entity_list = ['Counties', 'Cities', 'Education', 'Higher Education', 'Public Schools']

    year = datetime.datetime.today().year

    for entity_type in entity_list:
        print('Current Selected Audit Type: {}'.format(entity_type))
        crawler.select_option('#ctl00_MainContent_pc_ctl02_ddlAuditType', entity_type)

        for year in range(year, year - 22, -1):
            print("Current Selected Year is {}".format(year))
            crawler.send_keys('#ctl00_MainContent_pc_ctl02_tbSearchYear', year)

            crawler.click('#ctl00_MainContent_pc_ctl02_btnSearch')

            page_num = 1

            print("Current Selected Page is {}".format(page_num))

            if 'No audits' not in crawler.browser.page_source:
                results = crawler.get_elements('#ctl00_MainContent_pc_ctl02_pnlResults > div')[1:]
                for row in results:
                    items = crawler.get_elements('div', root=row)
                    name = items[1].text.title()
                    url = crawler.get_attr('a', 'href', root=items[1])

                    crawler.download(url, '{}|{}|{}.pdf'.format(name, entity_type, year))
                    crawler.upload_to_ftp('{}|{}|{}.pdf'.format(name, entity_type, year))

            page_num_list = crawler.get_elements('#ctl00_MainContent_pc_ctl02_dpAuditsTop > a')

            if not page_num_list:
                print("No next page")
                continue

            for page in page_num_list:
                if page_num >= 2:
                    page = crawler.get_elements('#ctl00_MainContent_pc_ctl02_dpAuditsTop > a')[int(page_num - 1)]

                if page.text == '...':
                    continue

                if int(page.text) <= page_num:
                    continue

                page_num = int(page.text)
                page.click()
                print("Current Selected Page is {}".format(page_num))

                results = crawler.get_elements('#ctl00_MainContent_pc_ctl02_pnlResults > div')[1:]
                for row in results:
                    items = crawler.get_elements('div', root=row)
                    name = items[1].text.title()
                    url = crawler.get_attr('a', 'href', root=items[1])

                    crawler.download(url, '{}|{}|{}.pdf'.format(name, entity_type, year))
                    crawler.upload_to_ftp('{}|{}|{}.pdf'.format(name, entity_type, year))

    crawler.close()
