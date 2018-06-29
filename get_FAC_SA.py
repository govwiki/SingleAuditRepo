# -*- coding: utf-8 -*-

#! /usr/bin/env python3.6
# Seraphina Anderson

import datetime
import time
import html
import re
import os
import sys
import codecs
import ntpath
import logging
import zipfile
import glob
import openpyxl
import json
import argparse
import configparser
import ntpath
from datetime import timedelta
from ftplib import FTP
from ftplib import FTP_TLS
from datetime import date
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from azure.storage.file import FileService, ContentSettings
from utils import DbCommunicator as db
from datetime import datetime

#parse command line args
rangefrom = ""
rangeto = ""
if len(sys.argv)>=3:
    date_from = sys.argv[1] 
    date_to = sys.argv[2]
    date_pattern = re.compile(r"\d\d/\d\d/\d\d\d\d")
    if (date_pattern.match(date_from) and date_pattern.match(date_to)):
        rangefrom = date_from
        rangeto = date_to

#collect data for logs
start_time = datetime.utcnow()

#read config from db
script_name = "get_FAC_SA.py"
config = configparser.ConfigParser()
config.read('conf.ini')
db = db(config)
dparameters = {}
try:
    dparameters = db.readProps('fac')
finally:
    db.close()

result = 1
config_file = str(dparameters)
error_message = ""

#with open('FAC_parms.txt', 'r') as fp: 
#    dparameters = json.load(fp)


global general_purpose
global school_district
global community_college_district
global special_district
global non_profit
global miscellaneous

general_purpose = r"General Purpose"
school_district = r"School District"
public_higher_education = r"Public Higher Education"
community_college_district = r"Community College District"
special_district = r"Special District"
non_profit = r"Non-Profit"
unclassified = r"Unclassified"


url = dparameters["url"]
if rangefrom == "":
    rangefrom = dparameters["rangefrom"]
if rangefrom == "99/99/9999":
    prevdaystr = str(date.today() - timedelta(days=2))
    rangefrom = prevdaystr[5:7] + "/" + prevdaystr[8:10] + "/" + prevdaystr[0:4]
if rangeto == "":
    rangeto = dparameters["rangeto"]
if rangeto == "99/99/9999":
    todaystr = str(date.today())
    rangeto = todaystr[5:7] + "/" + todaystr[8:10] + "/" + todaystr[0:4]
PATH = dparameters["path_to_script"]
path_to_chromedriver = dparameters["path_to_chromedriver"]
operating_system = dparameters["operating_system"]
dir_in = dparameters["dir_in"]
dir_downloads = dparameters["dir_downloads"]
dir_upload = dparameters["dir_upload"]
dir_pdfs = dparameters["dir_pdfs"]
headlessMode = int(dparameters["headlessMode"])
todownload = int(dparameters["todownload"])
sleeptime = int(dparameters["sleeptime"])
usemarionette = int(dparameters["usemarionette"])

#make dirs
os.makedirs(dir_in,exist_ok=True)
os.makedirs(dir_downloads,exist_ok=True)
os.makedirs(dir_upload,exist_ok=True)
os.makedirs(dir_pdfs,exist_ok=True)
os.makedirs(PATH,exist_ok=True)


os.environ["PATH"] += ":/data/Scrape"

timeout = 10        # timeout for openning web page

if headlessMode:
    display = Display(visible=0, size=(1024, 768))
    display.start()

