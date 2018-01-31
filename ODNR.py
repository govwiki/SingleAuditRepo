###########################################################################
# Open Data for Nonprofit Reseearch (ODNR)
# Server-Side Object Model
#
# Last revision: 09/20/2017
#
# Authors:
#   P. Kevin Bohan <votiputox@gmail.com>
#   Marc Joffe <marc@publicsectorcredit.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from enum import Enum
import urllib.request
import zipfile
import csv
import datetime
import glob
import math
import os
import re
import sys
import time


##########
# Globals
##########

raw_state_data = [
    [ 'AL',  1, 'Alabama'                        ],
    [ 'AK',  2, 'Alaska'                         ],
    [ 'AS', 80, 'American Samoa'                 ],
    [ 'AZ',  3, 'Arizona'                        ],
    [ 'AR',  4, 'Arkansas'                       ],
    [ 'CA',  6, 'California'                     ],
    [ 'CO',  8, 'Colorado'                       ],
    [ 'CT',  9, 'Connecticut'                    ],
    [ 'DE', 10, 'Delaware'                       ],
    [ 'DC', 11, 'District of Columbia'           ],
    [ 'FL', 12, 'Florida'                        ],
    [ 'FM', 64, 'Federated States of Micronesia' ],
    [ 'GA', 13, 'Georgia'                        ],
    [ 'GU', 66, 'Guam'                           ],
    [ 'HI', 15, 'Hawaii'                         ],
    [ 'ID', 16, 'Idaho'                          ],
    [ 'IL', 17, 'Illinois'                       ],
    [ 'IN', 18, 'Indiana'                        ],
    [ 'IA', 19, 'Iowa'                           ],
    [ 'KS', 20, 'Kansas'                         ],
    [ 'KY', 21, 'Kentucky'                       ],
    [ 'LA', 22, 'Louisiana'                      ],
    [ 'ME', 23, 'Maine'                          ],
    [ 'MH', 68, 'Marshall Islands'               ],
    [ 'MD', 24, 'Maryland'                       ],
    [ 'MA', 25, 'Massachusetts'                  ],
    [ 'MI', 26, 'Michigan'                       ],
    [ 'MN', 27, 'Minnesota'                      ],
    [ 'MS', 28, 'Mississippi'                    ],
    [ 'MO', 29, 'Missouri'                       ],
    [ 'MT', 30, 'Montana'                        ],
    [ 'NE', 31, 'Nebraska'                       ],
    [ 'NV', 32, 'Nevada'                         ],
    [ 'NH', 33, 'New Hampshire'                  ],
    [ 'NJ', 34, 'New Jersey'                     ],
    [ 'NM', 35, 'New Mexico'                     ],
    [ 'NY', 36, 'New York'                       ],
    [ 'NC', 37, 'North Carolina'                 ],
    [ 'ND', 38, 'North Dakota'                   ],
    [ 'MP', 69, 'Northern Mariana Islands'       ],
    [ 'OH', 39, 'Ohio'                           ],
    [ 'OK', 40, 'Oklahoma'                       ],
    [ 'OR', 41, 'Oregon'                         ],
    [ 'PW', 70, 'Palau'                          ],
    [ 'PA', 42, 'Pennsylvania'                   ],
    [ 'PR', 72, 'Puerto Rico'                    ],
    [ 'RI', 44, 'Rhode Island'                   ],
    [ 'SC', 45, 'South Carolina'                 ],
    [ 'SD', 46, 'South Dakota'                   ],
    [ 'TN', 47, 'Tennessee'                      ],
    [ 'TX', 48, 'Texas'                          ],
    [ 'UM', 74, 'U.S. Minor Outlying Islands'    ],
    [ 'UT', 49, 'Utah'                           ],
    [ 'VT', 50, 'Vermont'                        ],
    [ 'VA', 51, 'Virginia'                       ],
    [ 'VI', 78, 'U.S. Virgin Islands'            ],
    [ 'WA', 53, 'Washington'                     ],
    [ 'WV', 54, 'West Virginia'                  ],
    [ 'WI', 55, 'Wisconsin'                      ],
    [ 'WY', 56, 'Wyoming'                        ],
]

facdb_url = 'https://www.census.gov/pub/outgoing/govs/singleaudit/allfac.zip'
facdb_tmp = '.'

