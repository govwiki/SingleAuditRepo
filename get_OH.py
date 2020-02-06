import configparser
import os
import shutil
import sys
from datetime import datetime
from time import sleep

from utils import Crawler as CoreCrawler

schools = ['STEM School District', 'School', 'Community School District']
colleges = ['Universities, Colleges, Tech Schools']
special_districts = ['Insurance Pool', 'Metropolitan Housing Authority',
                     'Special Improvement District', 'Library/Law Library',
                     'Police/Fire/EMS/Ambulance District', 'Cemetery', 'Family and Children First Council',
                     'Community Improvement Corporation / Land Reutilization Corporation', 'Landfill',
                     'Retirement System', 'Airport/Transit/Port Authority/Convention Facilities / Financial Auth',
                     'Transportation Improvement District/Regional Project',
                     'Board of Health', 'State Agency', 'Visitor and Convention Bureau',
                     'Water/Sewer/Sanitary District', 'Workforce Development Area Agency',
                     'Soil/Water Conservation District/Joint Board',
                     'Community Based/Multi-County/Juvenile Correctional Facility',
                     'JEDD/JEDZ– Joint Economic Development District/Zone', 'Hospital', 'Agricultural Society',
                     'Child support', 'Conservancy District', 'County Board of Developmental Disabilities', 'Court',
                     'Developmental Disabilities Council', 'Educational Service Center/District',
                     'Emergency Management/Planning Agency', 'Medicaid Program', 'Medicaid Provider',
                     'Park/Recreation District', 'Political Party', 'Public Assistance',
                     'Regional Planning Commission / Organization', 'Solid Waste District']
general_purpose = ['Township', 'City', 'County', 'Village']


class Crawler(CoreCrawler):
    abbr = 'OH'

    def _get_remote_filename(self, local_filename):
        entity_type, entity_name, year = local_filename[:-4].split('|')
        if entity_type == 'General Purpose':
            name = entity_name
            directory = 'General Purpose'
        elif entity_type == 'Special District':
            name = entity_name
            directory = 'Special District'
        elif entity_type == 'School District':
            name = entity_name
            directory = 'School District'
        elif entity_type == 'Community College Districts':
            name = entity_name
            directory = 'Community College Districts'
        elif entity_type == 'Public Higher Education':
            name = entity_name
            directory = 'Public Higher Education'
        else:
            name = entity_name
            directory = 'Non-Profit'
        name = name.title()
        filename = '{} {} {}.pdf'.format(self.abbr, name, year)
        return directory, filename, year


if __name__ == '__main__':
    script_name = 'get_OH.py'
    start_time = datetime.utcnow()
    result = 1
    error_message = ""
    config_file = ""

    config = configparser.ConfigParser()
    config.read('conf.ini')

    crawler = Crawler(config, 'ohio', script_name, error_message)
    error_message = crawler.error_message
    try:
        if error_message != "":
            raise Exception(error_message)
        config_file = str(crawler.dbparams)

        downloads_path = crawler.get_property('downloads_path', 'ohio')
        if not os.path.exists(downloads_path):
            os.makedirs(downloads_path)
        elif not os.path.isdir(downloads_path):
            print('ERROR: downloads_path parameter points to file!')
            sys.exit(1)
        crawler.get(config.get('ohio', 'url'))
        crawler.select_option('#ddlReportType', 'Financial Audit')
        crawler.click('#btnSubmitSearch')
        urls = []
        for row in crawler.get_elements('#dgResults tr'):
            if (row.text != 'Entity Name County Report Type Entity Type Report Period Release Date'):
                a = row.find_element_by_tag_name('a')
                attribute = a.get_attribute('href')
                urls.append(attribute)
        for url in urls:
            path = downloads_path
            for filename1 in os.listdir(path):
                file_path = os.path.join(path, filename1)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
            crawler.get(url)
            pdf_url = crawler.get_elements('#hlReport')
            entity_name = crawler.get_elements('#lblEntityName')[0].text
            if '/' in entity_name:
                entity_name = entity_name.replace('/', '-')
            entity_type = crawler.get_elements('#lblEntityType')[0].text
            if entity_type in general_purpose:
                if 'City of' in entity_name:
                    entity_name = entity_name.split(' of ')[1].capitalize()
                entity_type = 'General Purpose'
            elif entity_type in special_districts:
                entity_type = 'Special District'
            elif entity_type in schools:
                entity_type = 'School District'
            elif entity_type in colleges:
                if 'Community' not in entity_name:
                    entity_type = 'Public Higher Education'
                else:
                    entity_type = 'Community College Districts'
            else:
                entity_type = 'Non-Profit'
            year = crawler.get_elements('#lblToDate')[0].text[-4:]
            new_file_name = '{}|{}|{}.pdf'.format(entity_type, entity_name, year)
            pdf_url[0].click()
            counter = 10000
            finished = False
            while not finished and counter > 0:
                sleep(3)
                finished = True
                for filename in os.listdir(downloads_path):
                    if filename.endswith(".crdownload") or filename.endswith(".tmp"):
                        print('waiting for file ' + filename)
                        counter -= 1
                        finished = False
            sleep(3)
            try:
                os.rename(os.path.join(path, filename),
                          os.path.join(path, new_file_name))
                print("Renamed {} to {}".format(filename, new_file_name))
            except Exception as e:
                print('Failed to rename ' + filename + ' to ' + new_file_name)
                print(e)
            if os.path.exists(os.path.join(path, new_file_name)):
                crawler.upload_to_ftp(new_file_name)
            if os.path.exists(os.path.join(path, new_file_name)):
                os.remove(os.path.join(path, new_file_name))
            if not os.path.exists(os.path.join(path, new_file_name)):
                print('Removed {}'.format(new_file_name))
    except Exception as e:
        result = 0
        error_message = str(e)
        print(e)
    finally:
        end_time = datetime.utcnow()
        crawler.db.log(script_name, start_time, end_time, config_file, result, error_message)
        crawler.close()
