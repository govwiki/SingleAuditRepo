import re
import os
import configparser
from datetime import datetime
from urllib.request import urlopen
from urllib.request import urlretrieve
from utils import FilenameManager
from bs4 import BeautifulSoup
from azure.storage.file import FileService, ContentSettings


global dir_pdfs
global db
global file_storage_dir
global file_storage_share


def main():
    file_storage_connect()
    cafr_year = 2009
    while (cafr_year < 2020):
        html = urlopen("http://www.municipalfinance.ri.gov/data/audits/" + str(cafr_year) + ".php")
        bsObj = BeautifulSoup(html.read(), "html.parser")
        links = bsObj.findAll(href=re.compile("pdf"))
        for link in links:
            if " " in link.get("href")[5:]:
                split = link.get("href")[5:].split()
                pdfurl = "http://www.municipalfinance.ri.gov" + split[0] + "%20" + split[1]
            else:
                pdfurl = "http://www.municipalfinance.ri.gov" + link.get("href")[5:]

            preparename = "RI" + link.text + str(cafr_year) + ".pdf"
            urlretrieve(pdfurl, preparename)
            file_details = db.readFileStatus(file_original_name=preparename)
            if file_details is None:
                file_details = db.saveFileStatus(script_name=script_name, file_original_name=preparename, file_status='Downloaded')
            upload_to_file_storage(preparename)
    cafr_year += 1


def _get_remote_filename(local_filename):
    abbr, directory, entity_name, year = local_filename[:-4].split('@#')
    filename = '{} {} {}.pdf'.format(abbr, entity_name, year)
    return directory, filename, year


def file_storage_connect():
    global file_service
    global file_storage_dir
    global file_storage_share
    global overwrite_remote_files
    global dir_pdfs
    file_storage_url = dbparameters['fs_server'].strip()
    file_storage_user = dbparameters['fs_username'].strip()
    file_storage_pwd = dbparameters['fs_password'].strip()
    file_storage_share = dbparameters['fs_share'].strip()
    file_storage_dir = dbparameters['fs_directory_prefix'].strip()
    overwrite_remote_files = dbparameters['overwrite_remote_files'].strip()
    dir_pdfs = dbparameters['dir_pdfs'].strip()
    file_service = FileService(account_name=file_storage_user, account_key=file_storage_pwd)
    try:
        if file_service.exists(file_storage_share):
            print('Connection to Azure file storage successfully established...')
            if len(file_storage_dir) > 0 and not file_service.exists(file_storage_share,
                                                                     directory_name=file_storage_dir):
                subdirs = file_storage_dir.split('/')
                subdirfull = ""
                for subdir in subdirs:
                    subdirfull += subdir
                    file_service.create_directory(file_storage_share, subdirfull)
                    subdirfull += "/"
                print('Created directory:' + file_storage_dir)
        else:
            print('Failed to connect to Asure file storage, share does not exist: ' + file_storage_share)
    except Exception as ex:
        print('Error connecting to Azure file storage: ', ex)


def upload_to_file_storage(filename):
    global script_name
    old_filename = filename
    downloads_path = dir_pdfs
    fnm = FilenameManager()
    retries = 0
    while retries < 3:
        try:
            path = os.path.join(downloads_path, old_filename)
            file_details = db.readFileStatus(file_original_name=old_filename, file_status='Uploaded')
            if file_details is not None:
                print('File {} was already uploaded before'.format(old_filename))
                retries = 3
                break
            file_details = db.readFileStatus(file_original_name=old_filename, file_status='Downloaded')
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
                        db.saveFileStatus(script_name=script_name, file_original_name=old_filename,
                                          file_upload_path=directory, file_upload_name=filename, file_status='Uploaded')
                    else:
                        db.saveFileStatus(id=file_details['id'], script_name=script_name, file_upload_path=directory,
                                          file_upload_name=filename, file_status='Uploaded')
                    return
            file_service.create_file_from_path(
                file_storage_share,
                directory,
                filename,
                path,
                content_settings=ContentSettings(content_type='application/pdf'))
            if file_details is None:
                db.saveFileStatus(script_name=script_name, file_original_name=old_filename, file_upload_path=directory,
                                  file_upload_name=filename, file_status='Uploaded')
            else:
                db.saveFileStatus(id=file_details['id'], script_name=script_name, file_upload_path=directory,
                                  file_upload_name=filename, file_status='Uploaded')
            print('{} uploaded'.format(path))
            retries = 3
        except Exception as e:
            print('Error uploading to Asure file storage,', str(e))
            filename = old_filename
            retries += 1


if __name__ == '__main__':
    start_time = datetime.utcnow()
    script_name = "get_RI.py"
    result = 1
    error_message = ""

    config = configparser.ConfigParser()
    config.read('conf.ini')
    db = db(config)
    try:
        dbparameters = db.readProps('rhode island')
        config_file = str(dbparameters)
        main()
    except Exception as e:
        result = 0
        error_message = str(e)
        print(error_message)
    finally:
        end_time = datetime.utcnow()
        db.log(script_name, start_time, end_time, config_file, result, error_message)
        db.close()
        print('Done.')
