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

Note. You can use combination of get_FAC_downloadpart.py and get_FAC.py with todownload value 0 in FAC_parms.txt  
in which case get_FAC.py will process zip files stored in dir_downloads  
or only get_FAC.py with todownload value 1 in FAC_parms.txt  
  
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

## get_VA.py
Script for downloading pdfs from Virginia Local Government Reports web page
Usage:

python get_VA.py --year YEAR --category CATEGORY_NAME

Both arguments are optional.

### Installation
pip install -r requirements.txt

## get_GA.py
Script for downloading pdfs from Georgia Local Government Reports web page
Usage:

python get_GA.py START_YEAR END_YEAR

Both arguments are required.

## get_WA.py
Script for downloading pdfs from Washington State Local Government Reports web page
Usage:

python get_WA.py START_YEAR END_YEAR

Both arguments are required.

## get_AZ.py
Script for downloading pdfs from Arizona Local Government Reports web page
Usage:

python get_AZ.py

## get_FL.py
Script for downloading pdfs from Florida Local Government Reports web page
Usage:

python get_FL.py START_YEAR END_YEAR

Both arguments are required.

## get_AK.py
Script for downloading pdfs from Alaska Local Government Reports web page
Usage:

python get_AK.py YEAR

YEAR arguments is required.

## get_UT.py
Script for downloading pdfs from Utah Local Government Reports web page
Usage:

python get_UT.py YEAR

YEAR arguments is required.
  
# Licence  
GPL  

# Naming Convention Info
Purpose

My goal is to create a complete library of audited financial statements for US state and local governments. These entities publish audited financial statements each year, but they are often hard to find.  This library is intended to save researchers time and effort by allowing them to find all the documents in one place with easily recognizable file names.

We are using web scraping programs to find the documents, and load them into the library at http://www.govwiki.info/pdfs, but the uploading and renaming algorithms are not reliable.  So human librarians are needed to make sure that the documents have correct names and are located in the correct subfolders.

Note:  In May 2018, I anticipate that the library will be moved to the Azure platform.

Note:  Data sources that we scrape often contain financial statements for non-profit, non-governmental organizations.  We will capture these as well, but they are not the focus of this project.


File Names and Locations

The file naming convention is [SS EEEEE YYYY.pdf] where: 
SS = Two position state code 
EEEEE = Name of entity (variable number of positions) 
YYYY = Four digit year for the date on which the fiscal year ends.

The files are divided into folders for 
General Purpose governments (cities, towns, townships, villages, boroughs. municipalities, Puerto Rican municipios, counties, parishes and states)
School Districts (public school systems serving students between Kindergarten and 12th grade, known as K-12)
Community College Districts
Public Higher Education (state or local government operated four year colleges and universities)
Special Districts. These are governments that provide specialized services such as transportation, water, sewers, irrigation, reclamation and mosquito control.  Their names often end with one of these words:  Agency, Authority and Special District.
Non-Profit (Non-Governmental Organizations that don’t try to earn financial profits)


For General Purpose governments, there are some rules to follow for the EEEEE (Name of Entity) portion of the file name:
For counties, the name should end with the word “County”.  For example, Alameda County’s 2017 financial statement should be named CA Alameda County 2017.pdf  This distinguishes Alameda County from the city of Alameda whose 2017 financial statement would be named CA Alameda 2017.pdf
In Louisiana (LA). Counties are called Parishes.  Use the same naming approach as for Counties but use the word “Parish” instead of “County”.
In Alaska (AK), Counties are called Boroughs. Use the same naming approach as for Counties but use the word “Borough” instead of “County”
Puerto Rico has 78 municipios - which serve as both cities and counties.  Just provide the name of each municipio; it is not necessary to include the word “municipio” at the end
Several states have a unit of government called a Township.  Townships usually include multiple towns or villages within their geographical area.  You should use the put the word “Township” at the end of the name, like you would do with Counties.
For Cities, Villages and Towns, you should generally NOT end the name with these types.  The only exception is when the name of the government typically includes one f these words.  An example is the city of Kansas City, MO.  In this case, you would use the name MO Kansas City 2017.pdf for the 2017 financial statement.
For State financial statements, use the two-word state abbreviation followed by “State of “ and then the fill name of the state.  For example:  MO State of Missouri 2017.pdf.
In some states, there are towns, townships, villages and cities with duplicate names.  We can’t have duplicates in our library, so we have to have a way of distinguishing them.  The way we do this is to include the name of the County in which the government is located at the end of the file name just before the “YYYY.pdf”.  For example, Michigan has two townships named “Bingham Township” - one in Clinton County and the other in Leelanau County.  These files are named:
MI Bingham Township (Clinton County) 2016.pdf
MI Bingham Township (Leelanau County) 2016.pdf
This issue also occurs for school districts.