fac_url = 'https://harvester.census.gov/facdissem/SearchA133.aspx'
fac_dir = '.'
fac_tmp = '.'
fac_ts  = 10


#######################
# Utility
# Some utility methods
#######################

class Utility(object):

    #==========================================================
    # Normalize an integer
    # Returns an integer representation of a normalized string
    #==========================================================
    def normal_int(data):
        retval = None

        if data != None:
            strval = data.rstrip(' ')
            if len(strval) > 1:
                retval = int(strval)

        return retval
    
    
    #================================================
    # Normalize a string
    # OPERATIONS:
    #   - Remove leading whitespace
    #   - Remove trailing whitespace
    #   - Convert double spaces into a comma + space
    #================================================
    @staticmethod
    def normal_str(data):
        retval = None
        
        if data != None:
            retval = data.rstrip(' ')
            p = re.compile('  ')
            retval = p.sub(', ', retval)

        return retval


    #=================================================================
    # Normalize a boolean
    # Converts a 'Y' or 'N' string into a True or False, respectively
    #=================================================================
    @staticmethod
    def normal_bool(data):
        retval = False

        if data != None:
            if data == 'Y':
                retval = True

        return retval
    

    #=====================================
    # Normalize a date
    # Parses dates into a datetime object
    #=====================================
    @staticmethod
    def normal_date(data):
        retval = None
        
        if data != None:
            retval = data.rstrip(' ')
            if len(retval) > 1:
                retval = datetime.datetime.strptime(data.rstrip(' '), '%d-%b-%y')

        return retval
    

    #===========================================
    # Normalize a phone number
    # Parses phone numbers into a common format
    #===========================================
    @staticmethod
    def normal_phone(data):
        retval = None
        
        if data != None:
            retval = data.rstrip(' ')
            if len(retval) == 10:
                retval = '+1 (' + retval[:3] + ') ' + retval[3:6] + '-' + retval[6:10]
            else:
                retval = None

        return retval


    #=======================================
    # Normalize a zip code
    # Converts ZIP+4 into the proper format
    #=======================================
    @staticmethod
    def normal_zip(data):
        retval = None

        if data != None:
            retval = data.rstrip(' ')
            if len(retval) > 5:
                retval = retval[:5] + '-' + retval[5:]

        return retval


    #======================================================
    # Convert a date into a string
    # Returns a string representation of a normalized date
    #======================================================
    @staticmethod
    def date_to_str(data):
        retval = None

        if data != None:
            retval = data.strftime('%m/%d/%Y')

        return retval
    

    #===========================================
    # Convert a boolean to a string
    # Returns 'Yes' for True and 'No' for False
    #===========================================
    @staticmethod
    def bool_to_str(data):
        retval = False

        if data == True:
            retval = 'Yes'
        else:
            retval = 'No'

        return retval

    
    
#################################################
# State
# Represents a U.S. state, territory or province
#################################################

class State(object):
    def __init__(self, data):
        self.long_name = data[2]
        self.short_name = data[0]
        self.fips = data[1]

    #================================
    # Get the full name of the state
    #================================
    def get_name(self):
        return self.long_name

    #=========================================
    # Get the state's FIPS PUB 5-2 Alpha code
    #=========================================
    def get_abbrev(self):
        return self.short_name

    #===========================================
    # Get the state's FIPS PUB 5-2 Numeric code
    #===========================================
    def get_fips(self):
        return self.fips

    #===========================
    # Get the set of all states
    #===========================
    @staticmethod
    def get_all():
        sts = []
        for t in raw_state_data:
            st = State(t)
            sts.append(st)

        return sts

    #===============================
    # Find a state by its full name
    #===============================
    @staticmethod
    def find_by_name(name):
        st = None
        for t in raw_state_data:
            if t[2].upper() == name.upper():
                st = State(t)

        return st

    #=======================================================
    # Find a state by its abbreviation (FIPS PUB 5-2 Alpha)
    #=======================================================
    @staticmethod
    def find_by_abbrev(abbrev):
        st = None
        for t in raw_state_data:
            if t[0] == abbrev.upper():
                st = State(t)

        return st

    #=================================================
    # Find a state by its code (FIPS PUB 5-2 Numeric)
    #=================================================
    @staticmethod
    def find_by_fips(fips):
        st = None
        for t in raw_state_data:
            if t[1] == fips:
                st = State(t)

        return st

                 
    
#############################
# Organization
# Represents an organization
#############################

