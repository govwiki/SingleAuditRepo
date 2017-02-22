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
    
dir_in = dparameters["dir_in"]
dir_downloads = dparameters["dir_downloads"]
dir_pdfs = dparameters["dir_pdfs"]
fileshortnames = dparameters["fileshortnames"]
sheetShortName = dparameters["sheetShortName"]

logging.basicConfig(filename=dir_in + 'transfer_pdfs.log', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

time1 = time.time()

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

def rename_files():
    ''' function for renaming pdf files, no extract from zip'''
    
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
    
    # here comes part for renaming
    print('Renaming files..')
    wbCross = openpyxl.load_workbook(dir_pdfs + 'FileNameCrossReferenceList.xlsx')
    sheetCross = wbCross.get_sheet_by_name('Table1')
    zrow = -1
    while True:
        zrow += 1
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
            if os.path.exists(dir_pdfs + lfilename + '.pdf'):
                os.rename(dir_pdfs + lfilename + '.pdf', dir_pdfs + lstate + ' ' + lname + ' ' + lyearending + '.pdf')
                print((lfilename + '.pdf').ljust(20) + lname + '.pdf')
                logging.info((lfilename + '.pdf').ljust(20) + lname + '.pdf')
                time.sleep(0.1)
        except Exception as e:
            print(str(e))
            logging.debug(str(e))
        
    ftp_upload_pdfs()
 
def calculate_time():
    time2 = time.time()
    hours = int((time2-time1)/3600)
    minutes = int((time2-time1 - hours * 3600)/60)
    sec = time2 - time1 - hours * 3600 - minutes * 60
    print("processed in %dh:%dm:%ds" % (hours, minutes, sec))    

if __name__ == '__main__':
    rename_files()
    calculate_time()
    print('Done.')
