# SingleAuditRepo
This script retrieves audited financial statements from the federal government's Single Audit Clearinghouse.
The Clearinghouse has over 17,000 audited finanical statements for fiscal year 2016 and should eventually reach 40,000.
But downloading these audits require multiple steps and provides PDFs with unintutive file names.

Downloaded and renamed Single Audits and CAFRs are being stored at http://www.govwiki.info/pdfs.
Users of this script can create their own Single Audit/CAFRs repositories.

# Installation
Script is python3.5+ program  
Dependencies installed selenium, pyvirtualdisplay, BeautifulSoup4, openpyxl  
pip install -U selenium pyvirtualdisplay BeautifulSoup4 openpyxl  

Also requires geckodriver.  
geckodriver can be downloaded from  
https://github.com/mozilla/geckodriver/releases  
  
Don't forget to fill in parameters.txt file with correct values
  
# Licence  
GPL  
