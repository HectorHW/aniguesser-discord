import youtube_search
#TODO


def search(query:str, N=5): #returns list[{title, link, id}]
    results =  youtube_search.YoutubeSearch(query, N).to_dict()
    #TODO return video duration
    return results



def format_results(results):
    tmp = []
    for i,item in enumerate(results):
        tmp.append(f"{i+1}. {item['title']}")
        
    return '\n'.join(tmp)




if __name__ == '__main__':
    s = input()
    print(search(s))