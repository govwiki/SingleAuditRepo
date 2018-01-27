import argparse
import configparser
import os
import sys
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'NE'

    def _get_remote_filename(self, local_filename):
        year, entity_type, entity_name = local_filename[:-4].split('|')
        if entity_type in ('Cities and Villages', 'Townships', 'Counties'):
            directory = 'General Purpose'
        elif entity_type == 'School Districts':
            directory = 'School District'
        elif entity_type == 'Community Colleges':
            directory = 'Community College Districts'
        else:
            directory = 'Special District'
        filename = '{} {} {}.pdf'.format(self.abbr, entity_name, year)
        return directory, filename


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("start_year")
    argparser.add_argument("end_year")
    args = argparser.parse_args()

    config = configparser.ConfigParser()
    config.read('conf.ini')

    downloads_path = config.get('general', 'downloads_path', fallback='/tmp/downloads/')
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    elif not os.path.isdir(downloads_path):
        print('ERROR: downloads_path parameter points to file!')
        sys.exit(1)

    crawler = Crawler(config, 'nebraska')
    crawler.get(config.get('nebraska', 'url'))
    for year in range(int(args.start_year), int(args.end_year) + 1):
        for county in crawler.get_text('#countyselect option', single=False):
            crawler.select_option('#countyselect', county)
            crawler.select_option('#year', str(year))
            crawler.click('#query')
            disoriented_table_data = []
            for row in crawler.get_elements('table tr'):
                disoriented_table_data.append(crawler.get_elements('td', root=row))
            table_data = [[None] * len(disoriented_table_data) for _ in range(len(disoriented_table_data[0]))]
            for i, row in enumerate(disoriented_table_data):
                for ii, val in enumerate(row):
                    table_data[ii][i] = val
            for report in table_data:
                if report[5] != 'Waiver':
                    if report[4].text != 'N/A':
                        filename = '{}|{}|{}.pdf'.format(
                            year, report[1].text, report[2].text
                        )
                        crawler.download(
                            crawler.get_attr('a', 'href', root=report[4]),
                            filename,
                        )
                        crawler.upload_to_ftp(filename)
            crawler.back()
            crawler.deselect_all('#countyselect')
            crawler.deselect_all('#year')
    crawler.close()
