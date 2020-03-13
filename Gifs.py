# External imports
from multiprocessing import Process, Manager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from os import chdir
from time import sleep
from sys import argv
from operator import itemgetter
from random import choice, shuffle
import json

#chdir to ensure geckodriver is in path
chdir('./Scraper_new')

# Internal imports
from Scraper_new.Browser import Browser
from Scraper_new.Structures.Site import Site

def main(proc_num:int = int(argv[1]) if len(argv) > 1 else 2) -> None:
    """
        The main function runs the program. It's only parameter is
        the number of process the program should run with. [Default=2]

        This parameter can be easily accessed in the console. Usage:
        
        $ python3.7 Gifs.py {proc_num}
    """

    # Https proxy list got from http://www.freeproxylists.net/ using
    # Array.from(document.querySelectorAll("tr[class='Odd']")).concat(Array.from(document.querySelectorAll("tr[class='Even']"))).filter(e => e.innerText).map(e => e.querySelector("a[href]").innerText + ':' + e.querySelector("td[align='center']").innerText).join('", "')
    proxy_list = []

    # Wether this program should be ran through proxys
    proxy = False
    # Gifs_to_get is from every site
    # If you run the program and tell it to get
    # 10 gifs in gfycat *and* giphy, expected return will
    # be of lenngth 20
    gifs_to_get = 250

    proxys = {'socksProxy':[],'httpProxy':proxy_list[:],
                'ftpProxy':proxy_list[:],'sslProxy':proxy_list[:]}

    # Create the driver
    new_browser = Browser(sites=[
                                "https://gfycat.com/discover/trending-gifs"
                                ,"https://giphy.com/trending-gifs"
                                ], 
                        load_timeout=80, load_wait=0.5, proxy_dict=proxys if proxy else {}) # max_tabs in scrapping call

    del proxy_list, proxys, proxy

    try:
        if(proc_num == 1): 
            # if the number of process is 1, the program won't use multiprocessing.
            # This is mainly for windows
            result = []

            keep = {}

            scrapping(new_browser, result, num=gifs_to_get)
        else:
            # Run scrapping in {proc_num} process
            result = new_browser._manager.list()
            keep = new_browser._manager.dict()

            process = []
            for proc in range(proc_num):
                new_proc = Process(target=scrapping,args=(new_browser, result), kwargs={'num':gifs_to_get})
                new_proc.start()
                
                process.append(new_proc)
                sleep(.25)

            for proc in process: proc.join()
    except KeyboardInterrupt: pass

    print(f"\n\nFound {len(result)} gifs. If the number is not the one expected, an error occurred;\n"
            "Please contact the developer and maybe try again")

    # Rank a list copy of result
    result = rank_results(result[:])

    # Store it using JSON, with an indent of 2 spaces
    with open("result.json",'w') as file:
        json.dump(result, file, indent=2)

    #breakpoint()


def scrapping(browser:Browser, gif_result:list, *, num) -> None:
    """
        This method is meant to open in tabs all urls given to the browser
        in browser._links; Thread safe.

        browser is the firefox driver's class instance
        gif_result is the list where this class will store its output. It's done
            this way so that I can pass a Manager().list() and keep it multiproccessing
    """
    # Open and configure the drivers
    browser.open()

    # Counter for printing
    opened = 0

    # Wait until there are tabs avaliable.
    # Useful only when multiprocessing
    while(not len(browser._links)): sleep(.25)

    # While there are links not yet loaded
    while(len(browser._links)):
        # Get a new site (thread safe) (type = Structures\\Site.Site)
        site = browser._get_sites()
        print(f"Got {site}")

        while(not site is None):
            if(not site.link is None):
                # Open the link. This method, despite its name is the most secure one
                site = browser.old_open_link(link=site.link, new_tab=True)
                if(not site is None): # Else timed out. The Browser manages it by itself
                    opened += 1
                    print(f"Opened {opened} links. Remaining: {len(browser._links)}")

                    # Run the function based on the site domain.
                    gifs = FUNCT_FROM_DOMAIN.get(browser.driver.execute_script("return document.domain;"),__crawl)(browser, num=num)
                    # Store the result (Thread safe)
                    gif_result.extend(gifs)

                    # Close the already visited site
                    browser.close_tab()

            #[EXPERIMENTAL] browser.set_proxy(**browser.get_proxy(http=True, ssl=True, ftp=True, socks=True))
            
            # Get new site (Thread safe)
            site = browser._get_sites()
            print(f"Got {site}")

        continue
    
    browser.close()

