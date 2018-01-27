import argparse
import configparser
import urllib.parse
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'FL'

    def _get_remote_filename(self, local_filename):
        entity_type, local_filename = local_filename.split('|')
        parts = local_filename[:-4].split(' ')
        year = parts[0]
        name = ' '.join([p.capitalize() for p in parts[1:]])
        if entity_type == 'Municipalities':
            directory = 'General Purpose'
        elif entity_type == 'Counties':
            directory = 'General Purpose'
        elif entity_type == 'Special Districts':
            directory = 'Special District'
        elif entity_type == 'District School Boards':
            directory = 'School District'
        filename = '{} {} {}.pdf'.format(self.abbr, name, year)
        return directory, filename


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("start_year")
    argparser.add_argument("end_year")
    args = argparser.parse_args()
    years_range = range(int(args.start_year), int(args.end_year) + 1)

    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'florida')
    for url in config.get('florida', 'urls').split('\n'):
        crawler.get(url.strip())
        entity_type = crawler.get_text('h1')
        for state_url in crawler.get_attr('div.column1 a, div.column2 a', 'href', single=False):
            crawler.get(state_url)
            report_urls = crawler.get_attr('p.efile a', 'href', single=False)
            urls = {}
            for url in report_urls:
                year = url.split('/')[-1][:4]
                if int(year) in years_range:
                    if year not in urls:
                        urls[year] = []
                    urls[year].append(url)
            for year in urls:
                filenames = []
                for url in urls[year]:
                    filename = '{}|{}'.format(
                        entity_type,
                        urllib.parse.unquote(url).split('/')[-1]
                    )
                    crawler.download(url, filename)
                    filenames.append(filename)
                if len(filenames) > 1:
                    if not all(['part' in filename.lower() for filename in filenames]):
                        filename = None
                        for filename in filenames:
                            crawler.upload_to_ftp(filename)
                    else:
                        filename = crawler.merge_files(filenames).replace(' -', '')
                else:
                    filename = filenames[0]
                if filename:
                    crawler.upload_to_ftp(filename)
    crawler.close()