# if log file become large, you can change filemode='w' for logging only individual sessons
os.makedirs(dir_in, exist_ok = True)
logging.basicConfig(filename=dir_in + 'get_FAClog.txt', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

logging.debug('Started')

time1 = time.time()
ddestdir = {}
ddestdiropp = {}

def is_download_completed():
    time.sleep(sleeptime)
    l = glob.glob(dir_downloads + '*.crdownload')
    while True:
        l = glob.glob(dir_downloads + '*.crdownload')
        if len(l) == 0:
            break
        else:
            time.sleep(sleeptime)

def download():
    os.makedirs(dir_downloads, exist_ok = True)
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
    
    options = webdriver.ChromeOptions() 
    options.add_argument("--start-maximized")
    prefs = {
            'download.default_directory': dir_downloads,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'plugins.always_open_pdf_externally': True,
        }
    options.add_experimental_option("prefs",prefs)

    capabilities = DesiredCapabilities.CHROME
        
    if usemarionette:
        capabilities["marionette"] = True

    driver = webdriver.Chrome(executable_path= path_to_chromedriver, chrome_options=options)
    #driver = webdriver.Chrome(chrome_options=options)
    
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
    time.sleep(0.5)

    # unselect All Years
    open_tag('#MainContent_UcSearchFilters_FYear_CheckableItems_0')
    # click on 2016
    open_tag('#MainContent_UcSearchFilters_FYear_CheckableItems_1')
    # click on 2017
    open_tag('#MainContent_UcSearchFilters_FYear_CheckableItems_2')
    # Fill ranges
    enter_in_tag('#MainContent_UcSearchFilters_DateProcessedControl_FromDate', rangefrom) #rangefrom
    enter_in_tag('#MainContent_UcSearchFilters_DateProcessedControl_ToDate', rangeto) #rangeto
    print(rangefrom + ' ' + rangeto)
    # click on Search button
    open_tag('#MainContent_UcSearchFilters_btnSearch_top')
    
    # click through new PII and Native Tribe information disclosure screen added April 2017
    open_tag("#chkAgree")
    open_tag("#btnIAgree")
    
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
    time.sleep(2)

    if bnum:
        # in this for loop we are selecting by groups of 100
        for audit in laudit:
            del audit_reports_select
            audit_reports_select = Select(driver.find_element_by_css_selector('#MainContent_ucA133SearchResults_ddlAvailZipTop'))
            audit_reports_select.select_by_visible_text(audit)
            # now we click on Download Audits button
            open_tag('#MainContent_ucA133SearchResults_btnDownloadZipTop')
            print('Downloading ' + audit)
            is_download_completed()
    # download summary report
    open_tag('#MainContent_ucA133SearchResults_lnkDownloadSummary')
    print('Downloading Summary Report')
    is_download_completed()

    driver.close()
    if headlessMode:
        display.stop()

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

def get_pdfs():
    global PATH
    global pdfs
    if operating_system == 'linux' or operating_system == 'mac':
        pdfs = os.listdir(PATH + "PDFS/")
    elif operating_system == 'windows':
        pdfs = os.listdir(PATH + "PDFS\\")
    return PATH, pdfs

def process_summary_report():
    global refs
    open_summary = openpyxl.load_workbook(dir_upload+'Summary_Reports.xlsx', data_only=True)
    general_info = open_summary['GENERAL INFO']
    col_b = general_info['B'][1:]
    col_c = general_info['C'][1:] 
    col_h = general_info['H'][1:] 

    refs = {}

    for i, e in enumerate(col_b):
        item = {}
        item['DBkey'] = col_b[i].value
        item['entity_code'] = col_c[i].value
        item['EIN'] = col_h[i].value
        record = item
        refs['item_' + str(i)] = record

    return refs

def process_cross_ref_file():
    global cross_items

    crossref = openpyxl.load_workbook(dir_pdfs + 'FileNameCrossReferenceList.xlsx', data_only=True)
    crossref_sheet = crossref['Table1']

    filename = crossref_sheet['B'][1:] 
    auditeename = crossref_sheet['C'][1:]
    city = crossref_sheet['D'][1:]
    state = crossref_sheet['E'][1:]
    ein = crossref_sheet['F'][1:]
    yearending = crossref_sheet['G'][1:]

    cross_items = {}

    for j, file in enumerate(filename):
        item = {}
        item['file_name'] = filename[j].value
        dbkey = re.match('(\d+)20\d{2}\d*',filename[j].value).group(1)
        item['dbkey'] = dbkey
        item['auditeename'] = auditeename[j].value
        item['city'] = city[j].value
        item['state'] = state[j].value
        item['ein'] = ein[j].value
        item['yearending'] = yearending[j].value
        record = item
        cross_items['cross_item_' + str(j)] = record

    return cross_items


def classify_doc():

    global classify_file
    global classify_general
    global general
    global states
    global codes

    get_pdfs()
    process_summary_report()
    process_cross_ref_file()

    classify = {'general_purpose': ['000', '100', '200', '300', '710', '700'], 'school_district': ['005', '105', '205', '305', '505', '605', '705', '715'], 'public_higher_education': ['004', '104', '204', '304', '504', '604', '704', '714', '904'], 'special_district': ['001', '002', '003', '006', '007', '009', '101', '102', '103', '106', '107', '109', '201', '202', '203', '206', '207', '209', '301', '302', '303', '306', '307', '309', '401', '402', '403', '406', '407', '409', '600', '602', '603', '606', '607', '609', '701', '702', '703', '706', '707', '709', '711', '712', '713', '716', '717', '719'], 'non_profit': ['901', '902', '903', '905', '906', '907', '908', '909'], 'unclassified': ['808', '888']}
    states = [['AL', 'Alabama'], ['AK', 'Alaska'], ['AS', 'America Samoa'], ['AZ', 'Arizona'], ['AR', 'Arkansas'], ['CA', 'California'], ['CO', 'Colorado'], ['CT', 'Connecticut'], ['DE', 'Delaware'], ['DC', 'District of Columbia'], ['FM', 'Micronesia1'], ['FL', 'Florida'], ['GA', 'Georgia'], ['GU', 'Guam'], ['HI', 'Hawaii'], ['ID', 'Idaho'], ['IL', 'Illinois'], ['IN', 'Indiana'], ['IA', 'Iowa'], ['KS', 'Kansas'], ['KY', 'Kentucky'], ['LA', 'Louisiana'], ['ME', 'Maine'], ['MH', 'Islands1'], ['MD', 'Maryland'], ['MA', 'Massachusetts'], ['MI', 'Michigan'], ['MN', 'Minnesota'], ['MS', 'Mississippi'], ['MO', 'Missouri'], ['MT', 'Montana'], ['NE', 'Nebraska'], ['NV', 'Nevada'], ['NH', 'New Hampshire'], ['NJ', 'New Jersey'], ['NM', 'New Mexico'], ['NY', 'New York'], ['NC', 'North Carolina'], ['ND', 'North Dakota'], ['OH', 'Ohio'], ['OK', 'Oklahoma'], ['OR', 'Oregon'], ['PW', 'Palau'], ['PA', 'Pennsylvania'], ['PR', 'Puerto Rico'], ['RI', 'Rhode Island'], ['SC', 'South Carolina'], ['SD', 'South Dakota'], ['TN', 'Tennessee'], ['TX', 'Texas'], ['UT', 'Utah'], ['VT', 'Vermont'], ['VI', 'Virgin Island'], ['VA', 'Virginia'], ['WA', 'Washington'], ['WV', 'West Virginia'], ['WI', 'Wisconsin'], ['WY', 'Wyoming']]
    codes = ['AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FM', 'FL', 'GA', 'GU', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MH', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PW', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VI', 'VA', 'WA', 'WV', 'WI', 'WY']

    classify_file = {}

    for k, record in enumerate(cross_items):
        dbkey = int(cross_items[record]['dbkey'])
        part_1 = next((refs[item] for item in refs if refs[item]['DBkey'] == dbkey), None)
        part_2 = cross_items[record]
        part_2.update(part_1)
        del part_2['DBkey']
        del part_2['EIN']
        entity_code = part_2['entity_code']
        folder = [e for e in classify if entity_code in classify[e]][0]
        part_2['folder'] = folder
        classify_file['record_' + str(k)] = part_2


    classify_general = [['State', 'State-Wide', '000'], ['County', 'County-General Purpose Government', '100'], ['Municipality', 'Municipality-General Purpose Government', '200'], ['Township', 'Township-General Purpose Government', '300'], ['Territory Local', 'Territory Local General Purpose Government', '710'], ['Territory', 'Territory-Wide', '700']]
    general = ['000', '100', '200', '300', '710', '700']

    return classify_file, classify_general, general, states

def rename_and_move_files():
    classify_doc()
    for pdf in pdfs:
        if re.match('(\d+)(?:19|20)\d{2}\d*\.pdf', pdf):
            file_key = re.match('(\d+)(?:19|20)\d{2}\d*\.pdf', pdf).group(1)
            file_folder = [classify_file['record_' + str(i)]['folder'] for i, rec in enumerate(classify_file) if classify_file['record_' + str(i)]['dbkey'] == file_key]
            pdf_record = [classify_file['record_' + str(i)] for i, rec in enumerate(classify_file) if classify_file['record_' + str(i)]['dbkey'] == file_key]
            def move_to_folder():
                
                dest_filename = dir_upload
                
                if file_folder == 'general_purpose':
                    dest_filename += general_purpose
                elif file_folder == 'school_district':
                    dest_filename += school_district
                elif file_folder == 'public_higher_education':
                    dest_filename += public_higher_education
                elif file_folder == 'special_district':
                    dest_filename += special_district
                elif file_folder == 'non_profit':
                    dest_filename += non_profit
                elif file_folder == 'unclassified':
                    dest_filename += unclassified
                elif re.match('.*community\s*college.*', auditeename, re.IGNORECASE):
                    dest_filename += community_college_district

                # test for operating system
                if operating_system == 'mac' or operating_system == 'linux':
                    dest_filename += '/' + year + '/'
                elif operating_system == 'windows':
                    dest_filename += '\\' + year + '\\'
                
                os.makedirs(dest_filename, exist_ok = True)    
                
                dest_filename += pdf_name
                print(dest_filename)
                try:
                    os.rename(dir_pdfs + pdf, dest_filename)
                except Exception as e:
                    print(e)                

            if file_folder != []:
                file_folder = file_folder[0]
                pdf_record = pdf_record[0]
                year = re.match('.*\/((?:19|20)\d{2})', pdf_record['yearending']).group(1)
                if file_key in general:
                    if file_key == '100':
                        pdf_name = pdf_record['state'] + ' ' + pdf_record['city'] + ' ' + 'County' + ' ' + year + '.pdf'
                        move_to_folder()
                    elif file_key == '200':
                        pdf_name = pdf_record['state'] + ' ' + pdf_record['city'] + ' ' + 'County' + ' ' + year + '.pdf'
                        move_to_folder()
                    elif file_key == '300':
                        pdf_name = pdf_record['state'] + ' ' + pdf_record['city'] + ' ' + 'Township' + ' ' + year + '.pdf'
                        move_to_folder()
                    elif re.match('.*financial.*', pdf_name, re.IGNORECASE):
                        num = codes.index(pdf_record['state'])
                        full_name = states[num]
                        pdf_name = pdf_record['state'] + ' ' + 'State of ' + full_name + ' ' + year + '.pdf'
                    else:
                        auditeename = pdf_record['auditeename'].replace('/', '-')
                        
                        # further testing here
                        if 'CITY OF ' in auditeename:
                            auditeename = auditeename.replace('CITY OF ', '')
                        elif 'MUNICIPALITY OF ' in auditeename:
                            auditeename = auditeename.replace('MUNICIPALITY OF ', '')
                        elif 'MUNICIPIOS OF ' in auditeename:
                            auditeename = auditeename.replace('MUNICIPIOS OF ', '')
                        elif 'VILLAGE OF ' in auditeename:
                            auditeename = auditeename.replace('VILLAGE OF ', '')
                        elif 'TOWN OF ' in auditeename:
                            auditeename = auditeename.replace('TOWN OF ', '')

                        if re.match('.*(,.*)', auditeename):
                            auditeename = auditeename.replace(re.match('.*(,.*)', auditeename).group(1), '')
                        auditeename = auditeename.title()

                        pdf_name = pdf_record['state'] + ' ' + auditeename + ' ' + year + '.pdf'
                        move_to_folder()
                else:
                    auditeename = pdf_record['auditeename'].replace('/', '-')

                    # further testing here
                    if 'CITY OF ' in auditeename:
                        auditeename = auditeename.replace('CITY OF ', '')
                    elif 'MUNICIPALITY OF ' in auditeename:
                        auditeename = auditeename.replace('MUNICIPALITY OF ', '')
                    elif 'MUNICIPIOS OF ' in auditeename:
                        auditeename = auditeename.replace('MUNICIPIOS OF ', '')
                    elif 'VILLAGE OF ' in auditeename:
                        auditeename = auditeename.replace('VILLAGE OF ', '')
                    elif 'TOWN OF ' in auditeename:
                        auditeename = auditeename.replace('TOWN OF ', '')

                    if re.match('.*(,.*)', auditeename):
                        auditeename = auditeename.replace(re.match('.*(,.*)', auditeename).group(1), '')
                    auditeename = auditeename.title()
                        
                    pdf_name = pdf_record['state'] + ' ' + auditeename + ' ' + year + '.pdf'
                    move_to_folder()
        else:
            continue

def extract_and_rename():

    # process summary data
    loc_summary = glob.glob(dir_downloads + 'Summary_Reports.xlsx')

    # move file to current directory
    os.makedirs(dir_upload, exist_ok = True)
    try:
        os.rename(dir_downloads + 'Summary_Reports.xlsx', dir_upload + 'Summary_Reports.xlsx')
    except Exception as e:
        print(e)

    print("Extracting zip...")

    # get zip files
    lloc = glob.glob(dir_downloads + '*.zip')
    lloc.sort()

    if len(lloc) == 0:
        print('no zip file(s). quiting')
        logging.info('no zip file(s). quiting')

    for myzipfile in lloc:
        print('----------------------------------------------------------------')
        print('Extracting ' + myzipfile)
        with zipfile.ZipFile(myzipfile, "r") as z:
            z.extractall(dir_pdfs)
        rename_and_move_files()

        time.sleep(10)
        os.remove(myzipfile)
    os.remove(dir_upload + 'Summary_Reports.xlsx')

def calculate_time():
    time2 = time.time()
    hours = int((time2-time1)/3600)
    minutes = int((time2-time1 - hours * 3600)/60)
    sec = time2 - time1 - hours * 3600 - minutes * 60
    print("processed in %dh:%dm:%ds" % (hours, minutes, sec))

#######    
# a function to upload files to Azure services
def upload_to_file_storage():
    # get a list of pdf files in dir_pdfs
    template = dir_upload + "**"
    if operating_system == 'mac' or operating_system == 'linux':
        template += '/*.pdf'
    elif operating_system == 'windows':
        template += '\\*.pdf'
    lpdfs = glob.glob(template, recursive = True)
    lpdfs.sort()
    #os.chdir(dir_pdfs) # needed for ftp.storbinary('STOR command work not with paths but with filenames
    # connect to FTP server and upload files
    try:
        file_storage_url = dparameters['fs_server'].strip()
        file_storage_user = dparameters['fs_username'].strip()
        file_storage_pwd = dparameters['fs_password'].strip()
        file_storage_share = dparameters['fs_share'].strip()
        file_storage_dir = dparameters['fs_directory_prefix'].strip()
        file_service = FileService(account_name=file_storage_user, account_key=file_storage_pwd) 
        try:
            if file_service.exists(file_storage_share):
                print('Connection to Azure file storage successfully established...')
                if len(file_storage_dir)>0 and not file_service.exists(file_storage_share, directory_name=file_storage_dir):
                    file_service.create_directory(file_storage_share, file_storage_dir)
                    print('Created directory:' + file_storage_dir)
            else:
                print('Failed to connect to Asure file storage, share does not exist: '+ file_storage_share)
        except Exception as ex:
            print('Error connecting to Azure file storage: ', ex)
        
        for pdffile in lpdfs:
            dir, rpdffile = ntpath.split(pdffile)
            
            destinationdir = ''
            
            if (dir + '\\') == dir_upload or (dir + '/')== dir_upload:
                destinationdir ='Unclassified'
            else:
                dir, year = ntpath.split(dir)
                dir, destinationdir = ntpath.split(dir) 
            
            retries = 0
            while retries<3:
                try:
                    path = pdffile
                    print('Uploading {}'.format(path))
                    filename = pdffile
                    remote_filename = rpdffile
                    if not remote_filename:
                        return
                    if len(file_storage_dir)>0:
                        directory = file_storage_dir+'/'+destinationdir
                    else:
                        directory = destinationdir
                    if not file_service.exists(file_storage_share,directory_name=directory):
                        file_service.create_directory(file_storage_share,directory)
                    directory += '/' + year
                    if not file_service.exists(file_storage_share,directory_name=directory):
                        file_service.create_directory(file_storage_share,directory)
                    print('Checking if {}/{} already exists'.format(directory, remote_filename))
                    if file_service.exists(file_storage_share,directory_name=directory, file_name=remote_filename):
                        print('{}/{} already exists'.format(directory, remote_filename))
                        break
                    file_service.create_file_from_path(
                        file_storage_share,
                        directory,
                        remote_filename,
                        path,
                        content_settings=ContentSettings(content_type='application/pdf'))    
                    print('{} uploaded'.format(path))
                    retries =3
                except Exception as e:
                    print('Error uploading to Asure file storage,', str(e))
                    retries+=1
    except Exception as e:
        print(str(e))
        logging.critical(str(e))
######

if __name__ == '__main__':
    try:
        if todownload:
            download()
        extract_and_rename()
        calculate_time()
        upload_to_file_storage()
        print('Done.')
    except Exception as e:
        result = 0
        error_message = str(e)
    end_time = datetime.utcnow()
    
    try:
        db.connect()
        db.log(script_name, start_time, end_time, config_file, result, error_message)
    finally:
        db.close()
    