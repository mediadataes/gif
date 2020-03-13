from random import choice

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.proxy import Proxy, ProxyType

from selenium import webdriver


def get_configuration(*,tabs_per_window:int, headless:bool=False,
                        load_images:bool=True, disable_downloads:bool=False,
                        disable_javascript:bool=False, autoload_videos:bool=False,
                        proxys={},
                        options=None, profile=None, capabilities=None):
    if(capabilities is None):
        # https://github.com/SeleniumHQ/selenium/wiki/DesiredCapabilities
        capabilities = DesiredCapabilities.FIREFOX.copy()

    if(options is None):
        options = webdriver.firefox.options.Options()
    options.set_preference("browser.popups.showPopupBlocker",False)

    if(headless):
        #DeprecationWarning: use setter for headless property instead of options.set_headless()
        options.headless = True

    if(profile is None):
        profile = webdriver.FirefoxProfile()
    try:
        del profile.DEFAULT_PREFERENCES['frozen']["browser.link.open_newwindow"]
        del profile.DEFAULT_PREFERENCES['frozen']["security.fileuri.origin_policy"]
        del profile.DEFAULT_PREFERENCES['frozen']["browser.safebrowsing.enabled"]
        del profile.DEFAULT_PREFERENCES['frozen']["browser.safebrowsing.malware.enabled"]
        
        #print(profile.DEFAULT_PREFERENCES)
        #del profile.DEFAULT_PREFERENCES['frozen']["browser.aboutConfig.showWarning"]
    except KeyError as err: print(f"Error on default preferences {err}")
    #http://kb.mozillazine.org/About:config_entries  #profile
    #http://kb.mozillazine.org/Categorhttps://stackoverflow.com/qhttps://stackoverflow.com/questions/20884089/dynamically-changing-proxy-in-firefox-with-selenium-webdriveruestions/20884089/dynamically-changing-proxy-in-firefox-with-selenium-webdrivery:Preferences
    profile.set_preference("browser.link.open_newwindow", 3)
    profile.set_preference("dom.popup_maximum", tabs_per_window)
    profile.set_preference("browser.dom.window.dump.enabled", False)
    profile.set_preference("browser.tabs.loadDivertedInBackground", True)
    profile.set_preference("browser.showPersonalToolbar", False)
    profile.set_preference("privacy.trackingprotection.enabled", True)
    profile.set_preference("content.notify.interval", 500000)
    profile.set_preference("content.notify.ontimer", True)
    profile.set_preference("content.switch.threshold", 250000)
    profile.set_preference("browser.cache.memory.capacity", 65536)
    profile.set_preference("browser.startup.homepage", "about:blank")
    profile.set_preference("reader.parse-on-load.enabled", False)
    profile.set_preference("browser.pocket.enabled", False) 
    profile.set_preference("loop.enabled", False)
    profile.set_preference("browser.chrome.toolbar_style", 1)
    profile.set_preference("browser.display.show_image_placeholders", False)
    profile.set_preference("browser.display.use_document_colors", False)
    profile.set_preference("browser.display.use_document_fonts", 0)
    profile.set_preference("browser.display.use_system_colors", False)
    profile.set_preference("browser.formfill.enable", False)
    profile.set_preference("browser.helperApps.deleteTempFileOnExit", True)
    profile.set_preference("browser.shell.checkDefaultBrowser", False)
    profile.set_preference("browser.startup.homepage", "about:blank")
    profile.set_preference("browser.startup.page", 0)
    profile.set_preference("browser.tabs.forceHide", True)
    profile.set_preference("browser.urlbar.autoFill", False)
    profile.set_preference("browser.urlbar.autocomplete.enabled", False)
    profile.set_preference("browser.urlbar.showPopup", False)
    profile.set_preference("browser.urlbar.showSearch", False)
    profile.set_preference("extensions.checkCompatibility", False) 
    profile.set_preference("extensions.checkUpdateSecurity", False)
    profile.set_preference("extensions.update.autoUpdateEnabled", False)
    profile.set_preference("extensions.update.enabled", False)
    profile.set_preference("general.startup.browser", False)
    profile.set_preference("plugin.default_plugin_disabled", False)
    profile.set_preference("browser.privatebrowsing.autostart", True)
    profile.set_preference("navigator.doNotTrack", 1)
    profile.set_preference("general.useragent.override", '')
    profile.set_preference('general.platform.override','')
    profile.set_preference('general.appname.override','')
    profile.set_preference('general.appversion.override','')
    profile.set_preference("general.buildID.override", '')
    profile.set_preference("general.oscpu.override", '')
    # Not working. I think it's not possible either
    profile.set_preference('general.useragent.vendor', '')
    # It depends in wether useragent was modified or not
    profile.set_preference('general.webdriver.override',False)
    profile.set_preference("browser.search.region",choice([
                "AF","AL","DZ","AS","AD","AO","AQ","AG","AR","AM",
                "AW","AU","AT","AZ","BS","BH","BD","BB","BY","BE",
                "BZ","BJ","BM","BT","BO","BA","BW","BV","BR","IO",
                "BN","BG","BF","BI","KH","CM","CA","CV","KY","CF",
                "CF","TD","CL","CN","CX","CC","CO","KM","CG","CD",
                "CK","CR","CI","HR","CU","CY","CZ","DK","DJ","DM",
                "DO","EC","EG","SV","GQ","ER","EE","ET","FK","FO",
                "FJ","FI","FR","GF","PF","TF","GA","GM","GE","DE",
                "GH","GI","GR","GL","GD","GP","GU","GT","GN","GW",
                "GY","HT","HM","HK","HU","IS","IN","ID","IR","IQ",
                "IE","IL","IT","JM","JP","JO","KZ","KE","KI","KP",
                "KR","KW","KG","LA","LB","LS","LR","LY","LI","LT",
                "LU","MO","MK","MG","MW","MY","MV","ML","MT","MH",
                "MQ","MT","MU","YT","MX","FM","MD","MC","ME","MS",
                "MA","MZ","MM","NA","NR","NP","NL","AN","NC","NZ",
                "NI","NE","NG","NU","NF","MP","NO","OM","PK","PW",
                "PS","PA","PG","PY","PE","PH","PN","PL","PT","PR",
                "QA","RE","RO","RU","RW","SH","KN","LC","PM","VC",
                "WS","SM","ST","SA","SN","RS","SC","SL","SG","SK",
                "SI","SB","SO","ZA","GS","ES","LK","SD","SR","SJ",
                "SZ","SE","CH","SY","TW","TJ","TZ","TH","TZ","TH",
                "TL","TG","TK","TO","TT","TN","TR","TM","TC","TV",
                "UG","UA","AE","GB","US","UM","UY","UZ","VU","VE",
                "VN","VG","VI","WF","EH","YE","ZM","ZW"]))
    #profile.set_preference("browser.search.region",'')
    profile.set_preference("browser.search.defaultenginename",'')
    profile.set_preference("browser.search.order.1",'')
    profile.set_preference("security.fileuri.strict_origin_policy",False)
    profile.set_preference("security.fileuri.origin_policy",0)
    profile.set_preference("security.sandbox.content.level", 0)
    profile.set_preference("privacy.resistFingerprinting", True)
    profile.set_preference("privacy.trackingprotection.fingerprinting.enabled", True)
    profile.set_preference("privacy.trackingprotection.cryptomining.enabled", True)
    profile.set_preference("intl.accept_languages", "en")
    profile.set_preference("services.sync.prefs.sync.intl.accept_languages", False)
    profile.set_preference("browser.newtabpage.activity-stream.feeds.section.topstories.options",
                                """{"api_key_pref":"extensions.pocket.oAuthConsumerKey","hidden":true,"provider_icon":"pocket",
                                "provider_name":"Pocket","read_more_endpoint":"https://getpocket.com/explore/trending?src=fx_new_tab",
                                "stories_endpoint":"https://getpocket.cdn.mozilla.net/v3/firefox/global-recs?version=3&consumer_key=
                                $apiKey&locale_lang=en&feed_variant=default_spocs_off","stories_referrer":
                                "https://getpocket.com/recommendations","topics_endpoint":
                                "https://getpocket.cdn.mozilla.net/v3/firefox/trending-topics?version=2&consumer_key=$apiKey&locale_lang=en"
                                ,"model_keys":["nmf_model_animals","nmf_model_business","nmf_model_career","nmf_model_datascience",
                                "nmf_model_design","nmf_model_education","nmf_model_entertainment","nmf_model_environment",
                                "nmf_model_fashion","nmf_model_finance","nmf_model_food","nmf_model_health","nmf_model_home",
                                "nmf_model_life","nmf_model_marketing","nmf_model_politics","nmf_model_programming","nmf_model_science",
                                "nmf_model_shopping","nmf_model_sports","nmf_model_tech","nmf_model_travel","nb_model_animals",
                                "nb_model_books","nb_model_business","nb_model_career","nb_model_datascience","nb_model_design",
                                "nb_model_economics","nb_model_education","nb_model_entertainment","nb_model_environment","nb_model_fashion",
                                "nb_model_finance","nb_model_food","nb_model_game","nb_model_health","nb_model_history","nb_model_home",
                                "nb_model_life","nb_model_marketing","nb_model_military","nb_model_philosophy","nb_model_photography",
                                "nb_model_politics","nb_model_productivity","nb_model_programming","nb_model_psychology","nb_model_science",
                                "nb_model_shopping","nb_model_society","nb_model_space","nb_model_sports","nb_model_tech","nb_model_travel",
                                "nb_model_writing"],"show_spocs":false,"personalized":false,"version":1}""")
    profile.set_preference("browser.search.context.loadInBackground", True)
    profile.set_preference("geo.enabled", False)
    profile.set_preference("browser.search.geoip.url", "")
    profile.set_preference("geo.wifi.uri", "")
    profile.set_preference("services.sync.prefs.sync.layout.spellcheckDefault", False)
    profile.set_preference("services.sync.prefs.sync.spellchecker.dictionary", False)
    profile.set_preference("browser.formfill.enable", False)
    profile.set_preference("browser.microsummary.updateGenerators", False)
    profile.set_preference("browser.search.update", False)
    profile.set_preference("browser.urlbar.filter.javascript", False)
    profile.set_preference("dom.allow_scripts_to_close_windows", True)
    #profile.set_preference("dom.disable_window_status_change", False)  Not necessary
    #profile.set_preference("dom. event. contextmenu. enabled", True)
    profile.set_preference("network.cookie.enableForCurrentSessionOnly", True)
    profile.set_preference("network.http.max-connections", 10000)
    profile.set_preference("privacy.sanitize.sanitizeOnShutdown", True)
    profile.set_preference("privacy.spoof_english", 2)
    profile.set_preference("browser.newtabpage.activity-stream.asrouter.userprefs.cfr.addons", False)
    profile.set_preference("browser.newtabpage.activity-stream.asrouter.userprefs.cfr.features", False)
    profile.set_preference("browser.search.suggest.enabled", False)
    profile.set_preference("xpinstall.whitelist.required", True)
    profile.set_preference("app.update.download.promptMaxAttempts",0)
    profile.set_preference("network.protocol-handler.external.mailto", False)
    profile.set_preference("security.tls.enable_post_handshake_auth", True)
    profile.set_preference("security.tls.version.min", 3)
    profile.set_preference("security.ssl.require_safe_negotiation", True)
    profile.set_preference("security.ssl.treat_unsafe_negotiation_as_broken", True)
    profile.set_preference("security.strict_security_checks.enabled", True)
    profile.set_preference("security.dialog_enable_delay", 2100)
    profile.set_preference("browser.ssl_override_behavior", 2)
    profile.set_preference("browser.aboutConfig.showWarning", False)
    profile.set_preference("browser.safebrowsing.enabled", True)
    profile.set_preference("browser.safebrowsing.malware.enabled", True)
    if(not disable_downloads):
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.panel.shown", False)
        #profile.set_preference("browser.download.dir", None)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/*")
        profile.set_preference("browser.helperApps.neverAsk.openFile", "application/*")
        profile.set_preference("pdfjs.disabled", True)
    #profile.set_preference("browser.translation.neverForLanguages", "*")

    if(autoload_videos):
        profile.set_preference("dom.media.autoplay.autoplay-policy-api", True)
        profile.set_preference("media.autoplay.enabled.user-gestures-needed", False)
        profile.set_preference("media.block-autoplay-until-in-foreground", False)
        profile.set_preference("media.autoplay.default", 0)
        profile.set_preference("dom.require_user_interaction_for_beforeunload", False)
        profile.set_preference("browser.preferences.defaultPerformanceSettings.enabled", True)
    else:
        profile.set_preference("dom.media.autoplay.autoplay-policy-api", False)
        profile.set_preference("media.autoplay.enabled.user-gestures-needed", True)
        profile.set_preference("media.block-autoplay-until-in-foreground", True)
        profile.set_preference("media.autoplay.default", 1)
        profile.set_preference("browser.preferences.defaultPerformanceSettings.enabled", False)



    #Test
    profile.set_preference("network.manage-offline-status", True)
    profile.set_preference("browser.offline", True)

    options.add_argument("--lang=en")

    capabilities['marionette'] = True
    capabilities["dom.popup_maximum"] = tabs_per_window
    capabilities['browserName'] = choice(["android", "chrome", "firefox", "htmlunit",
                                        "internet explorer", "iPhone", "iPad", "opera", "safari"])
    capabilities['version'] = ""
    capabilities['platform'] = ""
    capabilities["locationContextEnabled"] = False
    capabilities["databaseEnabled"] = False
    capabilities["applicationCacheEnabled"] = False
    capabilities["browserConnectionEnabled"] = False
    capabilities["webStorageEnabled"] = False

    # Not tested
    #if(max_cache_RAM_KB): profile.set_preference("browser.cache.memory.capacity",max_cache_RAM_KB)

    if(not load_images):
        profile.set_preference("permissions.default.image", 2)

    if(disable_javascript):
        capabilities["javascriptEnabled"] = False

    #breakpoint()

    http_proxy = proxys.get("httpProxy", None)
    ssl_proxy = proxys.get("sslProxy", None)
    ftp_proxy = proxys.get("ftpProxy", None)
    socks_proxy = proxys.get("socksProxy", None)


    if(not http_proxy is None and len(http_proxy)): 
        profile.set_preference("network.proxy.type", 1)
        http_proxy = http_proxy.split(':')
        profile.set_preference("network.proxy.http", http_proxy[0])
        profile.set_preference("network.proxy.http_port", int(http_proxy[1])) 
    if(not ssl_proxy is None and len(ssl_proxy)): 
        profile.set_preference("network.proxy.type", 1)
        ssl_proxy = ssl_proxy.split(':')
        profile.set_preference("network.proxy.ssl", ssl_proxy[0])
        profile.set_preference("network.proxy.ssl_port", int(ssl_proxy[1])) 
    if(not ftp_proxy is None and len(ftp_proxy)): 
        profile.set_preference("network.proxy.type", 1)
        ftp_proxy = ftp_proxy.split(':')
        profile.set_preference("network.proxy.ftp", ftp_proxy[0])
        profile.set_preference("network.proxy.ftp_port", int(ftp_proxy[1])) 
    if(not socks_proxy is None and len(socks_proxy)):
        profile.set_preference("network.proxy.type", 1)
        socks_proxy = socks_proxy.split(':')
        profile.set_preference("network.proxy.socks", socks_proxy[0])
        profile.set_preference("network.proxy.socks_port", int(socks_proxy[1])) 

    return options, profile, capabilities