import urllib
import requests
from bs4 import BeautifulSoup
import re
#TODO

def is_video(data):
    link = 'https://youtube.com' + data.contents[0]['href']
    return not 'list' in link

def _extract_results(data):
    try:
        title = data.contents[0].text
        link = 'https://youtube.com' + data.contents[0]['href']
        duration = data.contents[1].text
        duration = re.search(r'((\d+:)?\d+:\d+)', duration).group(0)
        return {"name": title, "link":link, 'duration':duration}
    except Exception as e:
        print(data)
        raise e
def search(query:str, N=5):
    r = requests.get('https://youtube.com/results', {'search_query':query})
    webpage = r.text
    r.close()
    soup = BeautifulSoup(webpage, 'html.parser')
    results = soup.find_all('h3', **{'class':'yt-lockup-title'})
    results = list(filter(is_video, results))[:N]
    return list(map(_extract_results, results))

def format_results(results):
    tmp = []
    for i,item in enumerate(results):
        tmp.append(f"{i+1}. {item['name']} [{item['duration']}]")

    return '\n'.join(tmp)




if __name__ == '__main__':
    s = input()
    print(search(s))