# SingleAuditRepo
# transfer_pdfs.py
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
as merged document from all FileNameCrossReferenceList.xlsx partials in zip files.  
Merged FileNameCrossReferenceList.xlsx should be placed in dir_pdfs directory.
  
# illinois.py  
Script for downloading pdf Illinois files from public ftp, merging in one if more pdf files in subdirectory  
then renaming files (and eventually uploading via FTP)  
  
Don't forget to fill illinois_parameters.txt with correct values  

Script is dependend on openpyxl, pdftk  
pip install -U openpyxl  
pdftk is used for merging (if more then one) pdf files  
on linux it can be installed sudo apt install pdftk  
on windows https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/pdftk_free-2.02-win-setup.exe (is link valid)  
pdftk.exe must be startable in dir_pdfs  
testing example in dir_pdfs via terminal on windows pdftk.exe file1.pdf file2.pdf cat output newfile.pdf  
  
# Licence  
GPL  

