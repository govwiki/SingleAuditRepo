#! /usr/bin/env python3.6
# Script for downloading zip files from specific url, extracting pdfs from, then renaming files and uploading via FTP
# Aleksandar Josifoski https://about.me/josifsk
# Script is dependend on selenium, pyvirtualdisplay, BeautifulSoup4, openpyxl
# pip install -U selenium pyvirtualdisplay BeautifulSoup4 openpyxl
# Also is dependend on geckodriver. Explanations for geckodriver few lines bellow
# 2017 February 19

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
import openpyxl
import json
from ftplib import FTP
from ftplib import FTP_TLS
import ntpath

with open('parameters.txt', 'r') as fp:
    dparameters = json.load(fp)

url = dparameters["url"]
rangefrom = dparameters["rangefrom"]
rangeto = dparameters["rangeto"]
dir_in = dparameters["dir_in"]
dir_downloads = dparameters["dir_downloads"]
dir_pdfs = dparameters["dir_pdfs"]
fileshortnames = dparameters["fileshortnames"]
sheetShortName = dparameters["sheetShortName"]
headlessMode = dparameters["headlessMode"]

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

# if log file become large, you can change filemode='w' for logging only individual sessons
logging.basicConfig(filename=dir_in + 'transfer_pdfs.log', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

logging.debug('Started')

time1 = time.time()

def download():
    ''' function for downloading zip files from server'''
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
        time.sleep(dparameters["sleeptime"])
        while True:
            l = glob.glob(dir_downloads + '*.part')
            if len(l) == 0:
                # print'Downloading ' + audit + ' completed')
                break
            else:
                time.sleep(dparameters["sleeptime"])

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

def ftp_upload_pdfs():
    ''' function for uploading pdf files to FTP server '''
    # get a list of pdf files in dir_pdfs
    lpdfs = glob.glob(dir_pdfs + "*.pdf")
    lpdfs.sort()
    os.chdir(dir_pdfs) # needed for ftp.storbinary('STOR command work not with paths but with filenames
    
    # connect to FTP server and upload files
    try:
        ftp = FTP()
        # ftp = FTP_TLS()
        ftp.connect(dparameters["server"].strip(), dparameters["port"])
        ftp.login(user = dparameters["username"].strip(), passwd = dparameters["password"].strip())
        # ftp.prot_p() if using FTP_TLS uncomment this line
        print("Connection to ftp successfully established...")
        #ftp.cwd('path_to_destination_directory_if_needed_on_server')
        for pdffile in lpdfs:
            rpdffile = ntpath.basename(pdffile)
            print('uploading ' + rpdffile)
            logging.info('uploading ' + rpdffile)
            ffile = open(pdffile, 'rb')
            ftp.storbinary('STOR ' + rpdffile, ffile)
            ffile.close()
            # file uploaded delete it now
            os.remove(pdffile)
        ftp.quit()
    except Exception as e:
        print(str(e))
        logging.critical(str(e))

def extract_and_rename():
    ''' function for extracting zip files and renaming pdf files'''
    print('Extracting files..')
    lloc = glob.glob(dir_downloads + '*.zip')
    lloc.sort()
    
    if len(lloc) == 0:
        print('no zip file(s). quiting')
        logging.info('no zip file(s). quiting')
    
    # placing shortnames in dictionary
    wbShort = openpyxl.load_workbook(dir_in + fileshortnames.strip())
    sheetShort = wbShort.get_sheet_by_name(sheetShortName.strip())
    dshort = {}
    row = 2
    scrolldown = True
    while scrolldown:
        dshort[sheetShort['A' + str(row)].value.strip()] = sheetShort['D' + str(row)].value.strip()
        row += 1
        if sheetShort['A' + str(row)].value == None:
            scrolldown = False # when finding empty row parsing of Shortnames xlsx will stop
    
    for myzipfile in lloc:
        with zipfile.ZipFile(myzipfile, "r") as z:
            z.extractall(dir_pdfs)
        # here comes part for renaming
        print('Renaming files..')
        wbCross = openpyxl.load_workbook(dir_pdfs + 'FileNameCrossReferenceList.xlsx')
        sheetCross = wbCross.get_sheet_by_name('Table1')
        for zrow in range(99):
            row = zrow + 2
            if sheetCross['A' + str(row)].value == None: 
                break
            lfilename = sheetCross['B' + str(row)].value.strip()
            lauditeename = sheetCross['C' + str(row)].value.strip()
            lstate = sheetCross['E' + str(row)].value.strip()
            lein = sheetCross['F' + str(row)].value.strip()
            lyearending = sheetCross['G' + str(row)].value.split('/')[-1].strip()
            # try to find short output name
            # in case there is in lshortname will be appended shortened name else original auditee name
            lname = dshort.get(sheetCross['F' + str(row)].value.strip(), sheetCross['C' + str(row)].value.strip())
            
            # filterling lname from special characters
            lname = lname.replace('/', '_')
            lname = lname.replace(':', '_')
            lname = lname.replace('\\', '')
            lname = lname.replace("'", "_")
            lname = lname.replace('"', '_')
            lname = lname.replace(',', '')
            lname = lname.replace('&', '')
            lname = lname.replace('.', '')
            lname = lname.replace('#', '')
            lname = lname.replace('%', '')
            lname = lname.replace('{', '')
            lname = lname.replace('}', '')
            lname = lname.replace('<', '')
            lname = lname.replace('>', '')
            lname = lname.replace('*', '')
            lname = lname.replace('?', '')
            lname = lname.replace('$', '')
            lname = lname.replace('!', '')
            lname = lname.replace('@', '')
            lname = lname.replace('+', '')
            lname = lname.replace('`', '')
            lname = lname.replace('|', '')
            lname = lname.replace('=', '')
            
            try:
                os.rename(dir_pdfs + lfilename + '.pdf', dir_pdfs + lstate + ' ' + lname + ' ' + lyearending + '.pdf')
                time.sleep(0.3)
            except Exception as e:
                print(str(e))
                logging.debug(str(e))
            
            print((lfilename + '.pdf').ljust(20) + lname + '.pdf')
            logging.info((lfilename + '.pdf').ljust(20) + lname + '.pdf')

        # sleep for system to affect rename command for all files
        time.sleep(dparameters["sleeptime"])
        ftp_upload_pdfs()
        os.remove(myzipfile)
 
def calculate_time():
    time2 = time.time()
    hours = int((time2-time1)/3600)
    minutes = int((time2-time1 - hours * 3600)/60)
    sec = time2 - time1 - hours * 3600 - minutes * 60
    print("processed in %dh:%dm:%ds" % (hours, minutes, sec))    

if __name__ == '__main__':
    download()
    extract_and_rename() # since FileNameCrossReferenceList.xlsx is same for all groups, 
                         # script have to use this grouped approaching, processing them by 100 or less for final group
    calculate_time()
    print('Done.')
