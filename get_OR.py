# -*- coding: utf-8 -*-
import configparser
import os
import re
import shutil
import sys
from datetime import datetime
from time import sleep

import requests
from selenium.webdriver.support.ui import Select

from utils import Crawler as CoreCrawler

unique_pdfs = []

# replace this with your path to script
# get start time
startTime = datetime.now()

# year range
rangeFrom = str(datetime.utcnow().year - 3)
rangeTo = str(datetime.utcnow().year)

# generate year range
years = range(int(rangeFrom), int(rangeTo) + 1)
years = list(years)
print("testing years...", years)

### DEFINE DOCUMENT CATEGORIES ###
schools = ['CHARTER SCHOOLS', 'SCHOOL DISTRICTS + ESD']
colleges = ['COMMUNITY COLLEGES']
special_districts = ['AIR POLLUTION AUTHORITY', 'AIRPORT DISTRICTS', 'CEMETERY DISTRICTS', 'DIKING DISTRICTS',
                     'DRAINAGE DISTRICTS', 'EMERGENCY COMMUNICATION DIST', 'FLOOD CONTROL DISTRICTS',
                     'GEOTHERMAL HEATING DISTRICTS', 'HOSPITAL DISTRICTS', 'HOSPITAL FACILITIES AUTHORITY',
                     'INSECT/HERBICIDE CONTROL DIST', 'IRRIGATION DISTRICTS', 'LIBRARY DISTRICTS', 'LIGHTING DISTRICTS',
                     'LIVESTOCK DISTRICTS', 'MASS TRANSIT DISTRICTS', 'METROPOLITAN SERVICE DISTRICTS',
                     'PARKS AND RECREATION DISTRICTS', 'PORT DISTRICTS', 'PUBLIC HOUSING AUTHORITY',
                     'PUBLIC UTILITY DISTRICTS', 'REGIONAL PLANNING DISTRICTS', 'ROAD ASSESSMENT DISTRICTS',
                     'RURAL FIRE PROTECTION DISTRICT', 'SANITARY DISTRICTS', 'SOIL WATER CONSERVATION DIST',
                     'TRANSLATOR DISTRICTS', 'URBAN RENEWAL AGENCIES', 'VECTOR CONTROL DISTRICTS',
                     'WATER CONTROL DISTRICTS', 'WATER DISTRICTS', 'WATER IMPROVEMENT DISTRICTS',
                     'WEATHER MODIFICATION DISTRICTS', 'WEED CONTROL DISTRICTS']
general_purpose = ['CITIES', 'COUNTIES', 'CITY UTILITY BOARDS', 'COUNCIL OF GOVERNMENTS']


class Crawler(CoreCrawler):

    def _get_remote_filename(self, local_filename):
        entity_type, abbr, entity_name, year = local_filename[:-4].split('|')
        entity_name = re.sub(r'\bCO\b', 'County', entity_name)
        if entity_type == 'General_Purpose':
            name = entity_name.title()
            directory = 'General Purpose'
        elif entity_type == 'Special_District':
            entity_name = entity_name.replace('&amp;', '&')
            entity_name = entity_name.replace('RFPD', 'RURAL FIRE PROTECTION DISTRICT')
            entity_name = entity_name.replace('SWCD', 'Soil & Water Conservation District')
            name = entity_name.title()
            directory = 'Special District'
        elif entity_type == 'School_District':
            name = entity_name.title()
            directory = 'School District'
        elif entity_type == 'Community_College_District':
            if 'Community' not in entity_name:
                directory = 'Public Higher Education'
            else:
                directory = 'Community College Districts'
            name = entity_name.title()
        else:
            name = entity_name.title()
            directory = 'Non-Profit'
        filename = '{} {} {}.pdf'.format(abbr, name, year)
        return directory, filename, year


