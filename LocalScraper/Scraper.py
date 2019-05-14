import pandas as pd
from googlesearch import search

# read test file and get first url to be scrapped.
df = pd.read_excel("Test.xlsx")

#Create the search term
targeturl=df.iloc[0,2]+df.iloc[0,3]
state=df.iloc[0,0]
name=df.iloc[0,1]

#Google url save it into a csv file   
for url in search(targeturl, tld='com', stop=5):
    #write results to a CSV
    file=open("output.csv", 'w')
    #for r in url:
    file.write(url+','+state+','+name)
    file.close()
    # print all the results
    print(url)
