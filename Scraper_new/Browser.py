print("Starting Browser imports...  ")

from os import chdir, getcwd
from collections.abc import Iterable
from collections import defaultdict
from random import choice, shuffle
from math import ceil
from time import sleep
from datetime import datetime, timedelta
from typing import Tuple, Any, Union, Iterable, List, Optional, Dict
from re import search as re_search
from asyncio import run, create_task, get_event_loop, sleep as asleep

from multiprocessing import Process, Manager, Lock
from multiprocessing.managers import BaseProxy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchWindowException, InvalidArgumentException
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from validator_collection import validators, checkers
from tldextract import extract
from validator_collection.checkers import is_url as validate_url

# Test imports
from screeninfo import get_monitors

try:
    from Structures.Order import OrderedList
    from Structures.Site import Site, parse_sites_arg
    from Structures.Async_generator import AGenerator, async_sleep
    from Structures.Search import search
    from Analizers.Text_analizer import analize_text, find, words_related, _color_sent
    from Settings.jQuery import load, download, jq_file
except ModuleNotFoundError:
    from .Structures.Order import OrderedList
    from .Structures.Site import Site, parse_sites_arg
    from .Structures.Async_generator import AGenerator, async_sleep
    from .Structures.Search import search
    from .Analizers.Text_analizer import analize_text, find, words_related, _color_sent
    from .Settings.jQuery import load, download, jq_file
    
print("Done (Browser)")

""" 

SRC https://stackoverflow.com/questions/20884089/dynamically-changing-proxy-in-firefox-with-selenium-webdriver

var prefs = Components.classes["@mozilla.org/preferences-service;1"]
.getService(Components.interfaces.nsIPrefBranch);

prefs.setIntPref("network.proxy.type", 1);
prefs.setCharPref("network.proxy.http", "${proxyUsed.host}");
prefs.setIntPref("network.proxy.http_port", "${proxyUsed.port}");
prefs.setCharPref("network.proxy.ssl", "${proxyUsed.host}");
prefs.setIntPref("network.proxy.ssl_port", "${proxyUsed.port}");
prefs.setCharPref("network.proxy.ftp", "${proxyUsed.host}");
prefs.setIntPref("network.proxy.ftp_port", "${proxyUsed.port}");
"""

def main(proc_num=8):
    proc_num = int(proc_num)

    a = Browser(sites=open("test.txt",'r',encoding="utf-8").readlines(), headless=False)

    sh = AGenerator()

    size = get_monitors()[0]

    half = proc_num//2 or 1

    posy = size.height//2 
    sizex, sizey = size.width//half, posy if proc_num > 1 else size.height

    if(True):
        ### Search params
        to_search = input("Search: ") or "was"
        tag = {'1':'n','2':'v','3':'a','4':'r'}.get(input(f"\nWhat '{to_search}'?\n"
                                                "[1]: Noun\n"
                                                "[2]: Verb\n"
                                                "[3]: Adjective\n"
                                                "[4]: Adverb\n\n"
                                                "> ") or '2',None)
        syn = not 'n' in input("\nFind related words too? ").lower()
        exact = not 'n' in input("\nFind exact word? ").lower()
        print()

    process = []
    multi = False
    if(multi):
        for n in range(proc_num):
            p = Process(target=test_search,args=(a,((sizex,sizey),((n%half)*sizex,(n<half)*posy)),sh))
            process.append(p)
            p.start()

        if(syn): rel_words = words_related(to_search, tag)
        else: rel_words = [to_search]

        for p in process: p.join()

        print("\n\nAll process joined\n")
    else:
        print("Running non-multithreaded mode")
        n=0

        #test_jq(a, ((sizex,sizey),((n%half)*sizex,(n<half)*posy))); exit(0)

        if(syn): rel_words = words_related(to_search, tag)
        else: rel_words = to_search

        test_crawl(a)#, ((sizex,sizey),((n%half)*sizex,(n<half)*posy)), sh, exact)

    result = []
    found = next(sh)

    while(len(found)):
        for s_dict,sentences in found:
            result.extend([sentences[n] for n in find(rel_words,s_dict)])
        
        found = next(sh)

    print(f"\n\nFound {len(result)} phrases containing words related to {to_search}\n")

    num = 0
    keep = False
    print()

    per_print = 6
    while(not keep and num < len(result)):
        for a in range(per_print if len(result)-num > (per_print-1) else len(result)-num):
            print(result[num],end="\n\n")
            print("-----")

            num += 1
            
        keep = input("### Stop?")
        print()
    
