# SingleAuditRepo
The goal of this project is to provide a comprehensive, free and regularly updated directory of US local government audited financial statements. The main source is the Federal Audit Clearinghouse, but this will be supplemented from state repositories and potentially other sources.

The files are being stored at http://www.govwiki.info/pdfs.
The file naming convention is [SS EEEEE YYYY.pdf] where:
  SS = Two position state code
  EEEEE = Name of entity (variable number of positions)
  YYYY = Fiscal Year

The files are divided into folders for General Purpose governments (cities, counties and states), School Districts, Community College Districts, Public Higher Education and Special Districts.  Because many single audit filers are private, not-for-profits, we have also included a Non-Profit folder. Due to classification errors in the Federal Single Audit data set and other technology problems, the classification is imperfect at this time.

Following are descriptions of the download scripts.

# transfer_pdfs.py
Script for downloading zip files from Federal Audit Clearinghouse, extracting pdfs from, then renaming files and uploading via FTP  

# Installation
Script is python3.5+ program  
Depends on installed selenium, pyvirtualdisplay, BeautifulSoup4, openpyxl  
pip install -U selenium pyvirtualdisplay BeautifulSoup4 openpyxl  

Also depends on geckodriver.  
geckodriver can be downloaded from  
https://github.com/mozilla/geckodriver/releases  
  
Don't forget to fill parameters.txt file with correct values  

Note. You can use combination of download.py and commented out download() function (at the end) in transfer_pdfs.py  
or only transfer_pdfs.py with download() function uncommented.  
  
If some of the pdf file(s) are not renamed, you can use rename_upload.py  
placing previously in dir_pdfs unrenamed files, also previously preparing FileNameCrossReferenceList.xlsx  
as merged document from all FileNameCrossReferenceList.xlsx partials in zip files.  
Merged FileNameCrossReferenceList.xlsx should be placed in dir_pdfs directory.
  
# illinois.py  
Script for downloading pdfs from Illinois Comptroller's Warehouse, merging partial pdfs when split up in the warehouse  
then renaming files (and eventually uploading via FTP)  
  
Don't forget to fill illinois_parameters.txt with correct values  

Script depends on openpyxl, pdftk  
pip install -U openpyxl  

pdftk is used for merging (if more then one) pdf files  
on linux it can be installed sudo apt install pdftk  
on windows https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/pdftk_free-2.02-win-setup.exe (is link valid)  
pdftk.exe must be startable in dir_pdfs  
testing example in dir_pdfs via terminal on windows pdftk.exe file1.pdf file2.pdf cat output newfile.pdf  
  
# Licence  
GPL  

