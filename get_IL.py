#! /usr/bin/env python3.6
# Script for downloading pdf Illinois files from public ftp, merging in one if more pdf files in subdirectory
# then renaming files (and eventually uploading via FTP)
# Aleksandar Josifoski https://about.me/josifsk
# Script is dependend on openpyxl, pdftk
# pip install -U openpyxl
# pdftk is used for merging (if more then one) pdf files
# on linux it can be installed sudo apt install pdftk
# on windows https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/pdftk_free-2.02-win-setup.exe
# pdftk.exe must be startable in dir_pdfs, ie. placed in system path
# testing example in dir_pdfs via terminal on windows pdftk.exe file1.pdf file2.pdf cat output newfile.pdf
# 2017 February 22

import datetime
import time
import os
import sys
import ntpath
import logging
import glob
import openpyxl
import json
import ftplib
from ftplib import FTP
from ftplib import FTP_TLS
import ntpath
import urllib
import posixpath
import platform

with open('illinois_parameters.txt', 'r') as fp:
    dparameters = json.load(fp)

ftpurl = dparameters["ftpurl"]
url = urllib.parse.urlparse(ftpurl)
start_from = dparameters["start_from"]
year = dparameters["year"]
dir_in = dparameters["dir_in"]
dir_pdfs = dparameters["dir_pdfs"]
illinois_entities_xlsx_file = dparameters["illinois_entities_xlsx_file"]
illinois_entities_sheet = dparameters["illinois_entities_sheet"]