def size_pos_(proc_num:int, n:int):
    size = get_monitors()[0]

    half = proc_num//2 or 1

    posy = size.height//2 
    sizex, sizey = size.width//half, posy if proc_num > 1 else size.height

    return ((sizex,sizey),((n%half)*sizex,(n<half)*posy))

def test(browser, size_pos=None):
    with browser as br:
        if(not size_pos is None): br.set_size_pos(*size_pos)
        link = br._get_loaded_sites()
        print(f"Got {link}")
        br.open_tab(link=link)
        br._get_loaded_sites()
        print(br.extract_text())
        br.close()

def test_search(browser, size_pos, shared_result, exact):
    with browser as br:
        if(not size_pos is None): br.set_size_pos(*size_pos)
        
        link = br._get_sites()
        print(f"Got {link}")
        counter = 0
        while(not link is None):
            counter += 1
            br.open_tab(link=link)
            link = br._get_sites()
            print(f"Got {link}")

        print("\nStarting text scrapping...\n")
        site = list(br._get_loaded_sites(wait=True))
        while(counter > 0):
            if(not len(site)):
                site = list(br._get_loaded_sites(wait=False))
                continue

            counter -= 1
            tab = site[0].tab
            br.driver.switch_to.window(tab)
            #print(len(br.extract_text()))
            shared_result.append(analize_text(br.extract_text(), exact_words=exact)[1:])
            br.close_tab(tab)
            if(len(site)>1):
                site.pop(0)
                continue
            site = list(br._get_loaded_sites(wait=False))

def test_crawl(browser, size_pos=None):
    with browser as br:
        if(not size_pos is None): br.set_size_pos(*size_pos)
        
        link = br._get_sites()
        print(f"Got {link}")
        counter = 0
        while(not link is None):
            counter += 1
            br.open_tab(link=link.link)
            link = br._get_sites()
            print(f"Got {link}")

        print("\nStarting text crawling...\n")
        site = list(br._get_loaded_sites(wait=True))
        while(counter > 0):
            if(not len(site)):
                site = list(br._get_loaded_sites(wait=False))
                continue

            counter -= 1
            tab = site[0].tab
            br.driver.switch_to.window(tab)
            print(br.extract_hrefs(),end="\n\n")
            br.close_tab(tab)
            if(len(site)>1):
                site.pop(0)
                continue
            site = list(br._get_loaded_sites(wait=False))        

def test_jq(browser, size_pos=None):
    try:
       from Settings.jQuery import download
    except: return

    jq_raw = AGenerator([download(return_after=True)])
    with browser as br:
        if(not size_pos is None): br.set_size_pos(*size_pos)

        br.open_tab(link="https://www.instagram.com/instagram/")
        script = ("window.el = document.createElement('script');\nn = function(e){"
                    "e.type='text/javascript';"
                    f"e.innerHTML={next(jq_raw)};e.onload=function()"
                    "{jQuery.noConflict();console.log('jQuery injected')};"
                    "document.head.appendChild(e);console.log(e);}(el);")
        print()
        print(script)
        print()
        print(br.driver.execute_script(script))
        i = input("\n\n> ")
        while(i):
            try:
                print(br.driver.execute_script(i))
            except: pass

            i = input("\n> ")

