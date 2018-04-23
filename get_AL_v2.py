# -*- coding: utf-8 -*-

import time
import os
import re
import json
import glob
import argparse
import configparser
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

Config = configparser.ConfigParser()
Config.read("/home/seraphina/Documents/CONTRACTS/UPWORK/PDF_CRAWLING/alabama_scraper/conf.ini")
proxy_url = 'http://kproxy.com'
url = "http://www.examiners.state.al.us/ReportSearch.aspx"
entities_list = []
unique_pdfs = []
counties = ['Autauga', 'Baldwin', 'Barbour', 'Bibb', 'Blount', 'Bullock', 'Butler', 'Calhoun', 'Chambers', 'Cherokee', 'Chilton', 'Choctaw', 'Clarke', 'Clay', 'Cleburne', 'Coffee', 'Colbert', 'Conecuh', 'Coosa', 'Covington', 'Crenshaw', 'Cullman', 'Dale', 'Dallas', 'DeKalb', 'Elmore', 'Escambia', 'Etowah', 'Fayette', 'Franklin', 'Geneva', 'Greene', 'Hale', 'Henry', 'Houston', 'Jackson', 'Jefferson', 'Lamar', 'Lauderdale', 'Lawrence', 'Lee', 'Limestone', 'Lowndes', 'Macon', 'Madison', 'Marengo', 'Marion', 'Marshall', 'Mobile', 'Monroe', 'Montgomery', 'Morgan', 'Perry', 'Pickens', 'Pike', 'Randolph', 'Russell', 'St. Clair', 'Shelby', 'Sumter', 'Talladega', 'Tallapoosa', 'Tuscaloosa', 'Walker', 'Washington', 'Wilcox', 'Winston']
cities = ['Abbeville', 'Adamsville', 'Addison', 'Akron', 'Alabaster', 'Albertville', 'Alexander', 'Aliceville', 'Allgood', 'Altoona', 'Andalusia', 'Anderson', 'Anniston', 'Arab', 'Ardmore', 'Argo', 'Ariton', 'Arley', 'Ashford', 'Ashland', 'Ashville', 'Athens', 'Atmore', 'Attalla', 'Auburn', 'Autaugaville', 'Avon', 'Babbie', 'Baileyton', 'Bakerhill[b]', 'Banks', 'Bay Minette', 'Bayou La Batre', 'Bear Creek', 'Beatrice', 'Beaverton', 'Belk', 'Benton', 'Berry', 'Bessemer', 'Billingsley', 'Birmingham', 'Black', 'Blountsville', 'Blue Springs', 'Boaz[c]', 'Boligee', 'Bon Air', 'Brantley', 'Brent', 'Brewton', 'Bridgeport', 'Brighton', 'Brilliant', 'Brookside', 'Brookwood', 'Brundidge', 'Butler', 'Calera', 'Camden', 'Camp Hill', 'Carbon Hill', 'Cardiff', 'Carolina', 'Carrollton', 'Castleberry', 'Cedar Bluff', 'Center Point[d]', 'Centre', 'Centreville', 'Chatom', 'Chelsea', 'Cherokee', 'Chickasaw', 'Childersburg', 'Citronelle', 'Clanton', 'Clay[e]', 'Clayhatchee', 'Clayton', 'Cleveland', 'Clio', 'Coaling', 'Coffee Springs', 'Coffeeville', 'Coker', 'Collinsville', 'Colony', 'Columbia', 'Columbiana', 'Coosada', 'Cordova', 'Cottonwood', 'County Line', 'Courtland', 'Cowarts', 'Creola', 'Crossville', 'Cuba', 'Cullman', 'Cusseta[f]', 'Dadeville', 'Daleville', 'Daphne', 'Dauphin Island', 'Daviston', 'Dayton', 'Deatsville', 'Decatur', 'Demopolis', 'Detroit', 'Dodge', 'Dora', 'Dothan', 'Dale County', 'Double Springs', 'Douglas', 'Dozier', 'Dutton', 'East Brewton', 'Eclectic', 'Edwardsville', 'Elba', 'Elberta', 'Eldridge', 'Elkmont', 'Elmore', 'Emelle', 'Enterprise', 'Epes', 'Ethelsville', 'Eufaula', 'Eutaw', 'Eva', 'Evergreen', 'Excel', 'Fairfield', 'Fairhope', 'Fairview', 'Falkville', 'Faunsdale', 'Fayette', 'Five Points', 'Flomaton', 'Florala', 'Florence', 'Foley', 'Forkland', 'Fort Deposit', 'Fort Payne', 'Franklin', 'Frisco', 'Fruithurst', 'Fulton', 'Fultondale', 'Fyffe', 'Gadsden', 'Gainesville', 'Gantt', 'Garden', 'Gardendale', 'Gaylesville', 'Geiger', 'Geneva', 'Georgiana', 'Geraldine', 'Gilbertown', 'Glen Allen', 'Glencoe', 'Glenwood', 'Goldville', 'Good Hope', 'Goodwater', 'Gordo', 'Gordon', 'Gordonville', 'Goshen', 'Grant', 'Graysville', 'Greensboro', 'Greenville', 'Grimes', 'Grove Hill', 'Guin', 'Gulf Shores', 'Guntersville', 'Gurley', 'Gu-Win', 'Hackleburg', 'Haleburg', 'Haleyville', 'Hamilton', 'Hammondville', 'Hanceville', 'Harpersville', 'Hartford', 'Hartselle', 'Hayden', 'Hayneville', 'Headland', 'Heath', 'Heflin', 'Helena', 'Henagar', 'Highland Lake', 'Hillsboro', 'Hobson', 'Hodges', 'Hokes Bluff', 'Holly Pond', 'Hollywood', 'Homewood', 'Hoover', 'Horn Hill', 'Hueytown', 'Huntsville', 'Limestone County', 'Morgan', 'Hurtsboro', 'Hytop', 'Ider', 'Indian Springs Village', 'Irondale', 'Jackson', "Jackson's Gap", 'Jacksonville', 'Jasper', 'Jemison', 'Kansas', 'Kellyton[g]', 'Kennedy', 'Killen', 'Kimberly', 'Kinsey', 'Kinston', 'La Fayette', 'Lake View', 'Lakeview', 'Lanett', 'Langston', 'Leeds', 'St. Clair County', 'Leesburg', 'Leighton', 'Lester', 'Level Plains', 'Lexington', 'Libertyville', 'Lincoln', 'Linden', 'Lineville', 'Lipscomb', 'Lisman', 'Littleville', 'Livingston', 'Loachapoka', 'Lockhart', 'Locust Fork', 'Louisville', 'Lowndesboro', 'Loxley', 'Luverne', 'Lynn', 'Madison', 'Madrid', 'Magnolia Springs [h]', 'Malvern', 'Maplesville', 'Margaret', 'Marion', 'Maytown', 'McIntosh', 'McKenzie', 'McMullen', 'Memphis', 'Mentone', 'Midfield', 'Midland', 'Midway', 'Millbrook', 'Millport', 'Millry', 'Mobile', 'Monroeville', 'Montevallo', 'Montgomery', 'Moody', 'Mooresville', 'Morris', 'Mosses', 'Moulton', 'Moundville', 'Mount Vernon', 'Mountain Brook', 'Mulga', 'Munford[i]', 'Muscle Shoals', 'Myrtlewood', 'Napier Field', 'Natural Bridge', 'Nauvoo', 'Nectar', 'Needham', 'New Brockton', 'New Hope', 'New Site', 'Newbern', 'Newton', 'Newville', 'North Courtland', 'North Johns', 'Northport', 'Notasulga', 'Oak Grove', 'Oak Hill', 'Oakman', 'Odenville[j]', 'Ohatchee', 'Oneonta', 'Onycha', 'Opelika', 'Opp', 'Orange Beach', 'Orrville', 'Owens Cross Roads', 'Oxford', 'Ozark', 'Paint Rock', 'Parrish', 'Pelham', 'Pell', 'Pennington', 'Perdido Beach[k]', 'Petrey', 'Phenix', 'Phil Campbell', 'Pickensville', 'Piedmont', 'Pike Road', 'Pinckard', 'Pine Apple', 'Pine Hill', 'Pine Ridge', 'Pinson[l]', 'Pisgah', 'Pleasant Grove', 'Pleasant Groves', 'Pollard', 'Powell', 'Prattville', 'Priceville', 'Prichard', 'Providence', 'Ragland', 'Rainbow', 'Rainsville', 'Ranburne', 'Red Bay', 'Red Level', 'Reece', 'Reform', 'Rehobeth', 'Repton', 'Ridgeville', 'River Falls', 'Riverside', 'Riverview', 'Roanoke', 'Robertsdale', 'Rockford', 'Rogersville', 'Rosa', 'Russellville', 'Rutledge', 'St. Florian', 'Samson', 'Sand Rock', 'Sanford', 'Saraland', 'Sardis', 'Satsuma', 'Scottsboro', 'Section', 'Selma', 'Sheffield', 'Shiloh', 'Shorter', 'Silas', 'Silverhill', 'Sipsey', 'Skyline', 'Slocomb', 'Smiths Station[m]', 'Snead', 'Somerville', 'South Vinemont', 'Southside', 'Spanish Fort', 'Springville', 'Steele', 'Stevenson', 'Sulligent', 'Sumiton', 'Summerdale', 'Susan Moore', 'Sweet Water', 'Sylacauga', 'Sylvan Springs', 'Sylvania', 'Talladega Springs', 'Talladega', 'Tallassee', 'Tarrant', 'Taylor', 'Thomaston', 'Thomasville', 'Thorsby', 'Toxey', 'Trafford', 'Triana', 'Trinity', 'Troy', 'Trussville', 'Tuscaloosa', 'Tuscumbia', 'Tuskegee', 'Twin[n]', 'Union Grove', 'Union Springs', 'Union', 'Uniontown', 'Valley', 'Valley Grande[o]', 'Valley Head', 'Vance', 'Vernon', 'Vestavia Hills', 'Vina', 'Vincent', 'St. Clair County', 'Vredenburgh', 'Wadley', 'Waldo', 'Walnut Grove', 'Warrior', 'Waterloo', 'Waverly', 'Weaver', 'Webb', 'Wedowee', 'West Blocton', 'West Jefferson', 'West Point', 'Westover[p]', 'Wetumpka', 'White Hall', 'Wilsonville', 'Wilton', 'Winfield', 'Woodland', 'Woodstock', 'Woodville', 'Yellow Bluff', 'York']


