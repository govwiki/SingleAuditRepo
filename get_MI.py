import configparser
import os
import sys
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'MI'

    def _get_remote_filename(self, local_filename):
        return 'General Purpose', '{} {}'.format(self.abbr, local_filename)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('conf.ini')

    downloads_path = config.get('general', 'downloads_path', fallback='/tmp/downloads/')
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    elif not os.path.isdir(downloads_path):
        print('ERROR: downloads_path parameter points to file!')
        sys.exit(1)

    crawler = Crawler(config, 'michigan')
    crawler.get(config.get('michigan', 'url'))

    county_list = ['LENAWEE-46', 'LIVINGSTON-47', 'LUCE-48', 'MACKINAC-49', 'MACOMB-50',
                   'MANISTEE-51', 'MARQUETTE-52', 'MASON-53', 'MECOSTA-54', 'MENOMINEE-55']
    # for county in crawler.get_elements('#ddlCounty option'):
    #     if 'Select County' in county.text:
    #         continue
    #     county_list.append(county.text)

    for county in county_list:
        print('Current Selected County:{}'.format(county))
        crawler.select_option('#ddlCounty', county)
        crawler.select_option('#ddlDocument', 'Audit-Financial Report')

        crawler.click('#btnSearch')

        for row in crawler.get_elements('#dgWEB_MF_DOC tr'):
            items = crawler.get_elements('td', root=row)
            year = items[0].text
            if year == 'Year':
                continue
            name = items[1].text
            m_type = items[2].text
            url = crawler.get_attr('a', 'href', root=items[3])

            if (m_type not in name) and (m_type == 'County' or m_type == 'Village' or m_type == 'Charter Township'):
                name = '{} {}'.format(name, m_type)
            if m_type == 'Township':
                if m_type in name:
                    name = '{} ({} County)'.format(name, county.split('-')[0].title())
                else:
                    name = '{} {} ({} County)'.format(name, m_type, county.split('-')[0].title())

            crawler.download(url, '{} {}.pdf'.format(name, year))
            crawler.upload_to_ftp('{} {}.pdf'.format(name, year))
    crawler.close()
