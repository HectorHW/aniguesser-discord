from downloader import flatten_playlist
from utils import Database
import re
if __name__ == '__main__':
    data = './data.csv'
    records = flatten_playlist('https://www.youtube.com/playlist?list=PLnAOXbQBAoxXP455AYiXF79yuMG2wfyJ8')
    print(records)
    def is_opening(s):
        return 'opening' in s['name'].lower() or re.search(r'\bop\b', s['name'].lower()+' ')
    records = list(filter(is_opening, records))
    print(records)
    d = Database(data)
    d.data+=records
    d.store()