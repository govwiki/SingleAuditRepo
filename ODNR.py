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
import datetime
import glob
import math
import time
import sys


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


#################################################
# State
# Represents a U.S. state, territory or province
#################################################

class State(object):
    def __init__(self, data):
        self.long_name = data[2]
        self.short_name = data[0]
        self.fips = data[1]

    def get_name(self):
        return self.long_name

    def get_abbrev(self):
        return self.short_name

    def get_fips(self):
        return self.fips

    @staticmethod
    def get_all():
        sts = []
        for t in raw_state_data:
            st = State(t)
            sts.append(st)

        return sts
    
    @staticmethod
    def find_by_name(name):
        st = None
        for t in raw_state_data:
            if t[2].upper() == name.upper():
                st = State(t)

        return st

    @staticmethod
    def find_by_abbrev(abbrev):
        st = None
        for t in raw_state_data:
            if t[0] == abbrev.upper():
                st = State(t)

        return st

    @staticmethod
    def find_by_fips(fips):
        st = None
        for t in raw_state_data:
            if t[1] == fips:
                st = State(t)

        return st


#############################
# Report
# Base class for all reports
#############################
    
class Report(object):
    def __init__(self, id):
        self.id = id


########################################
# FederalAudit
# Represents an audit report from
# the Federal Audit Clearinghouse (FAC)
########################################
        
class FederalAudit(Report):
    def __init__(self, id):
        self.id = id

    def get_id(self):
        return self.id

    
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
    def fetch_audits(url, st, begin_date, end_date, quiet, timeout, dir):
        audits_found = []

        # Set up the virtual display
        display = Display(visible=0, size=(1024, 1024))
        display.start()

        # Use Google Chrome
        webopts = webdriver.ChromeOptions()
        webprefs = { 'download.default_directory' : dir }
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
        for idx in range(idx_end, (idx_begin + 1)):
            css_id = '#MainContent_UcSearchFilters_FYear_CheckableItems_' + str(idx)
            FAC.__open_tag(drv, css_id, timeout)
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
            
        # Select audits to download
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
        
        # Clean up
        drv.close()
        display.stop()

        return audits_found