def _giphy(browser:Browser, *, num:int=250) -> list:
    """
        This function gets run when the url loaded has 'giphy.com'
        as its domain. It will use a basic scrollIntoView strategy
        to load and keep record of all requested gifs
    """
    if("/gifs/" in browser.driver.current_url): return __giphy_gif(browser)
    if(not "trending-gifs" in browser.driver.current_url):
        return []

    print("### Giphy main site")

    result = set()

    #breakpoint()

    while(len(result) < num):
        # Scroll and get unique gifs
        result.update(set(browser.driver.execute_script("""
                var gif_set = new Set();
                for(var new_gif of Array.from(document.querySelectorAll("img[src*='webp']"))){
                        gif_set.add(new_gif.parentNode.href);
                        new_gif.scrollIntoView();
                }
                return Array.from(gif_set);
                """)))
        print(f"Got {len(result)} hrefs ({len(result)*100/num}%)", end='\r')

        # Sleep as implicit wait to allow the site to load
        sleep(2)

    #breakpoint()

    browser._links.extend([(Site(link),0) for link in list(result)[:num]])
    
    print(len(browser._links))
    
    return []

def __giphy_gif(browser:Browser) -> list:
    """
        The site has been found to be a gif from giphy and so
        start getting its information
    """
    print("## Giphy gif")

    result = {}
    
    WebDriverWait(browser.driver, browser.load_timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, "img[src][alt]")))

    result["link"] = browser.driver.current_url
    result["archivoConElGif"] = browser.driver.execute_script("""return document.querySelector("img[src][alt]").src;""")
    result["titulo"] = browser.driver.execute_script("""return document.querySelector("img[src][alt]").alt.split("GIF by")[0];""").strip()
    try:
        result["source"] = browser.driver.execute_script("""return document.querySelector("div[style] a[href*='channel/']").childNodes[1].nodeValue;""")
    except: pass

    try:
        result["visualizaciones"] = int(browser.driver.execute_script("""return document.querySelector("div[class*='ss-view']").innerText;""").replace(',','').replace("Views",'').strip())
    except: pass

    result["etiquetas"] = browser.driver.execute_script("""return Array.from(document.querySelectorAll("div[class] div[class] a[class][href] h3")).map(e => (e.innerText[0] == "#" && e.innerText.substring(1, e.innerText.length))).filter(e => e);""")
    result["fechaSubida"] = browser.driver.execute_script("""var button_ = document.querySelector("div[class*='ss-ellipsis']"); var parent = button_.parentNode; button_.click(); var meta; for(meta of Array.from(parent.parentNode.children)){ if(meta != parent){break;} } return document.evaluate("//*[contains(text(), 'Uploaded')]", meta, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.innerText.split(" ")[1];""")
    try:
        result["rating"] = browser.driver.execute_script("""return document.querySelector("div[style] div div h1").parentNode.parentNode.querySelectorAll("span")[3].innerText;""")
    except: pass

    
    browser.driver.execute_script("window.scroll(0,window.screen.height/2);")
    sleep(.5)
    
    result["gifsRelacionados"] = [{"link":gif, "etiquetas":[]} for gif in list(filter(lambda el : not el is None and len(el) > 0,browser.driver.execute_script("""return Array.from(document.querySelectorAll("img[src][alt]")).map(e => (e.parentNode.href));""")))[1:6]]

    for num, relac in enumerate(result["gifsRelacionados"]):
        tmp_site = browser.old_open_link(link=relac["link"], new_tab=True)

        if(tmp_site is None): continue

        browser.driver.switch_to.window(tmp_site.tab)
        result["gifsRelacionados"][num]["etiquetas"].append(browser.driver.execute_script("""return Array.from(document.querySelectorAll("div[class] div[class] a[class][href] h3")).map(e => (e.innerText[0] == "#" && e.innerText.substring(1, e.innerText.length))).filter(e => e);"""))
        browser.close_tab()

    return [result]

