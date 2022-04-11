''' Python Scraper to Extract Social Media Handles from Website URL
    This includes Twitter and Facebook and if there any app store ID - Google Play or Apple.
    This code should handle redirects, timeouts and badly formatted urls'''
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd

#Reading the list of URL from a CSV File -- makes is scalable to address 'n' number of URL
df = pd.read_csv('URL_List.csv')

print(df['List of URL'])

url = 'http://www.zello.com'

response = requests.get(url)

target_sites = ["facebook", "twitter"]
sm_sites_present = []

soup = BeautifulSoup(response.content, 'html.parser')
all_links = soup.find_all('meta')
#print(all_links)


sm_dict={}
for sm_site in target_sites:
    for link in all_links:
        #print(link.attrs.keys())
        #print("Target Looking: ", sm_site)
        if 'content' in link.attrs.keys(): # & sm_site in link.attrs['content']:
            current_meta_content = link.attrs['content']
            if sm_site in current_meta_content:
                print('Found', current_meta_content)
                split_list = current_meta_content.split('/') 
                sm_dict[sm_site] = split_list[-1]            
            #print(link.attrs['content'])
            if 'name' in link.attrs.keys():
                if sm_site in link.attrs['name'] and 'site' in link.attrs['name']:
                    print('Found second', link.attrs['content'])
                    current_meta_content = link.attrs['content'].replace('@','')
                    sm_dict[sm_site]= current_meta_content
            
sm_sites_present.append(sm_dict)

#sm_sites_present = list(set(sm_sites_present))
print(sm_sites_present)
