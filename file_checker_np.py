import csv
import io
import os
from time import sleep

from PyPDF4 import PdfFileReader
from azure.storage.file import FileService, Directory, File
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer3.converter import TextConverter
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.pdfpage import PDFPage

downloads_path = '/tmp/downloads/FromAzure/'
file_storage_user = ''
file_storage_pwd = ''
file_storage_share = ''
resource_manager = PDFResourceManager()
folders = ['2015', '2016', '2017', '2018', '2019']
directories = ['Non-Profit']


def file_storage_connect():
    file_service = FileService(account_name=file_storage_user, account_key=file_storage_pwd, socket_timeout=15)
    try:
        if file_service.exists(file_storage_share):
            print('Connection to Azure file storage successfully established...')
        else:
            print('Filaed to connect to Asure file storage, share does not exist: ' + file_storage_share)
    except Exception as ex:
        print('Error connecting to Azure file storage: ', ex)
    return file_service


def file_check(dir):
    file_names = list(file_service.list_directories_and_files(file_storage_share, dir))
    for file in file_names:
        if isinstance(file, Directory):
            print('Directory: ' + file.name)
            if file.name not in folders:
                continue
            file_check(dir + '/' + file.name)
        elif isinstance(file, File):
            print('File: ' + file.name)
            downloaded = file_service.get_file_to_path(file_storage_share, dir, file.name,
                                                       downloads_path + file.name, timeout=120)
            if downloaded:
                try:
                    with open(downloads_path + file.name, 'rb') as f:
                        pdf = PdfFileReader(f)
                        info = pdf.getDocumentInfo()
                    print(info)
                except Exception as e:
                    print(e)
                    try:
                        fake_file_handle = io.StringIO()
                        converter = TextConverter(resource_manager, fake_file_handle)
                        page_interpreter = PDFPageInterpreter(resource_manager, converter)
                        with open(downloads_path + file.name, 'rb') as fh:
                            for page in PDFPage.get_pages(fh,
                                                          caching=True,
                                                          check_extractable=False):
                                page_interpreter.process_page(page)
                                break
                            text_from_pdf_miner = fake_file_handle.getvalue()
                            converter.close()
                            fake_file_handle.close()
                    except Exception as exx:
                        print(exx)
                        with open('corrupted_files/corrupted_files_nonprofit.csv', 'a', newline='') as fi:
                            writer = csv.writer(fi)
                            writer.writerow([file.name])
            if os.path.exists(os.path.join(downloads_path + file.name)):
                try:
                    os.remove(os.path.join(downloads_path, file.name))
                except Exception as e:
                    print(e)
            if not os.path.exists(os.path.join(downloads_path + file.name)):
                print('Removed {}'.format(downloads_path + file.name))


if __name__ == '__main__':
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    file_service = file_storage_connect()
    dirs = file_service.list_directories_and_files(file_storage_share)
    for dir in dirs:
        if dir.name not in directories:
            continue
        print('Directory: ' + dir.name)
        file_check(dir.name)