def _gfycat(browser:Browser, num=250) -> list:
    """
        This function gets run when the url loaded has 'gfycat.com'
        as its domain. It will use a basic scrollIntoView strategy
        to load and keep record of all requested gifs
    """
    if(not "trending-gifs" in browser.driver.current_url):
        return __gfycat_gif(browser)

    print("### Gfycat main site")

    result = set()

    while(len(result) < num):
        # Scroll and get unique gifs
        result.update(set(filter(lambda el : not el is None and len(el) > 0,
                browser.driver.execute_script("""
                var gif_set = new Set();
                for(var new_gif of Array.from(document.querySelectorAll("img[src*='.gif']"))){
                        gif_set.add(new_gif.parentNode.parentNode.parentNode.href);
                        new_gif.scrollIntoView();
                }
                return Array.from(gif_set);
                """))))
        print(f"Got {len(result)} hrefs ({len(result)*100/num}%)", end='\r')

        # Sleep as implicit wait to allow the site to load
        sleep(2)

    browser._links.extend([(Site(link),0) for link in list(result)[:num]])

    print(len(browser._links))

    return []

def __gfycat_gif(browser:Browser):
    """
        The site has been found to be a gif from gfycat and so
        start getting its information
    """
    print("## Gfycat gif")
    result = {}

    WebDriverWait(browser.driver, browser.load_timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, "video source[src]")))

    browser.driver.execute_script("""Array.from(document.querySelectorAll("div[class='upnext-horizontal'] a[href]"))[0].click();""")

    result["link"] = browser.driver.current_url
    result["archivoConElGif"] = browser.driver.execute_script("""return Array.from(document.querySelectorAll("video source[src]")).map(e => e.src.trim()).filter(e => e)[0];""")
    result["titulo"] = browser.driver.execute_script("""return (e => (e.substring(0,e.length-4)))(document.querySelector("div div h1").innerText);""")
    try:
        result["source"] = browser.driver.execute_script("""return document.querySelector("a div span[class='userid']").childNodes[1].nodeValue;""")
    except:pass

    vis = browser.driver.execute_script("""return (e => (e.substring(0,e.length-6)))(document.querySelector("div div[class='gif-views']").innerText);""").replace("views",'').strip()

    if(vis.endswith('K')):
        vis = int(float(vis[:-1])*1000)
    elif(vis.endswith('M')):
        vis = int(float(vis[:-1])*1000000)
    else:
        vis = int(vis)

    result["visualizaciones"] = vis
    result["etiquetas"] = browser.driver.execute_script("""return Array.from(document.querySelectorAll("div div a[href*='/gifs/search'][class]")).map(e => e.innerText);""")
    result["fechaSubida"] = browser.driver.execute_script("""return document.querySelector("div[class='gif-created']").childNodes[1].nodeValue;""")

    result["gifsRelacionados"] = [{"link":gif, "etiquetas":[]} for gif in browser.driver.execute_script("""return Array.from(document.querySelectorAll("div[class='upnext-horizontal'] a[href]")).slice(1,6).map(e => (e.href));""")]

    for num, relac in enumerate(result["gifsRelacionados"], start=1):
        browser.driver.execute_script(f"""Array.from(document.querySelectorAll("div[class='upnext-horizontal'] a[href]"))[{num}].click();""")

        sleep(1)

        result["gifsRelacionados"][num-1]["etiquetas"].append(browser.driver.execute_script("""return Array.from(document.querySelectorAll("div div a[href*='/gifs/search'][class]")).map(e => e.innerText);"""))

    browser.driver.switch_to.window(browser.driver.window_handles[1])

    return [result]


FUNCT_FROM_DOMAIN = {
    "giphy.com":_giphy,
    "gfycat.com":_gfycat
}


def __crawl(browser, ALLOWED_DOMAINS=FUNCT_FROM_DOMAIN.keys(), **kwargs):
    """
        This function should ideally not be called.
        It will be called if the link given is not in FUNCT_FROM_DOMAIN
    """
    browser._links.extend([(Site(link,depth=0),0) for link in browser.extract_hrefs() 
                                                    if browser._visited_sites_counter.get(link,None) is None and
                                                    browser.domain_from_link(link) in ALLOWED_DOMAINS])
    return []


# Aid function
def rank_results(result:list) -> list:
    """
        Rank the gifs based of the number of views.
        Gifs with no views information will be placed last
    """
    from collections import defaultdict

    # This function is slow, but will only be executed once

    ranking = defaultdict(list)
    for pos, gif in enumerate(result):
        ranking[Browser.domain_from_link(gif["link"])].append((gif.get("visualizaciones",0),pos))

    for gif_list in ranking.values():
        gif_list.sort(key=itemgetter(0), reverse=True)

        for rank, (_, gif_pos) in enumerate(gif_list, start=1):
            print(f"Ranked {rank} ({result[gif_pos]['titulo']})")
            result[gif_pos]["posicionEnElRanking"] = rank

    return result # Should not be necessary, however, just in case

if __name__ == "__main__":
    main()
