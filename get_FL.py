import argparse
import configparser
import urllib.parse
from utils import Crawler as CoreCrawler
from datetime import datetime


class Crawler(CoreCrawler):
    abbr = 'FL'

    def _get_remote_filename(self, local_filename):
        entity_type, local_filename = local_filename.split('@#')
        parts = local_filename[:-4].split(' ')
        year = parts[0]
        name = ' '.join([p.capitalize() for p in parts[1:]])
        if entity_type == 'MUNICIPALITIES':
            directory = 'General Purpose'
        elif entity_type == 'COUNTIES':
            directory = 'General Purpose'
        elif entity_type == 'SPECIAL DISTRICTS':
            directory = 'Special District'
        elif entity_type == 'SCHOOL DISTRICTS':
            directory = 'School District'
        else:
            directory = 'Unclassified'
        filename = '{} {} {}.pdf'.format(self.abbr, name, year)
        return directory, filename, year


if __name__ == '__main__':
    script_name = 'get_FL.py'
    start_time = datetime.utcnow()
    result = 1
    error_message = ""
    argparser = argparse.ArgumentParser()
    argparser.add_argument("start_year")
    argparser.add_argument("end_year")
    args = argparser.parse_args()
    years_range = range(int(args.start_year), int(args.end_year) + 1)

    config = configparser.ConfigParser()
    config.read('conf.ini')
    crawler = Crawler(config, 'florida', script_name)
    config_file = str(crawler.dbparams)
    try:
        urls = None
        if crawler.dbparams is not None and 'urls' in crawler.dbparams:
            urls = crawler.dbparams['urls'].split('\n')
        else:
            urls = config.get('florida', 'urls').split('\n')
        for url in urls:
            crawler.get(url.strip())
            entity_type = crawler.get_text('h1:not(.text-right)')
            for state_url in crawler.get_attr('div.col-12.col-md-6 a, div.col-12.col-md-4 a', 'href', single=False):
                crawler.get(state_url)
                report_urls = crawler.get_attr('p.pl-3 a', 'href', single=False)
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
                        filename = '{}@#{}'.format(
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
    except Exception as e:
            result = 0
            error_message = str(e)
    finally:
        end_time = datetime.utcnow()
        crawler.db.log(script_name, start_time, end_time, config_file, result, error_message)
        crawler.close()
        
