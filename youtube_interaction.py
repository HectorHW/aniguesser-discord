import requests
import json
import isodate
from typing import List
import math
import html
YT_API_KEY = open('youtube_api_key.txt').read().strip()

def get_video_data(video_id:str):
    string = "https://www.googleapis.com/youtube/v3/videos?id=%s&key=%s&part=contentDetails" % (
        video_id, YT_API_KEY
    )
    with requests.get(string) as response:
        answer = json.loads(response.text)
    return answer

def get_video_list_duration(video_id_list: List[str]) -> dict: # id:duration
    data = []
    for slicenum in range(math.ceil((len(video_id_list)/60))):

        data += get_video_data(','.join(video_id_list[slicenum*60:slicenum*60 + 60]))['items']
    durations = {row['id']:str(isodate.parse_duration(row['contentDetails']['duration'])) for row in data}
    return durations

def get_video_duration(video_id:str) -> str: # throws IndexError
    return str(isodate.parse_duration(get_video_data(video_id)['items'][0]['contentDetails']['duration']))

def search_youtube(search_query:str, max_results:int = 10) -> List[dict]: # {id, title, duration}

    string = "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=%d&q=%s&type=video&key=%s" % (
        max_results, search_query, YT_API_KEY
    )
    with requests.get(string) as response:
        answer:dict = json.loads(response.text)['items']
    results = [{'id':row['id']['videoId'], 'title':html.unescape(row['snippet']['title'])  } for row in answer]
    ids = [row['id'] for row in results]

    durations = get_video_list_duration(ids)
    results = [{'id':rec['id'], 'title':rec['title'], 'duration':durations.get(rec['id'], 'UNK')} for rec in results]

    return results


if __name__ == '__main__':
    print(search_youtube(input()))
        
    
