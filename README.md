# SingleAuditRepo
Script for downloading zip files from specific url, extracting pdfs from, then renaming files and uploading via FTP  

# Instalation
Script is python3.5+ program  
Dependend on installed selenium, pyvirtualdisplay, BeautifulSoup4, openpyxl  
pip install -U selenium pyvirtualdisplay BeautifulSoup4 openpyxl  

Also is dependend on geckodriver.  
geckodriver can be downloaded from  
https://github.com/mozilla/geckodriver/releases  
  
Don't forget to fill parameters.txt file with correct values  

Note. You can use combination of download.py and commented out download() function (at the end) in transfer_pdfs.py  
or only transfer_pdfs.py with download() function uncommented.  
  
If by any case some of pdf file(s) are not renamed, you can use rename_upload.py  
placing previusly in dir_pdfs unrenamed files, also previously preparing FileNameCrossReferenceList.xlsx  
as merged document from all FileNameCrossReferenceList.xlsx partials in zip files  
  
# Licence  
GPL  

