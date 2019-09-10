import subprocess
import json
import urllib.request
from bs4 import BeautifulSoup
#TODO
def top5(query:str):
    query = urllib.parse.quote(query)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        print('https://www.youtube.com' + vid['href'])

if __name__ == '__main__':
    s = input()
    print(top5(s))