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
#import cloudscraper


#Reading the list of URL from a CSV File -- makes is scalable to address 'n' number of URL
#df = pd.read_csv('URL_List.csv')
df = pd.read_csv('Testurl.csv')
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
sm_sites_present = {}

target_sites = ["facebook", "twitter", "itunes" ,"play.google.com"]
target_keys =["facebook", "twitter", "ios", "google"]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', \
            "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", \
                 "Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}

for url in df['List of URL']:
    try:
        response = requests.get(url, headers = headers, timeout=10)
    except Timeout:
        print("Timeout has been raised")
        sm_sites_present[url] ={}
        time.sleep(3)
        continue
    except requests.exceptions.TooManyRedirects:
        print("Too many redirects")
        sm_sites_present[url] ={}
        time.sleep(3)
        continue
    except ConnectionError:
        print("Badly Formatted URL")
        sm_sites_present[url] ={}
        time.sleep(3)
        continue
    except requests.exceptions.RequestException as e:
        sm_sites_present[url] ={}
        print("Error Raised", e)
        time.sleep(3)
        continue
    
    #if response.status_code == 403:
    #    print("CloudFare Issue")
    #    scraper = cloudscraper.create_scraper()
    #    print(scraper.get(url).status_code)

    sm_dict={} #Empty Dictionary to create a json response for a URL
    target_check = [0,0,0,0]
    
    soup = BeautifulSoup(response.content, 'html5lib')

    #Cheking the Meta Tags First - High Probability of finding Facebook, Twitter and Apple ID as they are usually embedded in meta tags
    all_links = soup.find_all('meta')   
    for idx, sm_site in enumerate(target_sites):
        for link in all_links:
            #print(link.attrs.keys())
            #print("Target Looking: ", sm_site)
            #print(idx)
            if 'content' in link.attrs.keys(): 
                current_meta_content = link.attrs['content']
                if sm_site in current_meta_content and target_check[idx] ==0:
                    print('Found', current_meta_content)
                    if sm_site =="facebook" and "facebook.com/" not in link.attrs['content']:
                        print("Incorrect Facebook URL")
                    elif sm_site =='twitter' and "twitter.com/" not in link.attrs['content']:
                        print("Incorrect Twitter URL")
                    else:
                        split_list = current_meta_content.split('/')
                        if split_list[-1] =="":
                            split_list.pop() 
                        sm_dict[sm_site] = split_list[-1] 
                        target_check[idx] = 1           
                #print(link.attrs['content'])
                if 'name' in link.attrs.keys():
                    if sm_site in link.attrs['name']:
                        if 'site' in link.attrs['name'] and target_check[idx] ==0:
                            print('Found second', link.attrs['content'])
                            current_meta_content = link.attrs['content'].replace('@','')
                            if not current_meta_content.isascii():
                                current_meta_content = (current_meta_content.encode('ascii', 'ignore')).decode('utf-8')
                            sm_dict[sm_site]= current_meta_content.strip()
                            print(sm_dict)
                            target_check[idx] = 1
                        
                        #Checking if Twitter Creator is present in name attribute
                        elif 'creator' in link.attrs['name'] and target_check[idx] ==0:
                            print("Twitter Creator Found", link.attrs['content'])
                            if sm_site == "twitter":
                                sm_dict[sm_site] = link.attrs['content'].replace('@', '')
                                target_check[idx] = 1

                        #Checking for Itunes or Google Play Id in the meta
                        elif 'app' in link.attrs['name']:
                            print("Found App ID", link.attrs['content'], " ", link.attrs['name'])

                            #Extracting APP ID
                            meta_contents = link.attrs['content'].split(',')
                            #print(meta_contents, idx)
                            for item in meta_contents:
                                print(item)
                                if len(meta_contents) == 1 and 'id' in link.attrs['name']:
                                    if 'iphone' in link.attrs['name'] or 'ipad' in link.attrs['name'] and target_check[2] == 0:
                                        sm_dict['ios'] = item
                                        target_check[2] = 1
                                    elif 'googleplay' in link.attrs['name'] and target_check[3] == 0:
                                        sm_dict['google'] = item
                                        target_check[3] = 1
                                if "app-id" in item and target_check[idx] ==0:
                                    app_id = item.split("=")[-1]
                                    if sm_site =="itunes":
                                        sm_dict['ios'] = app_id
                                        target_check[idx]=1
                                    else:
                                        sm_dict['google'] = app_id
                                        target_check[idx] =1

        #Checking Separately for Google ID as they usually are in <a> tags inside href attribute that takes you to play.google.com
        all_tags = soup.find_all('a')
        for tag in all_tags:
            #print(tag)
            if 'href' in tag.attrs.keys():
                #print("Checking")
                #print(sm_site)
                #print(tag.attrs['href'])
                if sm_site in tag.attrs['href'] and target_check[idx] == 0:
                    print('Checking inside')
                    print(sm_site, tag.attrs['href'])
                    if sm_site =='play.google.com':
                        print("Found Google ID")
                        print(tag.attrs['href'])
                        google_id = tag.attrs['href'].split('?')[-1]
                        google_id = google_id.split('&')[0]
                        sm_dict['google'] = google_id.split('=')[-1]
                        target_check[idx] = 1
                    else:
                        if 'facebook.com' in tag.attrs['href'] or 'twitter.com' in tag.attrs['href']:
                            print("Found ID here for {}".format(sm_site))
                            #print(tag.attrs['href'])
                            href_content = tag.attrs['href'].split('/')
                            #print(href_content)
                            if href_content[-1] == '':
                                href_content.pop()
                            #print(href_content)
                            if 'pages' in tag.attrs['href']:
                                href_content.pop()
                            sm_dict[target_keys[idx]] = href_content[-1]
                            target_check[idx] = 1
                        elif 'itunes.apple.com' in tag.attrs['href']:
                            print("Apple ID found for {}".format(sm_site))
                            apple_id = tag.attrs['href'].split('/')[-1]
                            if 'id' in apple_id:
                                apple_id = apple_id[2:]
                            if '?' in apple_id:
                                apple_id = apple_id.split('?')[0]
                            sm_dict[target_keys[idx]] = apple_id 
                            target_check[idx] = 1
                if 'apple.com' in tag.attrs['href'] and target_check[2] == 0:
                    print("Found Apple Link", tag.attrs['href'])
                    apple_id = tag.attrs['href'].split('/')[-1]
                    if 'id' in apple_id:
                        apple_id = apple_id[2:]
                    if '?' in apple_id:
                        apple_id = apple_id.split('?')[0]
                    if apple_id[-1] == '#':
                        apple_id = apple_id[:-1]
                    sm_dict['ios'] = apple_id
                    target_check[2] = 1

        
        find_fb = soup.find_all('div')
        #print(find_fb)
    
            
    json_format = json.dumps(sm_dict, indent=4)
    print(json_format)
    print(target_check)
    sm_sites_present[url] = sm_dict

final_json_obj = json.dumps(sm_sites_present, indent=4)
print("Final List: \n", final_json_obj)


with open("results.json", "w") as outfile:
    outfile.write(final_json_obj)