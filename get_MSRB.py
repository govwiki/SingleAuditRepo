import argparse
import configparser
import os
import sys
import time
import re
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    def _get_remote_filename(self, local_filename):
        abbr, entity_name, year = local_filename[:-4].split('|')

        if 'county' or 'cnty' or 'state' in entity_name:
            directory = 'General Purpose'
        elif 'city' in entity_name:
            directory = 'General Purpose'
            entity_name = entity_name.replace('City', '').replace('Of', '').strip()
        elif 'school' in entity_name:
            directory = 'School District'
        else:
            directory = 'Special District'
        filename = '{} {} {}.pdf'.format(abbr, entity_name, year)
        return directory, filename


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("start_date")  # ex. 5/18/2018
    argparser.add_argument("end_date")  # ex. 5/18/2018
    args = argparser.parse_args()

    config = configparser.ConfigParser()
    config.read('conf.ini')

    downloads_path = config.get('general', 'downloads_path', fallback='/tmp/downloads/')
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    elif not os.path.isdir(downloads_path):
        print('ERROR: downloads_path parameter points to file!')
        sys.exit(1)

    crawler = Crawler(config, 'msrb')
    crawler.get(config.get('msrb', 'url'))

    if crawler.assert_exists('#ctl00_mainContentArea_disclaimerContent_yesButton') is None:
        crawler.click('#ctl00_mainContentArea_disclaimerContent_yesButton')
    # Accepted Terms of Service

    crawler.click('#disclosuresFilter')
    crawler.send_keys('#postingDateFrom', args.start_date)
    crawler.send_keys('#postingDateTo', args.end_date)

    for row in crawler.get_elements('#financialFilingGridView itemstyle'):
        text = crawler.get_text('label', root=row)
        if text == 'Audited Financial Statements or CAFR':
            crawler.click('#financialFilingCheckBox', root=row)
            break

    crawler.click('#runSearchButton')
    time.sleep(10)

    # Check it rendered all data properly
    count = crawler.get_text('#counterLabel')
    print(count)

    crawler.select_option('#lvDocuments_length select', '100')

    all_pages_crawled = False
    entity_type = None

    states = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado",
              "Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois",
              "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland",
              "Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana",
              "Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York",
              "North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania",
              "Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah",
              "Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]

    while not all_pages_crawled:
        for row in crawler.get_elements('#lvDocuments tbody tr'):
            if crawler.get_elements('th', root=row):
                continue
            items = crawler.get_elements('td', root=row)
            name = items[0].text.replace('CNTY', 'COUNTY').title()

            if ',' in name:
                name_list = name.split(',')[:-1]
                name = ''.join(name_list)

            for state in states:
                if state in name:
                    if not name.partition(' ')[0] == state:
                        name = name.split(state)[0].strip()
                    break

            posted_date = items[2].text
            render_url = crawler.get_attr('a', 'href', root=items[1])

            if 'http' not in render_url:
                render_url = 'https://emma.msrb.org/' + render_url.replace('../', '')

            print(render_url)
            crawler_detail = Crawler(config, 'msrb')
            crawler_detail.get(render_url)
            time.sleep(10)
            if crawler_detail.assert_exists('#ctl00_mainContentArea_disclaimerContent_yesButton') is None:
                crawler_detail.click('#ctl00_mainContentArea_disclaimerContent_yesButton')

            # Move to detailed page
            member_part = crawler_detail.get_elements('#memberlist tbody tr')
            for member in member_part:
                member_items = crawler_detail.get_elements('td', root=member)
                url = crawler_detail.get_attr('a', 'href', root=member_items[0])
                year = crawler_detail.get_text('#ruleMandatedDiv table tbody tr td')
                if 'for the year ended' in year:
                    year = year.split('for the year ended')[1].split('/')[-1]
                else:
                    year = year.split('/')[-1]

                if name == '-':
                    name = crawler_detail.get_text('td', root=member)
                    name = name.split('Filing -')[-1].split('.pdf')[0]
                    name = re.sub(r'\d+', '', name).replace('-', '').strip()

                addition_name = crawler_detail.get_elements('#divCusip6List ul li')[0].text
                abbr = addition_name.split(',')[-2].strip()

                if not os.path.isfile(downloads_path + '{}|{}|{}.pdf'.format(abbr, name, year)):
                    crawler_detail.download(url, '{}|{}|{}.pdf'.format(abbr, name, year))
            crawler_detail.close()

        # Pagination
        if not crawler.get_elements('.next.paginate_button.paginate_button_disabled'):
            for page_instance in crawler.get_elements('.next.paginate_button'):
                if page_instance.text == 'Next':
                    page_instance.click()
                    time.sleep(10)
                    break
        else:
            all_pages_crawled = True

    crawler.close()