class Organization(object):

    def __init__(self,
                 csv=None,
                 ein=None,
                 name=None,
                 address=None,
                 address2=None,
                 city=None,
                 state=None,
                 zipcode=None,
                 phone=None,
                 fax=None,
                 email=None,
                 contact=None,
                 title=None):

        if csv != None:
            self.ein = csv['ein'] 
            self.name = csv['name'] 
            self.address = csv['address']
            self.address2 = csv['address2']
            self.city = csv['city']
            self.state = csv['state'] 
            self.zipcode = csv['zipcode']
            self.phone = csv['phone']
            self.fax = csv['fax']
            self.email = csv['email']
            self.contact = csv['contact']
            self.title = csv['title']
        else:
            self.ein = ein
            self.name = name
            self.address = address
            self.address2 = address2
            self.city = city
            self.state = state
            self.zipcode = zipcode
            self.phone = phone
            self.fax = fax
            self.email = email
            self.contact = contact
            self.title = title


    #============================
    # Get the organization's EIN
    #============================
    def get_ein(self):
        return self.ein
    
    
    #=============================
    # Get the organization's name
    #=============================
    def get_name(self):
        return self.name


    #================================================
    # Get the organization's street address (line 1)
    #================================================
    def get_address(self):
        return self.address


    #================================================
    # Get the organization's street address (line 2)
    #================================================
    def get_address2(self):
        return self.address2


    #=====================================
    # Get the city the organization is in
    #=====================================
    def get_city(self):
        return self.city


    #======================================
    # Get the state the organization is in
    #======================================
    def get_state(self):
        return self.state


    #================================
    # Get the organization's zipcode
    #================================
    def get_zipcode(self):
        return self.zipcode


    #=============================================
    # Get the organization's primary phone number
    #=============================================
    def get_phone(self):
        return self.phone


    #===========================================
    # Get the organization's primary fax number
    #===========================================
    def get_fax(self):
        return self.fax


    #======================================
    # Get the organization's email address
    #======================================
    def get_email(self):
        return self.email


    #=====================================
    # Get the organization's contact name
    #=====================================
    def get_contact_name(self):
        return self.contact


    #=========================
    # Get the contact's title
    #=========================
    def get_contact_title(self):
        return self.title

    

#############################
# Report
# Base class for all reports
#############################
    
class Report(object):
    def __init__(self, id):
        self.id = id


        
###################################
# FederalAuditType
# Enumeration of audit types
#
# SINGLE  = Single audit
# PROGRAM = Program-specific audit
###################################

class FederalAuditType(Enum):
    SINGLE  = 1,
    PROGRAM = 2


    
########################################
# FederalAudit
# Represents an audit report from
# the Federal Audit Clearinghouse (FAC)
########################################
        