# get start time
startTime = datetime.now()

with open('AL_params.txt', 'r') as fp: 
    dparameters = json.load(fp)

#month/day/year
rangeFrom = dparameters["rangeFrom"]
rangeTo = dparameters["rangeTo"]
print(rangeFrom, rangeTo)


def init_driver():
    print("start time is: ", startTime)
    print("initiallising the driver...")
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=options)
    driver.wait = WebDriverWait(driver, 5)
    return driver

def scrape(driver):
     #---------- FOR PROXY ONLY:- Enable line above and disable this code block---------------
    # driver.get(proxy_url)
    # driver.find_element_by_xpath('//*[@id="maintextfield"]').click()
    # time.sleep(2)
    # driver.find_element_by_xpath('//*[@id="maintextfield"]').send_keys(url)
    # driver.find_element_by_xpath('//*[@id="surfbar"]/input[2]').click()
    # time.sleep(2)
    #----------------- disable this code block if you are not using PROXY -------------------

    # disable this if using proxy
    driver.get("http://www.examiners.state.al.us/ReportSearch.aspx")

    driver.find_element_by_id("PageContent_txtFiled1").send_keys(rangeFrom)
    driver.find_element_by_id("PageContent_txtFiled2").send_keys(rangeTo)
    time.sleep(2)
    driver.find_element_by_id('PageContent_btnSearch').click()
    time.sleep(2)


    def process_data():
        print("processing data")

        # define global variables
        global records
        global reports
        global released_dates
        global entities
        global locations
        global audit_periods
        global pdfs

        # get data
        records = [record.text for record in driver.find_elements_by_xpath('//table[@class="GridViewStyle"]//tr')]
        records = records[1:-2]
        reports = [report.text for report in driver.find_elements_by_xpath('//table[@class="GridViewStyle"]//tr/td[1]')]
        reports = reports[:-2]
        released_dates = [date.text for date in driver.find_elements_by_xpath('//table[@class="GridViewStyle"]//tr/td[2]')]
        released_dates = released_dates[:-1]
        entities = [entity.text for entity in driver.find_elements_by_xpath('//table[@class="GridViewStyle"]//tr/td[3]')]
        entities = entities[:-1]
        locations = [location.text for location in driver.find_elements_by_xpath('//table[@class="GridViewStyle"]//tr/td[4]')]
        locations = locations[:-1]
        audit_periods = [period.text for period in driver.find_elements_by_xpath('//table[@class="GridViewStyle"]//tr/td[5]')]
        audit_periods = audit_periods[:-1]
        pdfs = [pdf for pdf in driver.find_elements_by_xpath('//input[@value="View"]')]
        return records, reports, released_dates, entities, locations, audit_periods, pdfs

    def process_pdfs():
        print("processing pdfs")
        #1 process pdfs
        for i, pdf in enumerate(pdfs):
            try: 
                pdf.click()
                file = glob.glob('/home/seraphina/Downloads/*') # * means all if need specific format then *.csv
                latest_file = max(file, key=os.path.getctime)
                state = 'AL'
                entity = entities[i]
                print(entity)
                year = released_dates[i]
                fiscal_year = re.match('\d{1,2}\/\d{1,2}\/(?:17|18|19|20)\d{2}\s*to\s*\d{1,2}\/\d{1,2}\/((?:17|18|19|20)\d{2})', audit_periods[i]).group(1)
                county = [county for county in counties if county in entity]
                city = [city for city in cities if city in entity]

                #2 rename and allocate files to folders
                # a) schools
                if re.match('.*?(school\s*(?:board|commissioners)|.*?Board\s*of\s*Education).*', entity, re.IGNORECASE):
                    PATH = '/home/seraphina/Documents/CONTRACTS/UPWORK/PDF_CRAWLING/School_District/'
                    print("# School District")
                    new_name = state + ' ' + entity + ' ' + fiscal_year + '.pdf'
                    if new_name not in unique_pdfs:
                        os.rename(latest_file, PATH + new_name)
                        unique_pdfs.append(new_name)

                # b) colleges
                elif re.match('.*?(?:technical|community).*?(?:college|university).*', entity, re.IGNORECASE):
                    PATH = '/home/seraphina/Documents/CONTRACTS/UPWORK/PDF_CRAWLING/Community_College_District/'
                    print("# Community College District")
                    new_name = state + ' ' + entity + ' ' + fiscal_year + '.pdf'
                    if new_name not in unique_pdfs:
                        os.rename(latest_file, PATH + new_name)
                        unique_pdfs.append(new_name)

                # c) special districts
                elif re.match('.*(?:Agency|Authorit(?:y|ies)|Special\s*(?:District|Report))', entity, re.IGNORECASE):
                    PATH = '/home/seraphina/Documents/CONTRACTS/UPWORK/PDF_CRAWLING/Special_District/'
                    print("# Special District")
                    new_name = state + ' ' + entity + ' ' + fiscal_year + '.pdf'
                    if new_name not in unique_pdfs:
                        os.rename(latest_file, PATH + new_name)
                        unique_pdfs.append(new_name)

                # d) general government
                #i test for county - name should end with name for the county - i.e. CA Alameda County 2017.pdf
                elif county != []:
                    PATH = '/home/seraphina/Documents/CONTRACTS/UPWORK/PDF_CRAWLING/General_Purpose/'
                    county = county[0]
                    print("#i General Purpose")
                    print("#ii county", county)
                    new_name = state + ' ' + entity + ' ' + 'County' + ' ' + fiscal_year + '.pdf'
                    if new_name not in unique_pdfs:
                        os.rename(latest_file, PATH + new_name)
                        unique_pdfs.append(new_name)
                #ii test for state financial statements - i.e. name as -  MO State of Missouri 2017.pdf
                elif re.match('.*?(?:Financial\s*Report\s*\(CAFR\)|Financial\s*Statements|CAFR).*?(?:State\s*of\s*Alabama|All\s*Counties).*', entity, re.IGNORECASE):
                    PATH = '/home/seraphina/Documents/CONTRACTS/UPWORK/PDF_CRAWLING/General_Purpose/'
                    print("#i General Purpose")
                    print("#ii state financial statement")
                    new_name = state + ' ' + 'State of Alabama' + ' ' + fiscal_year + '.pdf'
                    if new_name not in unique_pdfs:
                        os.rename(latest_file, PATH + new_name)
                        unique_pdfs.append(new_name)
                elif city != []:
                    PATH = '/home/seraphina/Documents/CONTRACTS/UPWORK/PDF_CRAWLING/General_Purpose/'
                    city = city[0]
                    print("#i General Purpose")
                    print("#ii city", city)
                    new_name = state + ' ' + entity + ' ' + fiscal_year + '.pdf'
                    if new_name not in unique_pdfs:
                        os.rename(latest_file, PATH + new_name)
                        unique_pdfs.append(new_name)

                # e) non-profit
                else:
                    PATH = '/home/seraphina/Documents/CONTRACTS/UPWORK/PDF_CRAWLING/Non_Profit/'
                    print("#Non-Profit")
                    new_name = state + ' ' + entity + ' ' + fiscal_year + '.pdf'
                    if new_name not in unique_pdfs:
                        os.rename(latest_file, PATH + new_name)
                        unique_pdfs.append(new_name)
            except Exception:
                print("failed to download file!")
                continue


    results = [record.text for record in driver.find_elements_by_xpath('//table[@class="GridViewStyle"]//tr')]
    
    if results[0] == 'No Records match your query.':
        print("no records!")
    else:
        # test for pages
        pages = results[-1]
        print("pages?", pages)

        ### process p1 ###
        print("processing p1")
        process_data()
        process_pdfs()

        if re.match('1(\s{1}\d+)+', pages):
            pages_pattern = re.match('1(\s{1}\d+)+', pages).group(0)
            print(pages_pattern)
            pages = pages.split(' ')
            try:
                # process p2
                print("processing p2")
                p = 2
                page = '//*[@id="PageContent_GridView1"]//tr/td[' + str(p) + ']/a'
                driver.find_element_by_xpath(page).click()
                # get data
                process_data()
                # process pdfs
                process_pdfs()
            except Exception:
                print("failed to find page 2!")
                pass
        
            if len(pages) > 2:
                
                for p in pages[2:]:
                    print("processing page", p)
                    page = '//*[@id="PageContent_GridView1"]//tr/td[' + str(p) + ']/a'
                    test = driver.find_element_by_xpath(page).get_attribute('href')
                    test = re.match('javascript:__doPostBack.*?(Page\$\d+).*', str(test)).group(1)
                    try:
                        driver.find_element_by_xpath(page).click()
                        # get data
                        process_data()
                        # process pdfs
                        process_pdfs()
                    except Exception:
                        print("the link didn't work...")
                        pass
        else:
           print("only one page of results!")
           pass


if __name__ == "__main__":
    driver = init_driver()
    scrape(driver)
    time.sleep(5)
    driver.quit()
    print("total runtime is: ", datetime.now() - startTime)
