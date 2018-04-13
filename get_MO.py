import argparse
import configparser
import os
import sys
import re
import PyPDF2
import requests
from utils import Crawler as CoreCrawler


class Crawler(CoreCrawler):
    abbr = 'MO'

    def _get_remote_filename(self, local_filename):
        return 'General Purpose', '{} {}'.format(self.abbr, local_filename)


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

    crawler = Crawler(config, 'missouri')
    crawler.get(config.get('missouri', 'url'))

    crawler.send_keys('#ContentPlaceHolder1_txtSearch', 'financial')
    crawler.select_option('#ContentPlaceHolder1_ddlStartYear', args.start_year)
    crawler.select_option('#ContentPlaceHolder1_ddlEndYear', args.end_year)

    crawler.click('#ContentPlaceHolder1_btnSearch')
    crawler.click('#ContentPlaceHolder1_rblPageSize_4')

    for row in crawler.get_elements('#ContentPlaceHolder1_gvAudits tr'):
        if crawler.get_elements('th', root=row):
            continue
        items = crawler.get_elements('td', root=row)
        url = crawler.get_attr('a', 'href', root=items[0])
        name = items[0].text
        if 'Financial Statements' not in name:
            continue
        name = name.split(' Financial Statements')[0].replace(' -', '')
        year = items[2].text.split('-')[0]
        crawler.download(url, '{} {}.pdf'.format(name, year))

        downloaded_file_name = downloads_path + 'MO/' + '{} {}.pdf'.format(name, year)
        pdfFileObj = open(downloaded_file_name, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        pageObj = pdfReader.getPage(1)
        try:
            page_text = pageObj.extractText().strip().replace('\n', '')
        except:
            page_text = pdfReader.getPage(2).extractText().strip().replace('\n', '')
        updated_year = re.search('DECEMBER 31, (\d+)', page_text.upper())

        if not updated_year:
            pageObj = pdfReader.getPage(0)
            if pageObj:
                page_text = pageObj.extractText().strip().replace('\n', '')
                updated_year = re.search('DECEMBER 31, (\d+)', page_text.upper())

        if updated_year:
            updated_year = updated_year.group(1)

        else:
            updated_year = int(year) - 1
            print('Manual Calc')

        updated_filename = '{} {}.pdf'.format(name, updated_year)
        os.rename(downloaded_file_name, downloads_path + 'MO/' + updated_filename)
        print('Updated filename as ' + updated_filename)

        crawler.upload_to_ftp('{} {}.pdf'.format(name, updated_year))
    crawler.close()