class FederalAudit(Report):
    def __init__(self,
                 csv=None,
                 id=None,
                 year=None,
                 fy_end=None,
                 atype=FederalAuditType.SINGLE,
                 period=12,
                 auditee=None,
                 signedname=None,
                 signeddate=None,
                 cpa=None,
                 cpasigneddate=None,
                 multiplecpas=False):

        if csv != None:
            self.id = csv['id'] 
            self.year = csv['year']
            self.fy_end = csv['fy_end']
            self.atype = csv['atype']
            self.period = csv['period']
            self.auditee = csv['auditee']
            self.signedname = csv['signedname']
            self.signeddate = csv['signeddate']
            self.cpa = csv['cpa']
            self.cpasigneddate = csv['cpasigneddate']
            self.multiplecpas = csv['multiplecpas']
        else:
            self.id = id
            self.year = year
            self.fy_end = fy_end
            self.atype = atype
            self.period = period
            self.auditee = auditee
            self.signedname = signedname
            self.signeddate = signeddate
            self.cpa = cpa
            self.cpasignedate = cpasigneddate
            self.multiplecpas = multiplecpas

            
    #===================
    # Get the report ID
    #===================
    def get_id(self):
        return self.id

    
    #====================
    # Get the audit year
    #====================
    def get_year(self):
        return self.year

    
    #================================
    # Get the end of the fiscal year
    # (returns a datetime object)
    #================================
    def get_fiscal_year_end(self):
        return self.fy_end
    

    #====================
    # Get the audit type
    #====================
    def get_type(self):
        return self.atype


    #==================================
    # Get the audit period (in months)
    #==================================
    def get_period(self):
        return self.period
    

    #==============================
    # Get the auditee organization
    #==============================
    def get_auditee(self):
        return self.auditee


    #===================================
    # Get the date the audit was signed
    #===================================
    def get_signed_date(self):
        return self.signeddate


    #=========================================================
    # Get the name & title of the person who signed the audit
    #=========================================================
    def get_signed_nametitle(self):
        return self.signedname


    #========================================================
    # Get the accounting firm (CPA) that prepared the report
    #========================================================
    def get_cpa(self):
        return self.cpa


    #====================================================
    # Get the date the accounting firm signed the report
    #====================================================
    def get_cpa_signed_date(self):
        return self.cpasigneddate


    #=============================================================
    # Get whether or not multiple CPAs were involved in the audit
    #=============================================================
    def is_multiple_cpas(self):
        return self.multplecpas
    
    
    #=================================================
    # Generate a string representation of this report
    #=================================================
    def to_string(self):
        at = {}
        at[FederalAuditType.SINGLE]  = 'Single'
        at[FederalAuditType.PROGRAM] = 'Program-specific'
        
        retval = '------------------------------------------------------------\n'   + \
                 'ID:                 ' + str(self.id)                     + '\n'   + \
                 'Audit Year:         ' + str(self.year)                   + '\n'   + \
                 'FY End:             ' + Utility.date_to_str(self.fy_end) + '\n'   + \
                 'Type:               ' + at[self.atype]                   + '\n'   + \
                 'Period:             ' + str(self.period) + ' months'     + '\n\n' + \
                 'Auditee EIN:        ' + str(self.auditee.get_ein())      + '\n'   + \
                 'Auditee Address:    ' + self.auditee.get_name()          + '\n'   + \
                 '                    ' + self.auditee.get_address()       + '\n'

        if self.auditee.get_address2():
            retval += '                    ' + self.auditee.get_address2() + '\n'

        retval += '                    ' + self.auditee.get_city() + ', '   + \
                  self.auditee.get_state().get_abbrev()            + '  '   + \
                  self.auditee.get_zipcode()                       + '\n\n'

        retval += 'Auditee Phone:       ' + self.auditee.get_phone()        + '\n'

        if self.auditee.get_fax():
            retval += 'Auditee Fax:         ' + self.auditee.get_fax()          + '\n'
        else:
            retval += 'Auditee Fax:         None\n'

        retval += 'Auditee Email:      ' + self.auditee.get_email()             + '\n\n'   
            
        retval += 'Contact Name:       ' + self.auditee.get_contact_name()      + '\n'   + \
                  'Contact Title:      ' + self.auditee.get_contact_title()     + '\n\n' + \
                  'Signed Name/Title:  ' + self.signedname                      + '\n'   + \
                  'Signed Date:        ' + Utility.date_to_str(self.signeddate) + '\n\n'

        if self.cpa.get_ein():
            retval += 'CPA EIN:            ' + str(self.cpa.get_ein())          + '\n'
        else:
            retval += 'CPA EIN:            None\n'
        
        retval += 'CPA Name:           ' + self.cpa.get_name()                  + '\n' + \
                  'CPA Address:        ' + self.cpa.get_address()               + '\n'

        if self.cpa.get_address2():
            retval += '                    ' + self.cpa.get_address2()          + '\n'

        retval += '                    ' + self.cpa.get_city() + ', '   + \
                  self.cpa.get_state().get_abbrev()            + '  '   + \
                  self.cpa.get_zipcode()                       + '\n\n'

        retval += 'CPA Contact Name:   ' + self.cpa.get_contact_name()             + '\n' + \
                  'CPA Contact Title:  ' + self.cpa.get_contact_title()            + '\n' + \
                  'CPA Signed Date:    ' + Utility.date_to_str(self.cpasigneddate) + '\n\n'

        retval += 'CPA Phone:          ' + self.cpa.get_phone()         + '\n'

        if self.cpa.get_fax():
            retval += 'CPA Fax:            ' + self.cpa.get_fax()       + '\n'
        else:
            retval += 'CPA Fax:            None\n'

        retval += 'CPA Email:          ' + self.cpa.get_email()         + '\n\n'

        retval += 'Multple CPAs:       ' + Utility.bool_to_str(self.multiplecpas) + '\n' 
        
        return retval

    
        
############################################
# FACDB
# Methods for interacting with FAC metadata
############################################