# if log file become large, you can change filemode='w' for logging only individual sessons
logging.basicConfig(filename=dir_in + 'get_ILlog.txt', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

logging.debug('Started')

time1 = time.time()
os.chdir(dir_pdfs)

def ftp_dir(ftp):
    """
    Given a valid ftp connection, get a list of 2-tuples of the
    files in the ftp current working directory, where the first
    element is whether the file is a directory and the second 
    element is the filename.
    """
    # use a callback to grab the ftp.dir() output in a list
    dir_listing = []
    ftp.dir(lambda x: dir_listing.append(x))
    return [(line[0].upper() == 'D', line.rsplit()[-1]) for line in dir_listing]

def main():
    ''' connect to public ftp function '''
    ftp = ftplib.FTP(url.netloc)
    ftp.login()
    print('login to ' + url.netloc)
    logging.info('login to ' + url.netloc)
    stack = [url.path]
    path = stack.pop()
    ftp.cwd(path)

    # add all directories to the queue
    children = ftp_dir(ftp)
    dirs = [posixpath.join(path, child[1]) for child in children if not child[0]]
    # set start_from directory
    while True:
        itemdir = dirs[0]
        if itemdir.split('/')[-1] != start_from.strip():
            del dirs[0]
        else:
            break
    
    # put values from Illinois Entities.xlsx in dictionary
    print('Creating connection with ' + illinois_entities_xlsx_file)
    wbShort = openpyxl.load_workbook(dir_in + illinois_entities_xlsx_file.strip())
    sheetShort = wbShort.get_sheet_by_name(illinois_entities_sheet.strip())
    dshort = {}
    row = 2
    scrolldown = True

    while scrolldown:
        key = str(sheetShort['A' + str(row)].value)
        if len(key) == 6:
            key = '00' + key
        elif len(key) == 7:
            key = '0' + key
        dshort[key] = sheetShort['B' + str(row)].value.strip()
            
        row += 1
        if sheetShort['A' + str(row)].value == None:
            scrolldown = False # when finding empty row parsing of Shortnames xlsx will stop    
    
    for udir in dirs:
        print('-' * 20)
        logging.info('-' * 20)
        print(udir)
        logging.info(udir)
        # example of path structure /LocGovAudits/FY2015/00100000
        parseddir = udir.split('/')[-1].strip()
        try:
            preparename = 'IL ' + dshort[parseddir] + ' ' + year + '.pdf'
        except:
            preparename = parseddir + '.pdf'
        preparename = preparename.replace('/', '')
        preparename = preparename.replace(':', '')
        
        ftp.cwd(udir)
        time.sleep(0.8)
        files = []
        
        try:
            files = ftp.nlst()
            files.sort()
        except Exception as e:
            if str(e) == "550 No files found":
                print("No files in this directory")
                logging.info(udir + " No files in this directory")
            else:
                print(str(e))
                logging.info(udir + ' ' + str(e))
        
        for f in files:
            with open(dir_pdfs + f, 'wb') as fobj:
                ftp.retrbinary('RETR %s' % f, fobj.write)
                print('downloading ' + f)
                logging.info('downloading ' + f)
                
        # if more then one pdf in ftp directory merge them
        if len(files) > 1:
            pdfline = ' '.join(files)
            if platform.system() == "Linux":
                command = 'pdftk ' + pdfline + ' cat output temp.pdf'
            if platform.system() == "Windows":
                command = 'pdftk.exe ' + pdfline + ' cat output temp.pdf'
            try:
                os.system(command)
                os.rename('temp.pdf', preparename)
                print(preparename + ' generated')
                logging.info(preparename + ' generated')
                bOK = True
            except Exception as e:
                print(udir + ' ' + pdfline + ' not generated pdf')
                print(str(e))
                logging.info(udir + ' ' + pdfline + ' not generated pdf')
                logging.info(str(e))
                bOK = False
        else:
            # check is there only one pdf file
            if len(files) == 1:
                try:
                    os.rename(dir_pdfs + files[0].strip(), dir_pdfs + preparename)
                except Exception as e:
                    logging.info(str(e))
                    print(str(e))
                print(preparename + ' generated')
                logging.info(preparename + ' generated')
            else:
                print('no files in ' + udir)
                logging.info('no files in ' + udir) #this most probably will never occure
        
        # delete original pdf files if more then one, since if one only, with renaming it is deleted
        if len(files) > 1 and bOK:
            for f in files:
                os.remove(dir_pdfs + str(f).strip())

def ftp_upload_pdfs():
    ''' function for uploading pdf files to FTP server 
    Since they can be over 10000, it's recommended to not use this function
    but to use some strategical method via filezilla'''
    # get a list of pdf files in dir_pdfs
    lpdfs = glob.glob(dir_pdfs + "*.pdf")
    lpdfs.sort()
    os.chdir(dir_pdfs) # needed for ftp.storbinary('STOR command work not with paths but with filenames
    
    # connect to FTP server and upload files
    try:
        ftpup = FTP()
        # ftpup = FTP_TLS()
        ftpup.connect(dparameters["server"].strip(), dparameters["port"])
        ftpup.login(user = dparameters["username"].strip(), passwd = dparameters["password"].strip())
        # ftpup.prot_p() if using FTP_TLS uncomment this line
        print("Connection to ftp successfully established...")
        #ftpup.cwd('path_to_destination_directory_if_needed_on_server')
        for pdffile in lpdfs:

            rpdffile = ntpath.basename(pdffile)
            print('uploading ' + rpdffile)
            logging.info('uploading ' + rpdffile)
            ffile = open(pdffile, 'rb')
            ftpup.storbinary('STOR ' + rpdffile, ffile)
            ffile.close()
            # file uploaded delete it now
            # os.remove(pdffile)

        ftp.quit()
    except Exception as e:
        print(str(e))
        logging.critical(str(e))
        
def calculate_time():
    time2 = time.time()
    hours = int((time2-time1)/3600)
    minutes = int((time2-time1 - hours * 3600)/60)
    sec = time2 - time1 - hours * 3600 - minutes * 60
    print("processed in %dh:%dm:%ds" % (hours, minutes, sec))    

if __name__ == '__main__':
    main()
    calculate_time()
    print('Done.')
