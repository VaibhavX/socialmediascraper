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

#Final List of Social Media and ID Dictionary in a list
sm_sites_present = {}

target_sites = ["facebook", "twitter", "itunes" ,"play.google.com"]
target_keys =["facebook", "twitter", "ios", "google"]

#Function to Extract all Meta Tags and Check for the Social Media IDs
def check_meta(soup, sm_dict, target_check):
    #Cheking the Meta Tags First - High Probability of finding Facebook, Twitter and Apple ID as they are usually embedded in meta tags
    all_links = soup.find_all('meta')   
    for idx, sm_site in enumerate(target_sites):
        for link in all_links:
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
                        if split_list[-1] =="": #Condition to elimitate null if present
                            split_list.pop()  
                        sm_dict[sm_site] = split_list[-1] 
                        target_check[idx] = 1           
                if 'name' in link.attrs.keys():
                    if sm_site in link.attrs['name']:
                        if 'site' in link.attrs['name'] and link.attrs['content']!= "" and target_check[idx] ==0:
                            print('Found second', link.attrs['content'])
                            current_meta_content = link.attrs['content'].replace('@','')
                            if not current_meta_content.isascii(): #Checking for any Unicode character and remove it
                                current_meta_content = (current_meta_content.encode('ascii', 'ignore')).decode('utf-8')
                            sm_dict[sm_site]= current_meta_content.strip() #Removes any leading or trailing spaces
                            target_check[idx] = 1
                        
                        #Checking if Twitter Creator is present in name attribute
                        elif 'creator' in link.attrs['name'] and target_check[idx] ==0:
                            print("Twitter Creator Found", link.attrs['content'])
                            if sm_site == "twitter":
                                sm_dict[sm_site] = link.attrs['content'].replace('@','')
                                target_check[idx] = 1

                        #Checking only for Twitter Title is creator and site not present
                        elif 'title' in link.attrs['name'] and sm_site =="twitter" and target_check[idx] ==0:
                            if link.attrs['content']!="" and len(link.attrs['content'].split(" ")) == 1:
                                sm_dict[sm_site] = link.attrs['content']
                                target_check[idx] = 1
                                
                        #Checking for Itunes or Google Play Id in the meta
                        elif 'app' in link.attrs['name']:
                            print("Found App ID", link.attrs['content'], " ", link.attrs['name'])

                            #Extracting APP ID
                            meta_contents = link.attrs['content'].split(',')
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
                #For Exception Case of ID as content itself
                if 'property' in link.attrs.keys() and sm_site in link.attrs['property'] and 'title' in link.attrs['property'] and target_check[idx] == 0:
                    print("Found ID in property", current_meta_content)
                    if len(current_meta_content.split(" "))== 1:
                        sm_dict[sm_site] = current_meta_content
                        target_check[idx] = 1

    return sm_dict, target_check

#Function to check the <a> tags and the attribute 'href' for missing ID values and add to response if available
def check_href(soup, sm_dict, target_check):
    #Google IDs are usually available in HREF and also check for missing Tags
    all_tags = soup.find_all('a')
    for idx, sm_site in enumerate(target_sites):
        for tag in all_tags:
            if 'href' in tag.attrs.keys():
                if sm_site in tag.attrs['href'] and target_check[idx] == 0:
                    if sm_site =='play.google.com':
                        print("Found Google ID")
                        google_id = tag.attrs['href'].split('?')[-1]
                        google_id = google_id.split('&')[0] #if there are multiple arguments present select the portion with id
                        sm_dict['google'] = google_id.split('=')[-1]
                        target_check[idx] = 1
                    else:
                        if 'facebook.com' in tag.attrs['href'] or 'twitter.com' in tag.attrs['href']:
                            print("Found ID for {}".format(sm_site))
                            href_content = tag.attrs['href'].split('/')
                            if href_content[-1] == '':
                                href_content.pop()
                            if 'pages' in tag.attrs['href']:
                                href_content.pop()
                            final_id = href_content[-1]
                            if '?' in final_id:
                                final_id = final_id.split('?')[0]
                            if 'status' in tag.attrs['href']:
                                print("Incorrect URL picked")
                            else:
                                sm_dict[target_keys[idx]] = final_id
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
                #Checking Exception Case of having Apple ID in a URL not containing iTunes
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
    return sm_dict, target_check


#Function to Extract URL response and parse using a html parser
def html_parser(url_list):
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', \
            "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", \
                 "Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}

    for url in url_list['List of URL']:
        sm_dict={}
        try:
            response = requests.get(url, headers = headers, timeout=10)
        #Checking for all possible Exception errors
        except Timeout:
            print("Timeout has been raised")
            sm_sites_present[url] = sm_dict
            time.sleep(3)
            continue
        except requests.exceptions.TooManyRedirects:
            print("Too many redirects")
            sm_sites_present[url] = sm_dict
            time.sleep(3)
            continue
        except ConnectionError:
            print("Badly Formatted URL")
            sm_sites_present[url] = sm_dict
            time.sleep(3)
            continue
        except requests.exceptions.RequestException as e:
            sm_sites_present[url] = sm_dict
            print("Error Raised", e)
            time.sleep(3)
            continue

        #Parsing the response if no exception raised
        soup = BeautifulSoup(response.content, 'html.parser')
        
        target_check = [0,0,0,0] #Empty List to check if a ID is found (change to 1 if found)

        sm_dict, target_check = check_meta(soup, sm_dict, target_check) #Checking all meta tags for the ID first

        sm_dict, target_check = check_href(soup, sm_dict, target_check) #Checking all a tags for missing ID

        json_format = json.dumps(sm_dict, indent=4)
        print(json_format)
        print(target_check)
        sm_sites_present[url] = sm_dict

    print("Extraction Completed \n")
    return


def main():
    print("Main Function")

    #Read List of URL
    df = pd.read_csv('URL_List.csv')

    #Call Function to Extract URL response for the list
    html_parser(df)

    final_json_obj = json.dumps(sm_sites_present, indent=4)
    print("Final Result: {}".format(final_json_obj))

    #Writing the Final Result to a JSON FILE
    with open("results.json", "w") as outfile:
        outfile.write(final_json_obj)
    
    print("End of Main -- Program finsihed execution \n")



if __name__ == '__main__':
    main()