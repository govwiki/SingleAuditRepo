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

from datetime import datetime
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
import configparser
from utils import DbCommunicator as db
from utils import FilenameManager
from azure.storage.file import FileService, ContentSettings

global db
global dbparameters
global file_service
global file_storage_dir
global file_storage_share
global overwrite_remote_files
global ftpurl
global url
global start_from
global year
global dir_in
global dir_pdfs
global illinois_entities_xlsx_file
global illinois_entities_sheet

start_time = datetime.utcnow()
script_name = "get_IL.py"
result = 1
error_message = ""

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

def getGategory(entity):
    if not entity:
        return r"Unclassified"
    if entity == "City" or entity == "County" or entity == "Town" or entity == "Township" or entity == "Village":
        return r"General Purpose"
    if entity == "School District":
        return r"School District"
    if entity == "Community College":
        return r"Community College District"
    else:
        return r"Special District"

def main():
    file_storage_connect()
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
    excel_name = {}
    excel_category = {}
    row = 2
    scrolldown = True

    while scrolldown:
        key = str(sheetShort['A' + str(row)].value)
        if len(key) == 6:
            key = '00' + key
        elif len(key) == 7:
            key = '0' + key
        excel_name[key] = sheetShort['B' + str(row)].value.strip()
        excel_category[key] = getGategory(sheetShort['J' + str(row)].value.strip())
            
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
            preparename = 'IL@#' + excel_category[parseddir] + '@#' + excel_name[parseddir] + '@#' + year + '.pdf'
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
        file_details = db.readFileStatus(file_original_name=preparename)
        if file_details is None:
            file_details = db.saveFileStatus(file_original_name=preparename, file_status = 'Downloaded')
        upload_to_file_storage(preparename)

def file_storage_connect():
    global file_service
    global file_storage_dir
    global file_storage_share
    global overwrite_remote_files
    file_storage_url = dbparameters['fs_server'].strip()
    file_storage_user = dbparameters['fs_username'].strip()
    file_storage_pwd = dbparameters['fs_password'].strip()
    file_storage_share = dbparameters['fs_share'].strip()
    file_storage_dir = dbparameters['fs_directory_prefix'].strip()
    overwrite_remote_files = dbparameters['overwrite_remote_files'].strip()
    file_service = FileService(account_name=file_storage_user, account_key=file_storage_pwd) 
    try:
        if file_service.exists(file_storage_share):
            print('Connection to Azure file storage successfully established...')
            if len(file_storage_dir) > 0 and not file_service.exists(file_storage_share, directory_name=file_storage_dir):
                subdirs = file_storage_dir.split('/')
                subdirfull=""
                for subdir in subdirs:
                    subdirfull+=subdir
                    file_service.create_directory(file_storage_share, subdirfull)
                    subdirfull+="/"
                print('Created directory:' + file_storage_dir)
        else:
            print('Filaed to connect to Asure file storage, share does not exist: ' + file_storage_share)
    except Exception as ex:
        print('Error connecting to Azure file storage: ', ex)

def _get_remote_filename(local_filename):
        abbr, directory, entity_name, year = local_filename[:-4].split('@#')
        filename = '{} {} {}.pdf'.format(abbr, entity_name, year)
        return directory, filename, year

def upload_to_file_storage(filename):
    old_filename = filename
    downloads_path = dir_pdfs
    fnm = FilenameManager()
    retries = 0
    while retries < 3:
        try:
            path = os.path.join(downloads_path, old_filename)
            file_details = db.readFileStatus(file_original_name=old_filename, file_status = 'Uploaded')
            if file_details is not None:
                print('File {} was already uploaded before'.format(old_filename))
                retries = 3
                break
            file_details = db.readFileStatus(file_original_name=old_filename, file_status = 'Downloaded')
            print('Uploading {}'.format(path))
            remote_filename = _get_remote_filename(old_filename)
            directory = None
            if not remote_filename:
                return
            try:
                directory, filename, year = remote_filename
            except:
                directory, filename = remote_filename
            filename = fnm.azure_validate_filename(filename)
            if len(file_storage_dir) > 0:
                directory = file_storage_dir + '/' + directory
            if not file_service.exists(file_storage_share, directory_name=directory):
                file_service.create_directory(file_storage_share, directory)
            if year:
                directory += '/' + year
                if not file_service.exists(file_storage_share, directory_name=directory):
                    file_service.create_directory(file_storage_share, directory)
            if not overwrite_remote_files:
                print('Checking if {}/{} already exists'.format(directory, filename))
                if file_service.exists(file_storage_share, directory_name=directory, file_name=filename):
                    print('{}/{} already exists'.format(directory, filename))
                    if file_details is None:
                        db.saveFileStatus(script_name = script_name, file_original_name=old_filename, file_upload_path = directory, file_upload_name = filename, file_status = 'Uploaded')
                    else:
                        db.saveFileStatus(id = file_details['id'], file_upload_path = directory, file_upload_name = filename, file_status = 'Uploaded')
                    return
            file_service.create_file_from_path(
                file_storage_share,
                directory,
                filename,
                path,
                content_settings=ContentSettings(content_type='application/pdf'))
            if file_details is None:
                db.saveFileStatus(script_name = script_name, file_original_name=old_filename, file_upload_path = directory, file_upload_name = filename, file_status = 'Uploaded')
            else:
                db.saveFileStatus(id = file_details['id'], file_upload_path = directory, file_upload_name = filename, file_status = 'Uploaded')     
            print('{} uploaded'.format(path))
            retries = 3
        except Exception as e:
            print('Error uploading to Asure file storage,', str(e))
            retries += 1
                
if __name__ == '__main__':
    global db
    global dbparameters
    global file_service
    global file_storage_dir
    global file_storage_share
    global overwrite_remote_files
    global ftpurl
    global url
    global start_from
    global year
    global dir_in
    global dir_pdfs
    global illinois_entities_xlsx_file
    global illinois_entities_sheet
    config = configparser.ConfigParser()
    config.read('conf.ini')
    try:
        db = db(config)
        dbparameters = db.readProps('illinois')
        config_file = str(dbparameters)
        with open('IL_parms.txt', 'r') as fp:
            dparameters = json.load(fp)
        ftpurl = dbparameters["url"] or dparameters["ftpurl"]
        url = urllib.parse.urlparse(ftpurl)
        start_from = dbparameters["start_from"] or dparameters["start_from"]
        year = dbparameters["year"] or dparameters["year"]
        dir_in = dbparameters["dir_in"] or dparameters["dir_in"]
        dir_pdfs = dbparameters["dir_pdfs"] or dparameters["dir_pdfs"]
        illinois_entities_xlsx_file = dbparameters["illinois_entities_xlsx_file"] or dparameters["illinois_entities_xlsx_file"]
        illinois_entities_sheet = dbparameters["illinois_entities_sheet"] or dparameters["illinois_entities_sheet"]
        # if log file become large, you can change filemode='w' for logging only individual sessons
        logging.basicConfig(filename=dir_in + 'get_ILlog.txt', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

        logging.debug('Started')
        
        try:
            os.makedirs(dir_pdfs)
        except:
            pass
        os.chdir(dir_pdfs)
        main()
    except Exception as e:
        result = 0
        error_message = str(e)
        print(error_message)
    finally:
        db.close()
        end_time = datetime.utcnow()
        db.log(script_name, start_time, end_time, config_file, result, error_message)            
        print('Done.')
