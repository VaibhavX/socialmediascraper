''' Python Scraper to Extract Social Media Handles from Website URL
    This includes Twitter and Facebook and if there any app store ID - Google Play or Apple.
    This code should handle redirects, timeouts and badly formatted urls'''
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

#Reading the list of URL from a CSV File -- makes is scalable to address 'n' number of URL
df = pd.read_csv('URL_List.csv')

print(df['List of URL'])

url = 'http://www.zello.com'
url2 ="http://zynga.com"
url3 ="https://www.appannie.com"
url4 ="https://www.data.ai"
url5 ="https://www.zello.com/downloads/android/"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', \
            "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", \
                 "Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}
response = requests.get(url5, headers = headers, timeout=10)
#print(response.text)

#time.sleep(3)

#r = requests.get(response.headers['Location'])
#print(r.status_code)



target_sites = ["facebook", "twitter", "itunes" ,"play.google.com"]
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
                if sm_site in link.attrs['name']:
                    if 'site' in link.attrs['name']:
                        print('Found second', link.attrs['content'])
                        current_meta_content = link.attrs['content'].replace('@','')
                        sm_dict[sm_site]= current_meta_content
                    
                    #Checking for Itunes or Google Play Id in the meta
                    elif 'app' in link.attrs['name']:
                        print("Found App ID", link.attrs['content'])

                        #Extracting APP ID
                        meta_contents = link.attrs['content'].split(',')
                        for item in meta_contents:
                            if "app-id" in item:
                                app_id = item.split("=")[-1]
                                if sm_site =="itunes":
                                    sm_dict['ios'] = app_id
                                else:
                                    sm_dict['google'] = app_id

#Checking Separately for Google ID as they usually are in href
all_tags = soup.find_all('a')
for tag in all_tags:
    if 'play.google.com' in tag.attrs['href']:
        print("Found Google ID")
        google_id = tag.attrs['href'].split('?')[-1]
        sm_dict['google'] = google_id.split('=')[-1]
            
sm_sites_present.append(sm_dict)

#sm_sites_present = list(set(sm_sites_present))
print(sm_sites_present)

print(type(sm_dict))

#json_format = json.dumps(sm_dict)
#print(type(json_format))