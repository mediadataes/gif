from typing import Union, Iterable


# Not using Yahoo since it requires additional steps
SEARCH_GENERAL = ["https://www.google.com/search?q=$0",
                "https://duckduckgo.com/?q=$0",
                "https://www.bing.com/search?q=$0"]

SEARCH_IMAGES = ["https://www.google.com/search?tbm=isch&q=$0",
                "https://duckduckgo.com/?iax=images&ia=images&q=$0",
                "https://www.bing.com/images/search?q=$0"]

SEARCH_VIDEOS = ["https://www.bing.com/videos/search?q=$0",
                "https://duckduckgo.com/?iax=videos&ia=videos&q=$0",    
                "https://www.google.com/search?tbm=vid&q=$0",
                "https://www.youtube.com/results?search_query=$0",
                "https://www.twitch.tv/search?term=$0&type=videos"]
                
SEARCH_NEWS = ["https://www.google.com/search?tbm=nws&q=$0",
                "https://www.bing.com/news/search?q=$0",
                "https://duckduckgo.com/?iar=news&ia=news&q=$0"]

SEARCH_SHOPPING = ["https://www.google.com/search?tbm=shop&q=$0",]

SEARCH_MAPS = ["https://duckduckgo.com/?iaxm=maps&ia=web&q=$0",
                "https://www.google.com/maps/search/$0/"]

SEARCH_SOCIAL = ["https://twitter.com/search?q=$0",
                "https://facebook.com/public/$0",
                "https://www.google.com/search?q=$0+site%3Ainstagram.com",
                "https://duckduckgo.com/?q=$0+site%3Ainstagram.com",
                "https://www.bing.com/search?q=$0+site%3Ainstagram.com"]


__search_list = [varname for varname in globals().keys() if varname.startswith("SEARCH_")]


__get_dict = {"default":SEARCH_GENERAL, 
            "*":[link for links in [globals()[varname] for varname in __search_list] for link in links],
            **{varname[7:].lower():globals()[varname] for varname in __search_list}}



def search(keywords:Union[str, Iterable], 
                search_in:Union[str, Iterable[Union[Iterable[str],str]]] = "default"):
    print(f"Got links for search ({keywords}) in {search_in}")
    if(isinstance(keywords, str)): keywords = [keywords]

    if(isinstance(search_in, str)):
        new_links = __get_dict.get(search_in, [search_in])
    elif(isinstance(search_in, Iterable)):
        new_links = []
        for sub in search_in:
            if(isinstance(sub, str)):
                new_links.extend(__get_dict.get(search_in, [search_in]))
            elif(isinstance(sub, Iterable)):
                new_links.extend(sub)
            else: raise ValueError("Search (sub) parameters were wrong. Check search args")
    else: raise ValueError("Search parameters were wrong. Check search args")

    if(not len(keywords)): return new_links

    for num, link in enumerate(new_links):
        for knum,word in enumerate(keywords):
            link = link.replace(f"${knum}",word)
        new_links[num] = link

    return new_links


def search_general(keywords:Union[str, Iterable], site:str=None):
    if(isinstance(keywords, str)): keywords = [keywords]
    if(not site is None): site=f"site:{site}"
    else: site = ''

    print(f"Got links for search ({keywords}) in general")

    return [link.replace(f"${knum}",word)+(site) for link in SEARCH_GENERAL 
                                            for knum,word in enumerate(keywords)]

def search_images(keywords:Union[str, Iterable]):
    if(isinstance(keywords, str)): keywords = [keywords]

    print(f"Got links for search ({keywords}) in images")

    return [link.replace(f"${knum}",word) for link in SEARCH_IMAGES 
                                            for knum,word in enumerate(keywords)]
                                            
def search_videos(keywords:Union[str, Iterable]):
    if(isinstance(keywords, str)): keywords = [keywords]

    print(f"Got links for search ({keywords}) in videos")

    return [link.replace(f"${knum}",word) for link in SEARCH_VIDEOS 
                                            for knum,word in enumerate(keywords)]

def search_news(keywords:Union[str, Iterable]):
    if(isinstance(keywords, str)): keywords = [keywords]

    print(f"Got links for search ({keywords}) in news")

    return [link.replace(f"${knum}",word) for link in SEARCH_NEWS 
                                            for knum,word in enumerate(keywords)]

def search_shopping(keywords:Union[str, Iterable]):
    if(isinstance(keywords, str)): keywords = [keywords]

    print(f"Got links for search ({keywords}) in shopping")

    return [link.replace(f"${knum}",word) for link in SEARCH_SHOPPING 
                                            for knum,word in enumerate(keywords)]

def search_maps(keywords:Union[str, Iterable]):
    if(isinstance(keywords, str)): keywords = [keywords]

    print(f"Got links for search ({keywords}) in maps")

    return [link.replace(f"${knum}",word) for link in SEARCH_MAPS 
                                            for knum,word in enumerate(keywords)]

def search_social(keywords:Union[str, Iterable]):
    if(isinstance(keywords, str)): keywords = [keywords]

    print(f"Got links for search ({keywords}) in social")

    return [link.replace(f"${knum}",word) for link in SEARCH_SOCIAL 
                                            for knum,word in enumerate(keywords)]

#def search_recipes(keywords:Union[str, Iterable]):
