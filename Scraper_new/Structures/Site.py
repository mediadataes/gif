from dataclasses import dataclass, field
from xml.etree.ElementTree import Element
from typing import Iterable

from .Order import OrderedList

@dataclass
class Site():
    link:str
    domain:str=None
    parent:Element=None
    hrefs:set=field(default_factory=set)
    tab:int=None
    depth:int=0
    timeout:int=0
    xml_node:Element=None

def parse_sites_arg(sites, parent_node:Element=None, *, as_site_obj:bool=True, _manager=None):
    if(isinstance(sites, OrderedList)): return sites
    elif(isinstance(sites, dict)): return OrderedList(sites, _manager=_manager)

    if(not sites is None):
        if(isinstance(sites, Iterable) and not len(sites)):
            return OrderedList(_manager=_manager)
        if(not isinstance(sites, Iterable) or isinstance(sites, str)):
            sites = [sites]
    else:
        return OrderedList(_manager=_manager)

    if(isinstance(sites[0], Site)):
        if(as_site_obj):
            return OrderedList([(site,0) for site in sites], is_dict=True, _manager=_manager)
        else:
            return OrderedList([(site.link,0) for site in sites], is_dict=True, _manager=_manager)
    elif(isinstance(sites[0],str)):
        if(as_site_obj):
            return OrderedList([(Site(site,parent_node),0) for site in sites], is_dict=True, _manager=_manager)
        else:
            return OrderedList([(site,0) for site in sites], is_dict=True, _manager=_manager)

    else: raise ValueError(f"sites must be either str/Site/List[str/Site]. sites is {type(sites)}")

if __name__ == "__main__":
    parse_sites_arg(["https://duckduckgo.com/","https://stackoverflow.com"])