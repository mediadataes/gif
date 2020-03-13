This repository is part of a project from <a href="https://mediadata.webs.upv.es/">MediaData</a>

<a href="https://github.com/mediadataes/gif">MediaData/gif</a> is meant to be used to download the top n trending gifs from various sites

## REQUIREMENTS

Python3 (only tested on Python3.7)

Note: it should run on any OS, but it may need to be run in only one process
Note2: Tested on Linux


## USAGE

$ python3 Gifs.py $number_process

Where: 
 $number_process is the number of instances of the browser that will run in parallel. This parameter will speed up the program significantly, but it will drawback as memory usage.


## RESULTS

As results the program will [over]write a file called results.json that can be found in the Scraper_new folder. This file should contain all gifs information formatted using JSON (identation 2 spaces).


## SETUP

Go to Scraper_new folder
Install all packages under requirements.txt
run setup.py

: code example :

cd Scraper_new
python3 -m pip install -r requirements.txt
python3 setup.py


## LIBRARIES

<a href="https://github.com/gitpython-developers/GitPython">GitPython</a>
<hr>
<a href="https://github.com/saisua/Scraper2">Scraper2</a>
<hr>
<a href="https://www.selenium.dev/">Selenium</a>
<hr>
<a href="https://github.com/john-kurkowski/tldextract">tldextract</a>
<hr>
<a href="https://github.com/insightindustry/validator-collection/">validatir-collection</a>
<hr>
<a href="https://bitbucket.org/techtonik/python-wget/src/default/">wget</a>
<hr>
