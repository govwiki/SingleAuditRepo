#! /usr/bin/env python3.5
# Script for scraping pdf files by
# Marc Joffe
# Aleksandar Josifoski
# Script is dependend on selenium, pyvirtualdisplay, BeautifulSoup4
# pip install -U selenium pyvirtualdisplay BeautifulSoup4
# Also is dependend on geckodriver. Explanations for geckodriver few lines bellow
# 2017 February 19

url = 'https://harvester.census.gov/facdissem/SearchA133.aspx'
rangefrom = '02/07/2017'
rangeto = '02/09/2017'
dir_in = '/data/upwork/Marc_Joffe/'  # directory where script will be
dir_downloads = '/data/upwork/Marc_Joffe/downloads/'
headlessMode = False # True is for invisible firefox, while False here will show firefox visible

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import datetime
import time
import html
import os
import sys
import codecs
import ntpath
import logging
import zipfile
import glob

# for selenium to work properly, geckodriver is needed to be downloaded,
# placed in some directory and in next line starting with 
# os.environ that directory should be inserted
# geckodriver can be downloaded from
# https://github.com/mozilla/geckodriver/releases
os.environ["PATH"] += ":/data/Scrape"

timeout = 10        # timeout for openning web page

if headlessMode:
    display = Display(visible=0, size=(1024, 768))
    display.start()

logging.basicConfig(filename=dir_in + 'scrape_pdfs.log', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

logging.debug('Started')

time1 = time.time()

def download():
    def open_tag(css_selector):
        driver.find_element_by_css_selector(css_selector).click()
        
    def enter_in_tag(css_selector, date_string):
        driver.find_element_by_css_selector(css_selector).send_keys(date_string)
    global url
    global rangefrom
    global rangeto
    url = url.strip()
    rangefrom = rangefrom.strip()
    rangeto = rangeto.strip()
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.download.dir", dir_downloads)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip")
    capabilities = DesiredCapabilities.FIREFOX
    capabilities["marionette"] = True
    driver = webdriver.Firefox(firefox_profile=profile, capabilities=capabilities)
    driver.implicitly_wait(timeout)

    print('loading: ' + url)
    try:
        driver.get(url)
    except Exception as e:
        logging.debug(str(e))
        print(str(e))
        sys.exit()
    
    st = html.unescape(driver.page_source)
    open_tag('#ui-id-1') # click on GENERAL INFORMATION
    
    # unselect All Years
    open_tag('#MainContent_UcSearchFilters_FYear_CheckableItems_0')
    # click on 2016
    open_tag('#MainContent_UcSearchFilters_FYear_CheckableItems_1')
    # Fill ranges
    enter_in_tag('#MainContent_UcSearchFilters_DateProcessedControl_FromDate', rangefrom)
    enter_in_tag('#MainContent_UcSearchFilters_DateProcessedControl_ToDate', rangeto)
    print(rangefrom + ' ' + rangeto)
    # click on Search button
    open_tag('#MainContent_UcSearchFilters_btnSearch_top')
    # give info how many results are found
    num_of_results = driver.find_element_by_css_selector('.resultsText').text
    print(num_of_results + ' RECORD(S)')
    logging.debug(num_of_results + ' RECORD(S)')
    try:
        inum_of_results = int(num_of_results)
        bnum = True
        if inum_of_results == 0:
            logging.info("0 results are found")
            print("0 results are found")
            bnum = False
    except:
        logging.critical("num_of_results is not produced")
        print("num_of_results is not produced")
        bnum = False
        
    # examine Selected Audit Reports
    audit_reports_select = Select(driver.find_element_by_css_selector('#MainContent_ucA133SearchResults_ddlAvailZipTop'))
    audit_reports_innerHTML = driver.find_element_by_css_selector('#MainContent_ucA133SearchResults_ddlAvailZipTop').get_attribute("innerHTML")
    innersoup = BeautifulSoup(audit_reports_innerHTML, "html.parser")
    laudit_tags = innersoup.findAll("option")
    laudit = []
    for option in laudit_tags:
        if option["value"].startswith("Audit Reports"):
            laudit.append(option["value"])
    if len(laudit) == 0:
        logging.critical("audit reports list is not produced")
        print("audit reports list is not produced")
        bnum = False

    def is_download_completed():
        time.sleep(30)
        while True:
            l = glob.glob(dir_downloads + '*.part')
            if len(l) == 0:
                # print'Downloading ' + audit + ' completed')
                break
            else:
                time.sleep(30)
                # print('sleeping 30 seconds')

    if bnum:
        # in this for loop we are selecting by groups of 100
        for audit in laudit:
            audit_reports_select.select_by_visible_text(audit)
            # now we click on Download Audits button
            open_tag('#MainContent_ucA133SearchResults_btnDownloadZipTop')
            print('Downloading ' + audit)
            is_download_completed()
    driver.close()
    if headlessMode:
        display.stop()
        
def extract_zip_files():
    pass

def rename_pdfs():
    pass
    
def ftp_upload_pdfs():
    pass
    
def calculate_time():
    time2 = time.time()
    hours = int((time2-time1)/3600)
    minutes = int((time2-time1 - hours * 3600)/60)
    sec = time2 - time1 - hours * 3600 - minutes * 60
    print("processed in %dh:%dm:%ds" % (hours, minutes, sec))    

if __name__ == '__main__':
    # for testing reasons you can comment out needed etape(s)
    download()
    extract_zip_files()
    rename_pdfs()
    ftp_upload_pdfs()
    calculate_time()
    print('Done.')