class Browser():
    """
    A browser site manager, with some data collection capabilities

    In case of using more than one browser it's highly recommended to open them all
    before opening them
    """
    def __init__(self, sites:Iterable[Union[str, Site]]=[], load_timeout:float=20,
                max_tabs:int=25, headless:bool=False, load_images:bool=True, autoload_videos:bool=False,
                load_wait:float=3, disable_downloads:bool=False, 
                proxy_dict:Dict[str,List[str]]={'socksProxy':[],'httpProxy':[],'ftpProxy':[],'sslProxy':[]}, 
                *, jq_filename:str=jq_file):
        
        ### Start loading
        jq = AGenerator()
        jq.append(load(jq_filename))

        ## Shared memory

        # Create a manager to create shared objects
        self._manager = Manager()

        # Check sites to be an OrderedList of {Site:depth}
        # Workaround. Improvement needed
        self._links = parse_sites_arg(sites, _manager=self._manager)

        # List to store timed out links
        self._timed_out_links = self._manager.list()

        # Some semaphores to aid in some functionalities
        self.__lock_loaded = self._manager.RLock()

        self.__lock_sited = self._manager.RLock()

        self.__lock_timed = self._manager.RLock()

        self.__lock_proxy = self._manager.RLock()

        # Store all visited sites and how many times it was visited
        self._visited_sites_counter = self._manager.dict()
        self._visited_domains_counter = self._manager.dict()

        # All proxys to be accessed
        self.proxys = self._manager.dict()
        for key, proxy_list in proxy_dict.items(): 
            shuffle(proxy_list)
            self.proxys[key] = Browser.check_proxys(proxy_list)

        ### PERFORMANCE settings

        # How many tabs per process will be able to open the browser
        # This setting affects severely the ram usage and speed of the crawling
        self.max_tabs = max_tabs

        # Should it load the images in the sites it visits?
        # This setting is meant to be used in low-speed connections
        self.load_images = load_images

        # If videos will be automatically loaded without the user's interaction.
        # May be necessary when video scrapping 
        self.autoload_videos = autoload_videos

        # How much time wait before releasing a timeout exception on a site.
        # This setting can have false positives on low-conn networks, but
        # it is meant to close blank urls
        self.load_timeout = load_timeout

        self.load_wait = load_wait

        # Store the jQuery script as plain text. There should've take shorter,
        # since it has been loading async
        self.__jQuery_script = next(jq)

                
        ###  OTHER configurations

        # If the browser will be shown
        self.headless = headless

        # Wether to block download/open file requests
        self.disable_downloads = disable_downloads
        
    def __enter__(self):
        self.open()

        return self

    def __exit__(self,_,__,___):
        self.close()

    def open(self, *, options=None, profile=None, capabilities=None, overwrite_config:bool=True,
                        proxys:Dict[str,List[str]]=None):
        from selenium import webdriver
        from os import getcwd
        try:
            from Settings.browser_configuration import get_configuration
            from Structures.Async_generator import AGenerator
        except ModuleNotFoundError:
            from .Settings.browser_configuration import get_configuration
            from .Structures.Async_generator import AGenerator

        print(f"Starting the opening of a Browser{' (headless)' if self.headless else ''}")

        #breakpoint()

        if(not proxys is None): self.proxys = proxys

        if(options is None or profile is None or capabilities is None or not overwrite_config):
            options2, profile2, capabilities2 = get_configuration(tabs_per_window=1000,
                                            headless=self.headless,
                                            load_images=self.load_images,
                                            autoload_videos=self.autoload_videos,
                                            disable_downloads=self.disable_downloads,
                                            proxys=self.get_proxy(http=True, ssl=True, ftp=True, socks=True),
                                            options=options if not overwrite_config else None, 
                                            profile=profile if not overwrite_config else None, 
                                            capabilities=capabilities if not overwrite_config else None)

            if(not overwrite_config or options is None):
                options = options2
            if(not overwrite_config or profile is None):
                profile = profile2
            if(not overwrite_config or capabilities is None):
                capabilities = capabilities2

            del options2, profile2, capabilities2

        print("Configuration complete. Trying to run the drivers. This could take some time...")
        try:
            self.driver = webdriver.Firefox(executable_path=f"{getcwd()}//geckodriver",
                    options=options, firefox_profile=profile, capabilities=capabilities) 

            #self._profile = profile
                    
            print("Drivers ran succesfully!")

        except Exception as ex:
            print(f"Looks like something failed. Error message: {ex}")
            self.driver = webdriver.Firefox()

        self.driver.get("about:config")
        self.driver.execute_script("document.querySelector('button').click();")

        #breakpoint()

        ### After driver configs
        #self.driver.set_page_load_timeout(0)
        self.driver.set_page_load_timeout(self.load_timeout)

        ### Non-shared memory
        self._site_from_tab = {}

        ## Async site_sleep
        self._async_site_sleep = AGenerator()
        

        print("New Browser opened")

    def close(self):
        self.driver.quit()

    def _get_sites(self, *, _number:int=1):
        # Ask for access
        self.__lock_sited.acquire()

        # There's work to be done. It's not the same a depth 0 site
        # as a depth N. Should be able to get more than one in one request
        if(not len(self._links)): 
            self.__lock_sited.release()
            return None

        result = self._links[0]
        self._links.pop(0)

        self.__lock_sited.release()

        return result

    def _get_loaded_sites(self, *, wait:bool=True) ->  Iterable:
        sites = []
        while(not len(sites)):
            sites = list(filter(None, next(self._async_site_sleep)))

            for site in sites:
                self._site_from_tab[site.tab] = site

            if(len(self._site_from_tab) or not wait):
                return self._site_from_tab.values()

    def open_tab(self, *, link:str=None, site:Site=None) -> int:
        self.__lock_timed.acquire()

        self.driver.switch_to.window(self.driver.window_handles[0])

        self.driver.execute_script("window.open();")
        
        #Switch to new tab instead of next
        self.driver.switch_to.window(self.driver.window_handles[self.driver.window_handles.index(
            self.driver.current_window_handle)+1])

        tab = self.driver.current_window_handle

        self.__lock_timed.release()

        if(not link is None):
            self.open_link(link, new_tab=False, site=site)

        return tab

    def open_link(self, link:str, *, new_tab:bool=False, site:Site=None, wait_load:bool=True):
        tab = self.driver.current_window_handle
        bef_tab = self.driver.window_handles.index(tab)

        if(new_tab):
            tab = self.open_tab(link=None)
        
        self.__lock_timed.acquire()

        try:
            self.driver.switch_to.window(tab)
            self.driver.get(link)
        except TimeoutException:
            pass

        self.__lock_timed.release()

        # window.array = [performance.getEntries()]; window.interval = setInterval(function foo(){var a = performance.getEntries(); if(window.array[window.array.length-1].length != a.length){window.array.push(a);}},200)

        domain = Browser.domain_from_link(link)

        self._visited_sites_counter[link] = self._visited_sites_counter.get(link,0) + 1
        self._visited_domains_counter[domain] = self._visited_domains_counter.get(domain,0) + 1

        if(site is None):
            site = Site(link, tab=tab)
        else:
            site.tab = tab
            site.link = link

        self._site_from_tab[tab] = site

        if(wait_load):
            self._async_site_sleep.append(self.async_sleep(tab, self.load_wait,
                                        _return=site))

        return site

    async def async_sleep(self, tab, load_wait:float, *, _return=None, period:float=0.1):
        load_start = datetime.now()
        timeout = load_start + timedelta(seconds=int(load_wait))

        while(not ready_state(self.driver, tab, self.__lock_timed) and (datetime.now() < timeout)):
            self.__lock_timed.release()

            await asleep(period)

        self.__lock_timed.release()

        if(timeout > datetime.now()):
            return

        await asleep(load_wait)

        return _return

    # open_link seems to be faster than async_open_link
    def async_open_link(self, link:str, *, new_tab:bool=False, site:Site=None):
        #raise DeprecationWarning()
        if(not link is None):
            self._async_site_sleep.append(self.__a_open_link(link, new_tab=new_tab, site=site))

    async def __a_open_link(self, link:str, *, new_tab:bool=False, site:Site=None):
        bef_tab = self.driver.window_handles.index(self.driver.current_window_handle)

        if(new_tab):
            tab = self.open_tab(link=None)
        else:
            tab = self.driver.current_window_handle

        try:
            self.driver.get(link)
        except TimeoutException:
            print(f"The site timed out. Skipping {link}")
            self._timed_out_links.append(link)
            self.driver.execute_script("window.close();")
            self.switch_to_window(self.driver.window_handles[bef_tab%len(self.driver.window_handles)])
            return 

        domain = Browser.domain_from_link(link)

        self._visited_sites_counter[link] = self._visited_sites_counter.get(link,0) + 1
        self._visited_domains_counter[domain] = self._visited_domains_counter.get(domain,0) + 1

        if(site is None):
            site = Site(link, tab=tab)
        else:
            site.tab = tab
            site.link = link

        self._site_from_tab[tab] = site

        await asleep(self.load_wait)

        return site

    def old_open_link(self, link:str, *, new_tab:bool=False, site:Site=None):
        if(new_tab):
            tab = self.open_tab(link=None)
        else:
            tab = self.driver.current_window_handle

        try:
            self.driver.get(link)
        except TimeoutException:
            print(f"The site timed out. Skipping {link}")
            self._timed_out_links.append(link)
            self.driver.execute_script("window.close();")
            self.switch_to_window(self.driver.window_handles[0])
            return 

        domain = Browser.domain_from_link(link)

        self._visited_sites_counter[link] = self._visited_sites_counter.get(link,0) + 1
        self._visited_domains_counter[domain] = self._visited_domains_counter.get(domain,0) + 1

        if(site is None):
            site = Site(link, tab=tab)
        else:
            site.tab = tab
            site.link = link

        self._site_from_tab[tab] = site

        sleep(self.load_wait)

        return site

    def switch_to_window(self, tab):
        if(tab in self.driver.window_handles):
            self.driver.switch_to_window(tab)
            return
        self.driver.switch_to_window(self.driver.window_handles[0])

    def restore_timed_out(self):
        self.__lock_timed.acquire()

        for zombie_tab in [tab for tab in self.driver.window_handles[1:] if not tab in self._site_from_tab.keys()]:
            print("Found a non-properly closed tab. Closing it...")
            self.close_tab(zombie_tab)


        self._links.extend(self._timed_out_links)
        
        while(len(self._timed_out_links)): self._timed_out_links.pop(0)

        self.__lock_timed.release()

    def extract_text(self, element:str="document") -> str:
        return self.driver.execute_script(
                        f"var query={element}.evaluate('//*[not(self::script)][not(self::style)]/text()',{element},null,XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,null);"
                        "return Array(query.snapshotLength).fill(0).map((element,index) => query.snapshotItem(index)"
                        ").map(x => function(e){if(e.data.replace('\\n','').trim()){return e.data;} return '';}(x)).join('\\n');")

    def extract_hrefs(self, element:str="document", *, site:Site=None):
        if(site is None):
            return list(filter(validate_url,
                        self.driver.execute_script(
                        f"var query={element}.evaluate('//body[1]//@href[not(self::script)][not(self::link)][not(self::style)]',{element},null,XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,null);"
                        "return Array.from(new Set(Array(query.snapshotLength).fill(0).map((element,index) => query.snapshotItem(index).value)"
                        ".map(x => function(e){if(e[0] == '/'){return location.origin+e;} return e}(x))))"
                        )))

        site.hrefs = list(filter(validate_url,
                        self.driver.execute_script(
                        f"var query={element}.evaluate('//@href',{element},null,XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,null);"
                        "return Array.from(new Set(Array(query.snapshotLength).fill(0).map((element,index) => query.snapshotItem(index).value)"
                        ".map(x => function(e){if(e[0] == '/'){return location.origin+e;} return e}(x))))"
                        )))
        return site.hrefs

    def extract_buttons(self):
        return self.driver.execute_script("""
                var _ = document.evaluate("//*", document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                return (jQuery(Array.from(new Set(Array(_.snapshotLength).fill(0).map((element, index) => _.snapshotItem(index).nodeName))).filter(function(value,_,_){return value!="IFRAME"}).join(", ")).contents().filter(function b(e){return jQuery._data(e, 'events') != undefined;})).toArray()
                """)
        """
        var c = (jQuery(window.some||Array.from(new Set(Array(_.snapshotLength).fill(0).map((element, index) => _.snapshotItem(index).nodeName))).filter(function(value,_,_){return value!="IFRAME"}).join(", ")).contents().toArray().filter(function b(e){return e.click != undefined;}));
        window.some = Array.from(new Set(c.map(function d(e){return e.nodeName;}))).filter(function f(e){return e != "IFRAME"}).join(', ')
        """

    def extract_video(self):
        return self.driver.execute_script("return performance.getEntries().map(e => (e.initiatorType == 'xmlhttprequest' && e.name.split('?')[0])).filter(e => (e && (e.endsWith('.mp4') || e.endsWith('.m3u8'))));")

    def store_cookies(self, filename:str="cookies.dat"):
        import pickle

        pickle.dump(self.driver.get_cookies(), open(filename, 'ab'))

    def load_cookies(self, filename:str="cookies.dat"):
        import pickle

        link_bef = self.driver.current_url

        for cookie in pickle.load(open(filename,'rb')):
            self.inject_cookie(cookie)
            print(f"Loaded cookie: {cookie}")

        self.driver.get(link_bef)

    def inject_cookie(self, cookie:dict):
        domain = cookie.get("domain",None)
        if(not domain is None):
            if(domain[0] == '.'): domain = "www"+domain
            if("about" in self.driver.current_url or 
                        Browser.domain_from_link(self.driver.current_url) != domain):
                self.driver.get(f"http://{domain}")
        else:
            if("about" in self.driver.current_url):
                self.driver.get("https://duckduckgo.com")

        if(isinstance(cookie, str)):
            raise NotImplementedError
            #cookie = cookie.split(":")
            #self.driver.add_cookie(dict(zip([][:len(cookie)],cookie)))
        self.driver.add_cookie(cookie)

    def inject_jQuery(self):
        self.driver.execute_script("window.el = document.createElement('script'); n = function(e){"
                    "e.type='text/javascript';"
                    f"e.innerHTML={self.__jQuery_script};e.onload=function()"
                    "{console.log('Checking jQuery');jQuery.noConflict();console.log('jQuery injected')};"
                    "console.log('Injecting');document.head.appendChild(e);console.log(e);}(el);")

    def get_proxy(self, *, http:bool=False, ssl:bool=False, ftp:bool=False, socks:bool=False) -> dict:
        result = {}
        self.__lock_proxy.acquire()

        if(http and len(self.proxys.get('httpProxy', []))):
            aux = self.proxys['httpProxy'][0]
            result['httpProxy'] = aux
            self.proxys['httpProxy'].pop(0)
            self.proxys['httpProxy'].append(aux)
        if(ssl and len(self.proxys.get('sslProxy', []))):
            aux = self.proxys['sslProxy'][0]
            result['sslProxy'] = aux
            self.proxys['sslProxy'].pop(0)
            self.proxys['sslProxy'].append(aux)
        if(ftp and len(self.proxys.get('ftpProxy', []))):
            aux = self.proxys['ftpProxy'][0]
            result['ftpProxy'] = aux
            self.proxys['ftpProxy'].pop(0)
            self.proxys['ftpProxy'].append(aux)
        if(socks and len(self.proxys.get('socksProxy', []))):
            aux = self.proxys['socksProxy'][0]
            result['socksProxy'] = aux
            self.proxys['socksProxy'].pop(0)
            self.proxys['socksProxy'].append(aux)

        self.__lock_proxy.release()

        return result

    def set_proxy(self, httpProxy:str=None, sslProxy:str=None, ftpProxy:str=None, 
                        socksProxy:str=None) -> None:
        self.driver.execute("SET_CONTEXT", {"context": "chrome"})

        if(not httpProxy is None):
            try:
                self.driver.execute_script("""
                        Services.prefs.setCharPref("network.proxy.http", arguments[0]);
                        Services.prefs.setIntPref("network.proxy.http_port", Number(arguments[1]));
                        """, *httpProxy.split(':'))
            except: pass
        if(not sslProxy is None):
            try:
                self.driver.execute_script("""
                Services.prefs.setCharPref("network.proxy.ssl", arguments[0]);
                Services.prefs.setIntPref("network.proxy.ssl_port", Number(arguments[1]));
                """, *sslProxy.split(':'))
            except: pass
        if(not ftpProxy is None):
            try:
                self.driver.execute_script("""
                Services.prefs.setCharPref('network.proxy.ftp', arguments[0]);
                Services.prefs.setIntPref('network.proxy.ftp_port', Number(arguments[1]));
                """, *ftpProxy.split(':'))
            except: pass
        if(not socksProxy is None):
            try:
                self.driver.execute_script("""
                Services.prefs.setCharPref('network.proxy.socks', arguments[0]);
                Services.prefs.setIntPref('network.proxy.socks_port', Number(arguments[1]));
                """, *socksProxy.split(':'))
            except: pass

        self.driver.execute("SET_CONTEXT", {"context": "content"})

    def close_tab(self, tab:int=None):
        if(not tab is None):
            if(not tab in self.driver.window_handles):
                #breakpoint()
                self._site_from_tab.pop(tab)
                for zombie_tab in [tab for tab in self.driver.window_handles[1:] if not tab in self._site_from_tab.keys()]:
                    print("Found a non-properly closed tab. Closing it...")
                    self.close_tab(zombie_tab)
                return

            self.__lock_timed.acquire()
            self.driver.switch_to.window(tab)
        else:
            self.__lock_timed.acquire()
        

        actual_tab = self.driver.current_window_handle
        self.driver.execute_script("window.close();")
        self.__lock_timed.release()

        # Suddenly this stopped working. Whatev
        try:
            self._site_from_tab.pop(actual_tab)
        except KeyError: pass

    # Aesthetics function    
    def set_size_pos(self, size:Tuple[int,int], position:Tuple[int,int]=(0,0)) -> None:
        self.driver.set_window_rect(*position,*size)

    @staticmethod
    def domain_from_link(link:str) -> Optional[str]:
        return re_search(r"(?<=:\/\/)?(([A-Z]|[a-z]|[0-9])+\.)+([A-Z]|[a-z]|[0-9])+", link).group()

    @staticmethod
    def check_proxys(proxys:list) -> list:
        return proxys

# Auxiliar function
def ready_state(driver, tab, semaphore):
    semaphore.acquire()
    sleep(.2)
    try:
        driver.switch_to.window(tab)
    except: return False    
    return driver.execute_script("return document.readyState == 'complete';")

if __name__ == "__main__":
    main(1)
