# -*- coding: utf-8 -*-

import time
import os
import re
import json
import glob
import shutil
import argparse
import configparser
import requests
import urllib.request
from datetime import datetime
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

unique_pdfs = []

# replace this with your path to script
PATH = '/home/seraphina/Documents/CONTRACTS/UPWORK/PDF_CRAWLING/oregon_scraper_v0/'

# get start time
startTime = datetime.now()

with open('OR_params.txt', 'r') as fp: 
    dparameters = json.load(fp)

#year range
rangeFrom = dparameters["rangeFrom"]
rangeTo = dparameters["rangeTo"]

# generate year range
years = range(int(rangeFrom), int(rangeTo) + 1)
print("testing years...", years)

# generate single year and county
year = dparameters["year"]
county = dparameters["county"]


def init_driver():
    print("start time is: ", startTime)
    print("initiallising the driver...")
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=options)
    driver.wait = WebDriverWait(driver, 5)
    return driver

def scrape(driver):

    global dump
    global pdf

    driver.get("https://secure.sos.state.or.us/muni/public.do")

    ### GET DATA FROM RESULTS ###
    def extract_data():

        global doc_types
        global doc_titles
        global get_year
        global pdfs

        # integrate this into a function
        doc_types = driver.find_elements_by_xpath('//*[@id="content"]/table//tr[1]/td[2]')
        doc_types = [record.text for record in doc_types if not re.match('.*?(?:(\d+\s+)+\s*>>|<<\s*\d+(\s+\d+)+).*', record.text)]
        # get doc title
        doc_titles = driver.find_elements_by_xpath('//*[@id="content"]/strong')
        doc_titles = [title.text for title in doc_titles]
        # get doc year
        doc_links = driver.find_elements_by_xpath('//*[@id="content"]/form/input[2]')
        doc_link_text = [link.get_attribute('value').encode('utf-8') for link in doc_links]
        get_year = [re.match('.*(20\d{2})', str(year)).group(1) for year in doc_link_text]

        ###GET DOCUMENT ID###
        get_ids = driver.find_elements_by_xpath('//form[@name="resultDisplyForm"]/input[2]')
        get_ids = [re.match('this\.form\.doc_rsn\.value\=\'(\d+)\'', e.get_attribute("onclick")).group(1) for e in get_ids if re.match('this\.form\.doc_rsn\.value\=\'(\d+)\'', e.get_attribute("onclick"))]
        # make list of links for pdfs
        pdfs = ['https://secure.sos.state.or.us/muni/report.do?doc_rsn=' + code for code in get_ids]

        return doc_types, doc_titles, get_year, pdfs

    ### create function - process pdf file names ###   
    def process_files():
        extract_data()
        ### TEST FOR DOC TYPES AND GENERATE NEW DOC NAMES ###
        if doc_types[i] in schools:
            # a) schools
            new_name = 'OR ' + str(doc_titles[i]) + ' ' + str(get_year[i]) + '.pdf'
            print(new_name)
            SCHOOL_DISTRICT = 'School_District/'
            if new_name not in unique_pdfs:
                # move file to relevant folder
                os.rename(PATH + 'new_name', PATH + SCHOOL_DISTRICT + str(new_name))
                unique_pdfs.append(new_name)
        elif doc_types[i] in colleges:
            # b) colleges
            new_name = 'OR ' + str(doc_titles[i]) + ' ' + str(get_year[i]) + '.pdf'
            print(new_name)
            COMMUNITY_COLLEGE_DISTRICT = 'Community_College_District/'
            if new_name not in unique_pdfs:
                # move file to relevant folder
                os.rename(PATH + 'new_name', PATH + COMMUNITY_COLLEGE_DISTRICT + str(new_name))
                unique_pdfs.append(new_name)
        elif doc_types[i] in special_districts:
            # c) special districts
            new_name = 'OR ' + str(doc_titles[i]) + ' ' + str(get_year[i]) + '.pdf'
            print(new_name)
            SPECIAL_DISTRICT = 'Special_District/'
            if new_name not in unique_pdfs:
                # move file to relevant folder
                os.rename(PATH + 'new_name', PATH + SPECIAL_DISTRICT + str(new_name))
                unique_pdfs.append(new_name)
        elif doc_types[i] in general_purpose:
            # d) [a] test for the following types
            GENERAL_PURPOSE = 'General_Purpose/'
            # test for Rule I
            if doc_types[i] == 'COUNTIES':
                # i.e. CA Alameda County 2017.pdf 
                new_name = 'OR ' + str(doc_titles[i]) + ' ' + 'County ' + str(get_year[i]) + '.pdf'
                print(new_name)
                if new_name not in unique_pdfs:
                    # move file to relevant folder
                    os.rename(PATH + 'new_name', PATH + GENERAL_PURPOSE + str(new_name))
                    unique_pdfs.append(new_name)
            else:
                # test for Rule II
                # test for Rule III
                new_name = 'OR ' + str(doc_titles[i]) + ' ' + str(get_year[i]) + '.pdf'
                print(new_name)
                if new_name not in unique_pdfs:
                    # move file to relevant folder
                    os.rename(PATH + 'new_name', PATH + GENERAL_PURPOSE + str(new_name))
                    unique_pdfs.append(new_name)
        # e) non-profit
        else:
            new_name = 'OR ' + str(doc_titles[i]) + ' ' + str(get_year[i]) + '.pdf'
            print(new_name)
            NON_PROFIT = 'Non_Profit/'
            if new_name not in unique_pdfs:
                # move file to relevant folder
                os.rename(PATH + 'new_name', PATH + NON_PROFIT + str(new_name))
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
        location = os.path.abspath(PATH + new_name)
        with open(new_name, 'wb') as location:
            shutil.copyfileobj(dump, location)
        del dump


    ### set options ###
    fiscal_year = Select(driver.find_element_by_id("fiscalYr"))
    fiscal_year.select_by_visible_text(year)
    county_options = Select(driver.find_element_by_id("county"))
    county_options.select_by_visible_text(county)

    driver.find_element_by_xpath('//*[@id="publicsearchform"]/table//input').submit()

    search_results = driver.find_element_by_xpath('//p[@class="search_results"]').text

    ### DEFINE DOCUMENT CATEGORIES ###
    schools = ['CHARTER SCHOOLS', ' SCHOOL DISTRICTS + ESD']
    colleges = ['COMMUNITY COLLEGES']
    special_districts = ['AIR POLLUTION AUTHORITY', 'AIRPORT DISTRICTS', 'CEMETERY DISTRICTS', 'DIKING DISTRICTS', 'DRAINAGE DISTRICTS', 'EMERGENCY COMMUNICATION DIST', 'FLOOD CONTROL DISTRICTS', 'GEOTHERMAL HEATING DISTRICTS', 'HOSPITAL DISTRICTS', 'HOSPITAL FACILITIES AUTHORITY', 'INSECT/HERBICIDE CONTROL DIST', 'IRRIGATION DISTRICTS', 'LIBRARY DISTRICTS', 'LIGHTING DISTRICTS', 'LIVESTOCK DISTRICTS', 'MASS TRANSIT DISTRICTS', 'METROPOLITAN SERVICE DISTRICTS', 'PARKS AND RECREATION DISTRICTS', 'PORT DISTRICTS', 'PUBLIC HOUSING AUTHORITY', 'PUBLIC UTILITY DISTRICTS', 'REGIONAL PLANNING DISTRICTS', 'ROAD ASSESSMENT DISTRICTS', 'RURAL FIRE PROTECTION DISTRICT', 'SANITARY DISTRICTS', 'SOIL WATER CONSERVATION DIST', 'TRANSLATOR DISTRICTS', 'URBAN RENEWAL AGENCIES', 'VECTOR CONTROL DISTRICTS', 'WATER CONTROL DISTRICTS', 'WATER DISTRICTS', 'WATER IMPROVEMENT DISTRICTS', 'WEATHER MODIFICATION DISTRICTS', 'WEED CONTROL DISTRICTS']
    general_purpose = ['CITIES', 'COUNTIES', 'CITY UTILITY BOARDS', 'COUNCIL OF GOVERNMENTS']

    
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
                fiscal_year.select_by_visible_text(year)
                county_options = Select(driver.find_element_by_id("county"))
                county_options.select_by_visible_text(county)
                break

if __name__ == "__main__":
    driver = init_driver()
    scrape(driver)
    time.sleep(5)
    driver.quit()
    print("total runtime is: ", datetime.now() - startTime)