def scrape(driver, download_path):
    global dump
    global pdf
    global year
    global option

    driver.get("https://secure.sos.state.or.us/muni/public.do")

    ### GET DATA FROM RESULTS ###
    def extract_data():

        global doc_types
        global doc_titles
        global get_year
        global pdfs

        ### get code ###
        get_html = driver.find_elements_by_xpath('//div[@id="content"]')
        get_html = [e.get_attribute('innerHTML') for e in get_html]
        split_results = get_html[0].split('<hr>')
        clean = split_results[1:-1]
        clean = [x for x in clean if 'No audit report filed for fiscal year' not in x]


        # integrate this into a function
        doc_types = [
            re.match('(?:.*\n)*.*?<tbody><tr>\n*.*?<td.*?>Type</td>\n*.*?<td.*?>(.*?)<\/td>.*', e).group(1) if re.match(
                '(?:.*\n)*.*?<tbody><tr>\n*.*?<td.*?>Type</td>\n*.*?<td.*?>(.*?)<\/td>.*', e) else '' for e in clean]
        doc_types = [e for e in doc_types if not re.match('.*?(?:(\d+\s+)+\s*>>|<<\s*\d+(\s+\d+)+).*', e)]
        print("doc_types", len(doc_types), doc_types)
        # get doc title
        doc_titles = [re.match('(?:.*\n)*.*?<strong>(.*?)<\/strong>.*', e).group(1) if re.match(
            '(?:.*\n)*.*?<strong>(.*?)<\/strong>.*', e) else '' for e in clean]
        doc_titles = [e for e in doc_titles if not re.match('.*?(?:(\d+\s+)+\s*>>|<<\s*\d+(\s+\d+)+).*', e)]
        print("doc_titles", len(doc_titles), doc_titles)
        # get doc year
        doc_links = driver.find_elements_by_xpath('//*[@id="content"]/form/input[2]')
        doc_link_text = [link.get_attribute('value').encode('utf-8') for link in doc_links]
        get_year = [re.match('.*(20\d{2})', str(year)).group(1) for year in doc_link_text]
        print("get_year", len(get_year), get_year)
        ###GET DOCUMENT ID###
        ids = driver.find_elements_by_css_selector('#content > strong + table + form > input:nth-child(2)')
        get_ids = [re.match('this\.form\.doc_rsn\.value\=\'(\d+)\'', e.get_attribute("onclick")).group(1) for e in ids
                   if re.match('this\.form\.doc_rsn\.value\=\'(\d+)\'', e.get_attribute("onclick"))]
        # make list of links for pdfs
        pdfs = ['https://secure.sos.state.or.us/muni/report.do?doc_rsn=' + code for code in get_ids]
        print(pdfs)
        # print("get_ids", len(get_ids), get_ids)
        return doc_types, doc_titles, get_year, pdfs

    ### create function - process pdf file names ###
    def process_files():
        extract_data()
        ### PROCESS DOC TITLE ###
        if '/' in doc_titles[i]:
            doc_titles[i] = doc_titles[i].replace('/', '-')
        ### TEST FOR DOC TYPES AND GENERATE NEW DOC NAMES ###
        if doc_types[i] in schools:
            # a) schools
            new_name = 'OR|' + str(doc_titles[i]) + '|' + str(get_year[i]) + '.pdf'
            print(new_name)
            SCHOOL_DISTRICT = 'School_District'
            if new_name not in unique_pdfs:
                # move file to relevant folder
                os.rename(os.path.join(download_path, 'new_name'),
                          os.path.join(download_path, SCHOOL_DISTRICT + '|' + new_name))
                print("Renamed {} to {}".format('new_name', SCHOOL_DISTRICT + '|' + new_name))
                unique_pdfs.append(new_name)
        elif doc_types[i] in colleges:
            # b) colleges
            new_name = 'OR|' + str(doc_titles[i]) + '|' + str(get_year[i]) + '.pdf'
            print(new_name)
            COMMUNITY_COLLEGE_DISTRICT = 'Community_College_District'
            if new_name not in unique_pdfs:
                # move file to relevant folder
                os.rename(os.path.join(download_path, 'new_name'),
                          os.path.join(download_path, COMMUNITY_COLLEGE_DISTRICT + '|' + new_name))
                print("Renamed {} to {}".format('new_name', COMMUNITY_COLLEGE_DISTRICT + '|' + new_name))
                unique_pdfs.append(new_name)
        elif doc_types[i] in special_districts:
            # c) special districts
            new_name = 'OR|' + str(doc_titles[i]) + '|' + str(get_year[i]) + '.pdf'
            print(new_name)
            SPECIAL_DISTRICT = 'Special_District'
            if new_name not in unique_pdfs:
                # move file to relevant folder
                os.rename(os.path.join(download_path, 'new_name'),
                          os.path.join(download_path, SPECIAL_DISTRICT + '|' + new_name))
                print("Renamed {} to {}".format('new_name', SPECIAL_DISTRICT + '|' + new_name))
                unique_pdfs.append(new_name)
        elif doc_types[i] in general_purpose:
            # d) [a] test for the following types
            GENERAL_PURPOSE = 'General_Purpose'
            # test for Rule I
            if doc_types[i] == 'COUNTIES':
                # i.e. CA Alameda County 2017.pdf
                new_name = 'OR|' + str(doc_titles[i]) + '|' + str(get_year[i]) + '.pdf'
                print(new_name)
                if new_name not in unique_pdfs:
                    # move file to relevant folder
                    os.rename(os.path.join(download_path, 'new_name'),
                              os.path.join(download_path, GENERAL_PURPOSE + '|' + new_name))
                    print("Renamed {} to {}".format('new_name', GENERAL_PURPOSE + '|' + new_name))
                    unique_pdfs.append(new_name)
            else:
                # test for Rule II
                # test for Rule III
                new_name = 'OR|' + str(doc_titles[i]) + '|' + str(get_year[i]) + '.pdf'
                print(new_name)
                if new_name not in unique_pdfs:
                    # move file to relevant folder
                    os.rename(os.path.join(download_path, 'new_name'),
                              os.path.join(download_path, GENERAL_PURPOSE + '|' + new_name))
                    print("Renamed {} to {}".format('new_name', GENERAL_PURPOSE + '|' + new_name))
                    # os.rename(download_path + 'new_name', download_path + GENERAL_PURPOSE + str(new_name))
                    unique_pdfs.append(new_name)
        # e) non-profit
        else:
            new_name = 'OR|' + str(doc_titles[i]) + '|' + str(get_year[i]) + '.pdf'
            print(new_name)
            NON_PROFIT = 'Non_Profit'
            if new_name not in unique_pdfs:
                # move file to relevant folder
                os.rename(os.path.join(download_path, 'new_name'),
                          os.path.join(download_path, NON_PROFIT + '|' + new_name))
                print("Renamed {} to {}".format('new_name', NON_PROFIT + '|' + new_name))
                unique_pdfs.append(new_name)

    # method for downloading files
    def download_file():
        global dump
        file = requests.get(pdf, stream=True)
        dump = file.raw

    # method for saving and changing name of files
    def save_file():
        global dump
        global new_name
        new_name = 'new_name'
        os.chdir(download_path)
        with open(new_name, 'wb') as location:
            shutil.copyfileobj(dump, location)
        del dump

    ### set options ###
    fiscal_year = Select(driver.find_element_by_id("fiscalYr"))
    county_options = Select(driver.find_element_by_id("county"))

    for year in years:
        fiscal_year.select_by_visible_text(str(year))

        ### GENERATE OPTION LIST ###
        county = Select(driver.find_element_by_id("county"))
        county_options = county.options
        options = [e.text for e in county_options if '\n' not in e.text]

        ### iterate through counties ###
        for option in options:
            print("testing options...", option)
            county.select_by_visible_text(option)
            driver.find_element_by_xpath('//*[@id="publicsearchform"]/table//input').submit()
            search_results = driver.find_element_by_xpath('//p[@class="search_results"]').text

            ### TEST FOR RESULTS ###
            if "No results for search criteria" not in search_results:
                print("content element matches!")

                ### PROCESS FIRST PAGE (I) ###
                # DOWNLOAD AND RENAME FILES
                extract_data()
                for i, pdf in enumerate(pdfs):
                    download_file()
                    save_file()
                    process_files()
                    sleep(5)
                    # test and click next page
                while True:
                    ###TEST FOR NEXT PAGE (II) ###
                    try:
                        next = driver.find_element_by_link_text('>>')
                        next.click()
                        # DOWNLOAD AND RENAME FILES
                        extract_data()

                        for i, pdf in enumerate(pdfs):
                            download_file()
                            save_file()
                            process_files()
                    except:
                        print("No more pages!")
                        new_search = driver.find_element_by_link_text('New Search')
                        new_search.click()
                        fiscal_year = Select(driver.find_element_by_id("fiscalYr"))
                        fiscal_year.select_by_visible_text(str(year))
                        county = Select(driver.find_element_by_id("county"))
                        county_options = county.options
                        options = [e.text for e in county_options if '\n' not in e.text]
                        break


