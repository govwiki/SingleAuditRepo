import argparse
import configparser
import os
import sys
import urllib.parse
import urllib.request
from utils import Crawler as CoreCrawler
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import re


class Crawler(CoreCrawler):
    abbr = 'VA'

    def _get_remote_filename(self, local_filename):
        directory = 'School District' if 'Schools' in local_filename else 'General Purpose'
        local_filename = re.sub(r'(\s*-?\s*reissue.*)\.pdf','.pdf',local_filename)
        filename = '{} {}'.format(
            self.abbr, local_filename.replace(' CAFR', '').replace(' Single Audit', '').replace(' Town', '')
        )
        if not re.search("Gate City", filename, re.IGNORECASE) and not re.search("Chase City", filename, re.IGNORECASE):
            filename.replace(' City', '')
        r = re.compile(".*(\d{4})\s*\..{3}")
        if local_filename == "IL Virginia Beach.pdf":
            local_filename = "IL Virginia Beach 2017.pdf"
        year = r.search(local_filename).group(1)
        return directory, filename, year


if __name__ == '__main__':
    script_name = 'get_VA.py'
    start_time = datetime.utcnow()
    result = 1
    error_message = ""
    config_file = ""

    config = configparser.ConfigParser()
    config.read('conf.ini')
    
    crawler = Crawler(config, 'virginia', script_name)
    try:
        argparser = argparse.ArgumentParser()
        argparser.add_argument("--year")
        argparser.add_argument("--category")
        args = argparser.parse_args()
    
        config_file = str(crawler.dbparams)

        crawler.get(crawler.get_property('url','virginia'))
        
        if args.year:
            crawler.send_keys('#ASPxPageControl1_Grid1_ob_Grid1FilterContainer_ctl02_ob_Grid1FilterControl0', args.year + Keys.ENTER)
        if args.category:
            crawler.click('#ob_iDdlddlCategoriesTB')
            crawler.click_xpath('//div[@id="ob_iDdlddlCategoriesItemsContainer"]//ul[@class="ob_iDdlICBC"]//li/b[text() = "{}"]/..'.format(args.category))
    
        urls_downloaded = []
        download_complete = False
        while not download_complete:
            urls = crawler.get_attr('a.blacklink', 'href', single=False)
            if len(urls)<=0:
                print("nothing to download")
                download_complete = True
            for url in urls:
                if url in urls_downloaded:
                    download_complete = True
                    break
                file = urllib.parse.unquote(url).split('/')[-1]
                if ' CAFR' not in file or ' memo ' in file:
                    urls_downloaded.append(url)
                    continue
                file_db_record = crawler.db.readFileStatus(script_name=script_name,file_original_name=file)
                if file_db_record and file_db_record["file_status"] == 'Uploaded':
                    print('File {} was uploaded before, skipping download'.format(file))
                    continue
                file_id = None
                if file_db_record:
                    file_id = file_db_record["id"]
                downloaded = crawler.download(url, file,file_id)
                if downloaded:
                    crawler.upload_to_file_storage(file)
                    file_path = os.path.join(crawler.get_property('downloads_path', 'virginia'),file)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    if not os.path.exists(file_path):
                        print('Removed {}'.format(file_path))
                urls_downloaded.append(url)
            crawler.click_xpath('//div[@class="ob_gPBC"]/img[contains(@src, "next")]/..')
    except Exception as e:
            result = 0
            error_message = str(e)
    finally:
        end_time = datetime.utcnow()
        crawler.db.log(script_name, start_time, end_time, config_file, result, error_message)
        crawler.close()