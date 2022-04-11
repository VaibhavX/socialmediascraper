import json
import requests
from bs4 import BeautifulSoup

url = 'http://www.zello.com'

response = requests.get(url)

target_sites = ['twitter.com', 'facebook.com']
sm_sites_present = []

soup = BeautifulSoup(response.content, 'html.parser')
all_links = soup.find_all('a', href = True)


for sm_site in target_sites:
    for link in all_links:
        if sm_site in link.attrs['href']:
            sm_sites_present.append(link.attrs['href'])

sm_sites_present = list(set(sm_sites_present))
print(sm_sites_present)