if __name__ == "__main__":
    script_name = 'get_OR.py'
    result = 1
    error_message = ""
    config = configparser.ConfigParser()
    config.read('conf.ini')
    crawler = Crawler(config, 'oregon', script_name, error_message)
    error_message = crawler.error_message
    config_file = str(crawler.dbparams)
    try:
        if error_message != "":
            raise Exception(error_message)
        downloads_path = crawler.get_property('downloads_path', 'oregon')
        if not os.path.exists(downloads_path):
            os.makedirs(downloads_path)
        elif not os.path.isdir(downloads_path):
            print('ERROR: downloads_path parameter points to file!')
            sys.exit(1)
        scrape(crawler.browser, downloads_path)
        sleep(5)
        path = downloads_path
        file_names = os.listdir(path)
        for filename in file_names:
            if not filename.endswith(".pdf"):
                continue
            crawler.upload_to_ftp(filename)
            print("Uploading: " + filename)
            if os.path.exists(os.path.join(path, filename)):
                os.remove(os.path.join(path, filename))
            if not os.path.exists(os.path.join(path, filename)):
                print('Removed {}'.format(filename))
    except Exception as e:
        result = 0
        error_message = str(e)
        print(e)
    finally:
        end_time = datetime.utcnow()
        crawler.db.log(script_name, startTime, end_time, config_file, result, error_message)
        crawler.close()
