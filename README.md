# SingleAuditRepo
The goal of this project is to provide a comprehensive, free and regularly updated directory of US local government audited financial statements. The main source is the Federal Audit Clearinghouse, but this will be supplemented from state repositories and potentially other sources.

The files are being stored at http://www.govwiki.info/pdfs.
The file naming convention is [SS EEEEE YYYY.pdf] where:
  SS = Two position state code
  EEEEE = Name of entity (variable number of positions)
  YYYY = Fiscal Year

The files are divided into folders for General Purpose governments (cities, counties and states), School Districts, Community College Districts, Public Higher Education and Special Districts.  Because many single audit filers are private, not-for-profits, we have also included a Non-Profit folder. Due to classification errors in the Federal Single Audit data set and other technology problems, the classification is imperfect at this time.

Following are descriptions of the download scripts.

## get_FAC.py
Script for downloading zip files from Federal Audit Clearinghouse, extracting pdfs from, then renaming files and uploading via FTP  

### Installation
Script is python3.5+ program  
Depends on installed selenium, pyvirtualdisplay, BeautifulSoup4, openpyxl  
pip install -U selenium pyvirtualdisplay BeautifulSoup4 openpyxl  

Also depends on geckodriver.  
geckodriver can be downloaded from  
https://github.com/mozilla/geckodriver/releases  
  
Don't forget to fill FAC_parms.txt file with correct values  

Note. You can use combination of get_FAC_downloadpart.py and commented out download() function (at the end) in get_FAC.py  
or only get_FAC.py <-- recommended  
with download() function uncommented.  
  
If some of the pdf file(s) are not renamed, you can use get_FAC_rename_upload_part.py  
placing previously in dir_pdfs unrenamed files, also previously preparing FileNameCrossReferenceList.xlsx  
as merged document from all FileNameCrossReferenceList.xlsx partials in zip files.  
Merged FileNameCrossReferenceList.xlsx should be placed in dir_pdfs directory.
  
## get_IL.py  
Script for downloading pdfs from Illinois Comptroller's Warehouse, merging partial pdfs when split up in the warehouse  
then renaming files (and eventually uploading via FTP)  
 
### Installation
Script depends on openpyxl, pdftk  
pip install -U openpyxl 

Don't forget to fill IL_parms.txt with correct values 

pdftk is used for merging (if more then one) pdf files  
on linux it can be installed sudo apt install pdftk  
on windows download and install executable from https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/  
pdftk.exe must be startable in dir_pdfs  
testing example in dir_pdfs via terminal on windows pdftk.exe file1.pdf file2.pdf cat output newfile.pdf  
  
# Licence  
GPL  

