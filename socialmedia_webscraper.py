''' Python Scraper to Extract Social Media Handles from Website URL
    This includes Twitter and Facebook and if there any app store ID - Google Play or Apple.
    This code should handle redirects, timeouts and badly formatted urls'''
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from requests.exceptions import Timeout
from requests.exceptions import ConnectionError


#Reading the list of URL from a CSV File -- makes is scalable to address 'n' number of URL
df = pd.read_csv('URL_List.csv')
#print(df['List of URL'])  #Uncomment this command to test the list of URL present as input

'''
#To use on individual URL Tests
url = 'http://www.zello.com'
url2 ="http://zynga.com"
url3 ="https://www.appannie.com"
url4 ="https://www.data.ai"
url5 ="https://www.zello.com/downloads/android/"
'''

#Final List of Social Media and ID Dictionary in a list
sm_sites_present = []

target_sites = ["facebook", "twitter", "itunes" ,"play.google.com"]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', \
            "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", \
                 "Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}

for url in df['List of URL']:
    try:
        response = requests.get(url, headers = headers, timeout=10)
    except Timeout:
        print("Timeout has been raised")
        sm_sites_present.append(json.dumps({}, indent=4))
        time.sleep(3)
        continue
    except requests.exceptions.TooManyRedirects:
        print("Too many redirects")
        sm_sites_present.append(json.dumps({}, indent=4))
        time.sleep(3)
        continue
    except ConnectionError:
        print("Badly Formatted URL")
        sm_sites_present.append(json.dumps({}, indent=4))
        time.sleep(3)
        continue
    except requests.exceptions.RequestException as e:
        sm_sites_present.append(json.dumps({}, indent=4))
        print("Error Raised", e)
        time.sleep(3)
        continue
    
    sm_dict={} #Empty Dictionary to create a json response for a URL
    
    soup = BeautifulSoup(response.content, 'html.parser')

    #Cheking the Meta Tags First - High Probability of finding Facebook, Twitter and Apple ID as they are usually embedded in meta tags
    all_links = soup.find_all('meta')   
    for sm_site in target_sites:
        for link in all_links:
            #print(link.attrs.keys())
            #print("Target Looking: ", sm_site)
            if 'content' in link.attrs.keys(): 
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

    #Checking Separately for Google ID as they usually are in <a> tags inside href attribute that takes you to play.google.com
    all_tags = soup.find_all('a')
    for tag in all_tags:
        if 'href' in tag.attrs.keys() and 'play.google.com' in tag.attrs['href']:
            print("Found Google ID")
            google_id = tag.attrs['href'].split('?')[-1]
            sm_dict['google'] = google_id.split('=')[-1]
            
    json_format = json.dumps(sm_dict, indent=4)
    print(json_format)
    sm_sites_present.append(json_format)

print("Final List: \n", sm_sites_present)