class FACDB(object):

    def __init__(self):
        self.generated = datetime.datetime.today()
        self.reports = []

    #=============================================
    # Parse original DB files into a FACDB object
    #=============================================
    @staticmethod
    def from_file(dir=facdb_tmp):
        db = FACDB()
        orgs = {}
        cpas = {}
        
        # Iterate over general information in the CSV
        # WARNING: These files are encoded in ISO
        # Latin 1, not unicode (UTF-8)
        with open(dir + '/general.txt', newline='', encoding='latin-1') as general:
            reader = csv.DictReader(general, delimiter=',', quotechar='|', dialect='excel')
            for row in reader:
                fa_csv = {}                
                fa_csv['id'] = int(row['DBKEY'])
                fa_csv['year'] = int(row['AUDITYEAR'])
                fa_csv['fy_end'] = Utility.normal_date(row['FYENDDATE'])
        
                # Audit type
                if row['AUDITTYPE'] == 'S':
                    fa_csv['atype'] = FederalAuditType.SINGLE
                else:
                    fa_csv['atype'] = FederalAuditType.PROGRAM
            
                # Audit period
                if row['PERIODCOVERED'] == 'A':
                    fa_csv['period'] = 12
                elif row['PERIODCOVERED'] == 'B':
                    fa_csv['period'] = 24
                else:
                    fa_csv['period'] = int(row['NUMBERMONTHS'])

                # Auditee
                auditee = {}
                auditee['ein']      = int(row['EIN'])
                auditee['name']     = Utility.normal_str(row['AUDITEENAME'])
                auditee['address']  = Utility.normal_str(row['STREET1'])
                auditee['address2'] = Utility.normal_str(row['STREET2'])
                auditee['city']     = Utility.normal_str(row['CITY'])
                auditee['state']    = State.find_by_abbrev(row['STATE'])
                auditee['zipcode']  = Utility.normal_zip(row['ZIPCODE'])
                auditee['phone']    = Utility.normal_phone(row['AUDITEEPHONE'])
                auditee['fax']      = Utility.normal_phone(row['AUDITEEFAX'])
                auditee['email']    = Utility.normal_str(row['AUDITEEEMAIL'])
                auditee['contact']  = Utility.normal_str(row['AUDITEECONTACT'])
                auditee['title']    = Utility.normal_str(row['AUDITEETITLE'])
                
                org = None
                if auditee['ein'] in orgs:
                    org = orgs[auditee['ein']]
                else:
                    org = Organization(csv=auditee)
                fa_csv['auditee'] = org

                # The name and title of the person who signed it, plus the date
                fa_csv['signedname'] = Utility.normal_str(row['AUDITEENAMETITLE'])
                fa_csv['signeddate'] = Utility.normal_date(row['AUDITEEDATESIGNED'])

                # The accounting firm that did the analysis
                cpa = {}

                cpa['ein']          = Utility.normal_int(row['AUDITOR_EIN'])
                cpa['name']         = Utility.normal_str(row['CPAFIRMNAME'])
                cpa['address']      = Utility.normal_str(row['CPASTREET1'])
                cpa['address2']     = Utility.normal_str(row['CPASTREET2'])
                cpa['city']         = Utility.normal_str(row['CPACITY'])
                cpa['state']        = State.find_by_abbrev(row['CPASTATE'])
                cpa['zipcode']      = Utility.normal_zip(row['CPAZIPCODE'])
                cpa['phone']        = Utility.normal_phone(row['CPAPHONE'])
                cpa['fax']          = Utility.normal_phone(row['CPAFAX'])
                cpa['email']        = Utility.normal_str(row['CPAEMAIL'])
                cpa['contact']      = Utility.normal_str(row['CPACONTACT'])
                cpa['title']        = Utility.normal_str(row['CPATITLE'])
                
                cpa_org = None
                if cpa['name'] in cpas:
                    cpa_org = cpas[cpa['name']]
                else:
                    cpa_org = Organization(csv=cpa)
                fa_csv['cpa'] = cpa_org

                fa_csv['cpasigneddate'] = Utility.normal_date(row['CPADATESIGNED'])
                fa_csv['multiplecpas']  = Utility.normal_bool(row['MULTIPLE_CPAS'])
                
                fa = FederalAudit(csv=fa_csv)
                db.reports.append(fa)
                print(fa.to_string())
        
        return db
    
        
    #====================================
    # Generate a FACDB object from a URL
    #====================================
    @staticmethod
    def from_url(url=facdb_url, work=facdb_tmp):

        # Download the entire FAC database
        resp = urllib.request.urlretrieve(url, temp + '/allfac.zip')

        # Unzip the file
        zip = ZipFile(temp + '/allfac.zip', 'r')
        zip.extractall(temp)
        zip.close()

        # Parse it
        return FACDB.from_file(dir=work)

    
    
