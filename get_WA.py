import argparse
import configparser
import io
import os
import sys
from datetime import datetime
from time import sleep

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from selenium.webdriver.common.keys import Keys

from utils import Crawler as CoreCrawler

schools = ['School Districts', 'Educational Service District (ESD)', 'Public Charter School', 'Tribal Schools']
colleges = ['Community or Technical College']
special_districts = ['Agency, Commission, or Board', 'Agency, Commission, or Board', 'Area Agency on Aging',
                     'Behavioral Health Organization', 'Cemetery District', 'Commodity Commission',
                     'Conservation District', 'Diking_Drainage District', 'Educational Service District',
                     'Emergency Management Service', 'Fire Protection District', 'Flood Control District',
                     'Government Association', 'Health District', 'Hospital District', 'Housing Authority',
                     'Industrial Development Corporation', 'Irrigation and Reclamation District',
                     'Irrigation and Reclamation District', 'Local_Regional Trauma Care Council',
                     'Mosquito_Pest_Weed District', 'Park and Recreation District', 'Port_Airport District',
                     'Public Development Authority', 'Public Facilities District', 'Public Utility District',
                     'Regional Planning Council', 'Risk Pool', 'Stadium Authority', 'Transportation Benefit District',
                     'TV Reception District', 'Water Conservancy Board', 'Water_Sewer District']
general_purpose = ['City_Town', 'County', 'CITY UTILITY BOARDS', 'COUNCIL OF GOVERNMENTS']
public_higher_education = ['University or College']


class Crawler(CoreCrawler):
    abbr = 'WA'

    def _get_remote_filename(self, local_filename):
        entity_name, entity_type, year = local_filename[:-4].split('|')
        if entity_type in general_purpose:
            if 'City of' in entity_name:
                entity_name = entity_name.split(' of ')[1].capitalize()
            name = entity_name
            directory = 'General Purpose'
        elif entity_type in special_districts:
            name = entity_name
            directory = 'Special District'
        elif entity_type in schools:
            name = entity_name
            directory = 'School District'
        elif entity_type in colleges:
            name = entity_name
            directory = 'Community College Districts'
        elif entity_type in public_higher_education:
            name = entity_name
            directory = 'Public Higher Education'
        else:
            name = entity_name
            directory = 'Non-Profit'
        filename = '{} {} {}.pdf'.format(self.abbr, name, year)
        return directory, filename, year


if __name__ == '__main__':
    script_name = 'get_WA.py'
    start_time = datetime.utcnow()
    result = 1
    error_message = ""

    argparser = argparse.ArgumentParser()
    argparser.add_argument("start_date")
    argparser.add_argument("end_date")
    args = argparser.parse_args()
    resource_manager = PDFResourceManager()

    config = configparser.ConfigParser()
    config.read('conf.ini')
    # pdf-miner

    crawler = Crawler(config, 'washington', script_name, error_message)
    try:
        config_file = str(crawler.dbparams)
        crawler.script_name = script_name
        downloads_path = crawler.get_property('downloads_path', 'washington')
        if not os.path.exists(downloads_path):
            os.makedirs(downloads_path)
        elif not os.path.isdir(downloads_path):
            print('ERROR: downloads_path parameter points to file!')
            sys.exit(1)
        crawler.get(config.get('washington', 'url'))
        crawler.send_keys('#Keyword', 'Grant County')
        crawler.send_keys('#FromDate', '01/01/' + args.start_date + Keys.ESCAPE)
        crawler.send_keys('#ToDate', '12/31/' + args.end_date + Keys.ESCAPE)
        crawler.click('div.radioRowItem:nth-child(3) > label:nth-child(2)')
        crawler.click('#primarySearchButton')
        crawler.wait_for_displayed('#gridContainer')
        while True:
            for row in crawler.browser.find_elements_by_css_selector(
                    '#grid > div.k-grid-content.k-auto-scrollable table tbody tr'):
                items = row.find_elements_by_tag_name('td')
                entity_type = items[1].text
                row_type = items[3].text
                if row_type.lower() not in (
                        'financial', 'financial and federal', 'comprehensive annual financial report'):
                    continue
                a = row.find_elements_by_tag_name('a')[0]
                url = a.get_attribute('href')
                text = a.text
                year = items[4].text.split('/')[-1]
                file_name = '{}|{}|{}.pdf'.format(text, entity_type.replace('/', '_'), year)
                downloaded = crawler.download(url, file_name, year)
                reader = None
                text_year = 0
                text_from_pdf_miner = ''
                fake_file_handle = io.StringIO()
                converter = TextConverter(resource_manager, fake_file_handle)
                page_interpreter = PDFPageInterpreter(resource_manager, converter)
                if downloaded:
                    with open(downloads_path + file_name, 'rb') as fh:
                        for page in PDFPage.get_pages(fh,
                                                      caching=True,
                                                      check_extractable=True):
                            page_interpreter.process_page(page)
                            break
                        text_from_pdf_miner = fake_file_handle.getvalue()
                        converter.close()
                        fake_file_handle.close()
                        # close open handles
                    if text_from_pdf_miner is not None and text_from_pdf_miner != '':
                        try:
                            text_year = text_from_pdf_miner.split('31, ')[1][:4]
                            year = text_year
                            print(year)
                        except Exception as e:
                            print(e)
                    new_file_name = '{}|{}|{}.pdf'.format(text, entity_type.replace('/', '_'), year)
                    os.rename(os.path.join(downloads_path, file_name),
                              os.path.join(downloads_path, new_file_name))
                    crawler.upload_to_ftp(new_file_name)
                    # ----------------Files deleting
                    if os.path.exists(os.path.join(downloads_path, new_file_name)):
                        os.remove(os.path.join(downloads_path, new_file_name))
                    if not os.path.exists(os.path.join(downloads_path, new_file_name)):
                        print('Removed {}'.format(new_file_name))
            try:
                crawler.browser.find_element_by_css_selector(
                    '#grid > div.k-pager-wrap.k-grid-pager.k-widget.k-floatwrap > a:nth-child(4) > span').click()
                crawler.wait_for_displayed('#gridContainer')
                sleep(3)
            except Exception as e:
                print("All files are uploaded")
                break
    except Exception as e:
        result = 0
        error_message = str(e)
        print(e)
    finally:
        end_time = datetime.utcnow()
        crawler.db.log(script_name, start_time, end_time, config_file, result, error_message)
        crawler.close()
