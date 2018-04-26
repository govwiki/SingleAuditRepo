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
        if entity_type == 'Common':
            if 'College' in entity_name:
                directory = 'Community College Districts'
            elif 'University' in entity_name:
                directory = 'Public Higher Education'
            elif 'Education' in entity_name or 'School' in entity_name or 'Institute' in entity_name or 'Academy' in entity_name or ' Prep ' in entity_name or ' Prep.' in entity_name or 'Technical Center' in entity_name or 'Technology' in entity_name or 'Influence1 Foundation' in entity_name or 'Voc-Tech' in entity_name or 'New Consortium' in entity_name or 'Elementary' in entity_name or 'Academ' in entity_name:
                directory = 'School Districts'
            elif 'Inc.' in entity_name or 'Incorporated' in entity_name or 'Company' in entity_name or 'Society' in entity_name or 'LLC' in entity_name or 'Community' in entity_name or 'Coalition' in entity_name or 'Arc of' in entity_name or 'Clubs' in entity_name or 'Corporation' in entity_name or 'Memorial Care' in entity_name or 'CARES' in entity_name or 'Neighborhood' in entity_name or 'Program' in entity_name or 'CADAS' in entity_name or 'P.C.' in entity_name or 'Care' in entity_name or 'Independent' in entity_name or 'Bank' in entity_name or 'Organization' in entity_name or 'Friends' in entity_name or 'Initiative' in entity_name or 'Foundation' in entity_name or 'Group' in entity_name or 'Association' in entity_name or 'Residency' in entity_name or 'Commission' in entity_name or 'DDS' in entity_name or 'Support' in entity_name or 'Public' in entity_name or 'Nature' in entity_name or 'Cooperative' in entity_name or 'Parenthood' in entity_name or 'Child' in entity_name or 'Panel' in entity_name or 'Catholic' in entity_name or 'Alliance' in entity_name or 'Nursing' in entity_name:
                directory = 'Non-Profit'
            elif 'Department' in entity_name or 'Division' in entity_name or 'Agency' in entity_name or 'Authority' in entity_name or 'Center' in entity_name or 'Museum' in entity_name or 'Utilit' in entity_name or 'Pension' in entity_name or 'Development' in entity_name or 'Service' in entity_name or 'Energy' in entity_name or 'Transportation' in entity_name or 'Airport' in entity_name or 'Gas' in entity_name or 'Water' in entity_name or 'Sewer' in entity_name or 'Medical' in entity_name or 'Electric' in entity_name or 'Golf' in entity_name or 'Animal Shelter' in entity_name or 'Light' in entity_name or 'Power' in entity_name or 'Transit' in entity_name or 'Library' in entity_name or 'Stadium' in entity_name or 'Housing' in entity_name or 'Sport' in entity_name or 'Cemetery' in entity_name or 'Stormwater' in entity_name or 'Area Investment' in entity_name or 'Redevelopment' in entity_name or 'Landfill' in entity_name or 'Health' in entity_name or 'Homes' in entity_name or 'Government' in entity_name or 'Hous' in entity_name or 'Tennergy' in entity_name or 'Municipal' in entity_name or 'Risk Management' in entity_name or 'Promotion' in entity_name or 'Facility' in entity_name or 'Traffic' in entity_name:
                directory = 'Special Districts'
            else:
                directory = 'General Purpose'
                
        elif entity_type == 'Special District' and 'Community College' in entity_name:
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
    #sections = {'ContentPlaceHolder1_lnkCities':'General Purpose','ContentPlaceHolder1_lnkHousing':'Special Districts','ContentPlaceHolder1_lnkNonProfit':'Non-Profit','ContentPlaceHolder1_lnkQuasi':'Special Districts','ContentPlaceHolder1_lnkSchools':'School Districts','ContentPlaceHolder1_lnkUtilities':'Special Districts'}
    sections = {'ContentPlaceHolder1_lnkAll':'Common'}
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
