import argparse
import configparser
import os
import sys
import re
from utils import Crawler as CoreCrawler
from selenium.webdriver.common.keys import Keys


class Crawler(CoreCrawler):
    abbr = 'TN'

    def _get_remote_filename(self, local_filename):
        entity_name, entity_type, year = local_filename[:-4].split('@&')
        name = entity_name
        if entity_type == 'Special District' and 'Community College' in entity_name:
            directory = 'Community College Districts'
        elif entity_type == 'Special District' and 'University' in entity_name:
            directory = 'Public Higher Education'
        else:
            directory = entity_type
        filename = '{} {} {}.pdf'.format(self.abbr, name, year)
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

    crawler = Crawler(config, 'tennessee')
    crawler.get(config.get('tennessee', 'url'))
    sections = {'ContentPlaceHolder1_lnkCities':'General Purpose','ContentPlaceHolder1_lnkHousing':'Special Districts','ContentPlaceHolder1_lnkNonProfit':'Non-Profit','ContentPlaceHolder1_lnkQuasi':'Special Districts','ContentPlaceHolder1_lnkSchools':'School Districts','ContentPlaceHolder1_lnkUtilities':'Special Districts'}
    for key,entity_type in sections.items():
        curr_row = 0        
        while True:
            try: 
                crawler.click('#'+key)
                crawler.wait_for_displayed('#ContentPlaceHolder1_gridVendors')
                links = crawler.browser.find_elements_by_css_selector('#ContentPlaceHolder1_gridVendors a.gridStyle')
                size = len(links)
                if curr_row >size:
                    break
                link = links[curr_row]
                link.click()
                crawler.wait_for_displayed('a#ContentPlaceHolder1_HyperLink1')
                for document in crawler.browser.find_elements_by_css_selector('a[id^=ContentPlaceHolder1_rptrParent_rptrChild_]'):
                    block_id, doc_id = re.match(r"ContentPlaceHolder1_rptrParent_rptrChild_(\d+)_hlDocument_(\d+)",document.get_attribute('id')).group(1,2)
                    
                    year = crawler.get_text('span#ContentPlaceHolder1_rptrParent_lblYear_'+block_id)
                    
                    text = document.get_attribute('text')
                    
                    url = document.get_attribute('href')           
                    
                    if url and len(url)>0: 
                        crawler.download(url, '{}@&{}@&{}.pdf'.format(text,entity_type, year))
                        crawler.upload_to_ftp('{}@&{}@&{}.pdf'.format(text,entity_type, year))
                curr_row += 1
                crawler.get(config.get('tennessee', 'url'))
            except Exception as e:
                curr_row += 1
                print('Error in section', key, 'line',  curr_row,  str(e))
                crawler.get(config.get('tennessee', 'url'))
    crawler.close()
