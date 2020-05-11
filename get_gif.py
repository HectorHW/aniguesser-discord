import requests
import json
import random
API_KEY = open('tenor_token.txt').read().strip()
def get_gif_links(limit=20, query='evangelion'):
    search_term = query

# get the top 8 GIFs for the search term
    r = requests.get("https://api.tenor.com/v1/random?q=%s&key=%s&limit=%s" % (search_term, API_KEY, limit))
    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        top_gifs = json.loads(r.content)
        return top_gifs
    else:
        raise PermissionError

def get_random_gif(limit=1, query='evangelion'):
    links = get_gif_links(limit, query)
    results = links['results']
    result = random.choice(results)
    return result['media'][0]['gif']['url']


if __name__ == '__main__':
    i = 2
    print(get_random_gif(query=input()))