###########################################
# FAC
# Methods for interacting with the Federal
# Audit Clearinghouse (FAC)
###########################################

class FAC(object):

    #===============================================
    # Helper: Find an element by its CSS identifier
    #===============================================    
    def __find_tag_by_selector(driver, css_selector, ts):
        element = WebDriverWait(driver, ts).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        if element:
            return element
        else:
            return False

        
    #=====================================
    # Helper: Find a method through XPath
    #=====================================
    def __find_tag_by_xpath(driver, xpath, ts):
        element = WebDriverWait(driver, ts).until(EC.presence_of_element_located((By.XPATH, xpath)))
        if element:
            return element
        else:
            return False

        
    #============================
    # Helper: Click on a control
    #============================
    def __open_tag(driver, css_selector, ts):
        element = FAC.__find_tag_by_selector(driver, css_selector, ts)
        actions = ActionChains(driver)
        actions.move_to_element(element).click().perform()

        
    #==========================
    # Type text into a control
    #==========================
    def __enter_in_tag(driver, css_selector, text, ts):
        element = FAC.__find_tag_by_selector(driver, css_selector, ts)
        actions = ActionChains(driver)
        actions.move_to_element(element).send_keys(text).perform()

        
    #==============================
    # See if a checkbox is checked
    #==============================
    def __is_checked(driver, css_selector, ts):
        element = FAC.__find_tag_by_selector(driver, css_selector, ts)
        return element.is_selected()

    
    #====================================
    # Figure out what a state's index is
    #====================================
    def __get_state_element_id(driver, state, ts):
        element = FAC.__find_tag_by_xpath(driver, "//input[@value='" + state.get_abbrev() + "']", ts)
        return '#' + element.get_attribute("id")

    
    #===============================
    # Wait for a download to finish
    #===============================
    def __wait_for_download(dir, ts):
        time.sleep(ts)
        dls = glob.glob(dir + "/*.crdownload")
        while len(dls) > 0:
            time.sleep(math.ceil(ts / 2))
            dls = glob.glob(dir + "/*.crdownload")

            
    #=============================================
    # Download audits
    # WARNING: This is a side-effecting method!
    #          Prints to STDOUT if quiet == False
    #=============================================
    @staticmethod
    def fetch_audits(url, st, begin_date, end_date, quiet, timeout, dir, tmp):
        audits_found = []
                
        # Set up the virtual display
        display = Display(visible=0, size=(1024, 1024))
        display.start()

        # Use Google Chrome
        webopts = webdriver.ChromeOptions()
        webprefs = { 'download.default_directory' : tmp }
        webopts.add_experimental_option('prefs', webprefs)
    
        drv = webdriver.Chrome(chrome_options = webopts)
        drv.implicitly_wait(timeout)

        if not quiet:
            sys.stdout.write("\nSearching for reports between ")
            sys.stdout.write(begin_date.strftime('%m/%d/%Y') + ' and ')
            sys.stdout.write(end_date.strftime('%m/%d/%Y') + ' for ')
            sys.stdout.write(st.get_name() + '...\n')
                         
        # Fetch the top-level page
        try:
            drv.get(url)
        except Exception as e:
            if not quiet:
                print(str(e))
                sys.exit()
        
        # Click on "GENERAL INFORMATION"
        FAC.__open_tag(drv, '#ui-id-1', timeout)
        time.sleep(1)
        
        # Figure out the index of the start year (assume current year is 1)
        today = datetime.datetime.today()
        idx_begin = (today.year % begin_date.year) + 1
        idx_end = (today.year % end_date.year) + 1
    
        # Uncheck 'All Years'
        FAC.__open_tag(drv, '#MainContent_UcSearchFilters_FYear_CheckableItems_0', timeout)
        while FAC.__is_checked(drv, '#MainContent_UcSearchFilters_FYear_CheckableItems_0', timeout) == True:
            time.sleep(0.2)
    
        # Check applicable years
        # The current year may not be available, so we'll fail silently if we can't check the last year
        for idx in range(idx_end, (idx_begin + 1)):
            try:
                css_id = '#MainContent_UcSearchFilters_FYear_CheckableItems_' + str(idx)
                FAC.__open_tag(drv, css_id, timeout)
            except:
                css_id = None

            if css_id:
                while FAC.__is_checked(drv, css_id, timeout) == False:
                    time.sleep(0.2)
        
        # Fill out start and end dates
        fmt_start = begin_date.strftime('%m/%d/%Y')
        fmt_end = end_date.strftime('%m/%d/%Y')

        FAC.__open_tag(drv, "#MainContent_UcSearchFilters_DateProcessedControl_FromDate", timeout)
        FAC.__enter_in_tag(drv, "#MainContent_UcSearchFilters_DateProcessedControl_FromDate", fmt_start, timeout)

        FAC.__open_tag(drv, "#MainContent_UcSearchFilters_DateProcessedControl_ToDate", timeout)
        FAC.__enter_in_tag(drv, "#MainContent_UcSearchFilters_DateProcessedControl_ToDate", fmt_end, timeout)
    
        # Check the state that matches the requested index
        css_id = FAC.__get_state_element_id(drv, st, timeout)
        FAC.__open_tag(drv, css_id, timeout)

        while FAC.__is_checked(drv, css_id, timeout) == False:
            drv.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            FAC.__open_tag(drv, css_id, timeout)
  
        # Submit the form
        FAC.__open_tag(drv, '#MainContent_UcSearchFilters_btnSearch_bottom', timeout)
    
        # Click through the disclosure page
        FAC.__open_tag(drv, '#chkAgree', timeout)
        FAC.__open_tag(drv, '#btnIAgree', timeout)

        element = FAC.__find_tag_by_xpath(drv, "//span[@id='MainContent_ucA133SearchResults_lblCount']//span[@class='resultsText']", timeout)
        total_audits = int(element.text)

        if total_audits == 0:
            drv.close()
            display.stop()

            if not quiet:
                print("No audits found.\n")

            return audits_found
    
        element = FAC.__find_tag_by_xpath(drv, "//span[@id='MainContent_ucA133SearchResults_SelectedCountLabelTop']//span[@class='resultsText']", timeout)
        download_audits = int(element.text)

        if download_audits == 0:
            drv.close()
            display.stop()
        
            if not quiet:
                print("No downloadable audits found.\n")
            
                return audits_found
        else:
            if not quiet:
                print("Found " + str(download_audits) + " downloadable audits out of " + str(total_audits) + " total audits.\n")
            
        # Select audits and download
        downloaded = 0
        rpts_drop = Select(FAC.__find_tag_by_selector(drv, '#MainContent_ucA133SearchResults_ddlAvailZipTop', timeout))
        rpts_opts = rpts_drop.options
        for idx in range(1, len(rpts_opts)):
            if not quiet:
                dl_start = downloaded
                if download_audits - downloaded > 100:
                    downloaded = downloaded + 100
                    dl_end = downloaded
                else:
                    downloaded = downloaded + (download_audits % 100)
                    dl_end = downloaded

                sys.stdout.write("Downloading audits " + str(dl_start) + "-" + str(dl_end))
                sys.stdout.flush()
        
            # this needs to be here twice because the element can change between iterations!
            rpts_drop = Select(FAC.__find_tag_by_selector(drv, '#MainContent_ucA133SearchResults_ddlAvailZipTop', timeout))
            rpts_opts = rpts_drop.options
            opt = rpts_opts[idx]
            rpts_drop.select_by_visible_text(opt.text)

            FAC.__open_tag(drv, "#MainContent_ucA133SearchResults_btnDownloadZipTop", timeout)
            FAC.__wait_for_download(dir, timeout)

            if not quiet:
                if downloaded <= 100:
                    sys.stdout.write('  ')
                    
                sys.stdout.write('  done\n')
                sys.stdout.flush()

        # Extract downloaded archives
        zips = glob.glob(tmp + '/*.zip')
        for z in zips:
            if z != '.' and z != '..':
                zr = zipfile.ZipFile(z, 'r')
                zr.extractall(dir)
                zr.close()
                os.unlink(z)
                        
        # Clean up
        drv.close()
        display.stop()

        return audits_found
