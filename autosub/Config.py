# Autosub Config.py - https://code.google.com/p/autosub-bootstrapbill/
#
# The Autosub config Module
#

# python 2.5 support
from __future__ import with_statement

import os
import logging
import codecs

from ConfigParser import SafeConfigParser

import autosub
import autosub.version as version

# Autosub specific modules

# Settings -----------------------------------------------------------------------------------------------------------------------------------------
# Location of the configuration file:
# configfile = "config.properties"
# Set the logger
log = logging.getLogger('thelogger')
#/Settings -----------------------------------------------------------------------------------------------------------------------------------------

# TODO: Webserver config, basic are done. CherryPy logging still needs a file only
# TODO: Auto restart if needed after saving config
# TODO: Make the config page pretty again
# TODO: Make user re-enter password and compare 'em to rule out typing errors
# TODO: Code cleanup?


def ReadConfig(configfile):
    """
    Read the config file and set all the variables.
    """

    # Read config file
    cfg = SafeConfigParser()
    try:
        with codecs.open(autosub.CONFIGFILE, 'r', autosub.SYSENCODING) as f:
            cfg.readfp(f)
    except:
        print "***************************************************************************"
        print "Config ERROR: Not a valid configuration file! Using default values instead!"
        print "***************************************************************************"
        cfg = SafeConfigParser()

    if cfg.has_section('config'):
        if cfg.has_option('config', 'path'):
            autosub.PATH = cfg.get('config', 'path')
        else:
            print "Config ERROR: Variable PATH is missing. This is required! Using current working directory instead."
            autosub.PATH = unicode(os.getcwd(), autosub.SYSENCODING)

        if cfg.has_option('config', 'downloadeng'):
            autosub.DOWNLOADENG = cfg.getboolean('config', 'downloadeng')
        else:
            autosub.DOWNLOADENG = False

        if cfg.has_option('config', 'downloaddutch'):
            autosub.DOWNLOADDUTCH = cfg.getboolean('config', 'downloaddutch')
        else:
            autosub.DOWNLOADDUTCH = True

        if cfg.has_option('config', 'minmatchscore'):
            autosub.MINMATCHSCORE = int(cfg.get('config', 'minmatchscore'))
        else:
            autosub.MINMATCHSCORE = 0

        if cfg.has_option('config', 'checksub'):
            autosub.SCHEDULERCHECKSUB = int(cfg.get('config', 'checksub'))
            # CHECKSUB may only be ran 4 times a day, to prevent the API key from being banned
            
            if autosub.SCHEDULERCHECKSUB < 21600:
                print "Config WARNING: checksub variable is lower then 21600! This is not allowed, this is to prevent our API-key from being banned."
                autosub.SCHEDULERCHECKSUB = 21600  # Run every 6 hours
        else:
            autosub.SCHEDULERCHECKSUB = 21600  # Run every 6 hours

        if cfg.has_option("config", "rootpath"):
            autosub.ROOTPATH = cfg.get("config", "rootpath")
        else:
            print "Config ERROR: Variable ROOTPATH is missing. This is required! Using current working directory instead."
            autosub.ROOTPATH = unicode(os.getcwd(), autosub.SYSENCODING)

        if cfg.has_option("config", "fallbacktoeng"):
            autosub.FALLBACKTOENG = cfg.getboolean("config", "fallbacktoeng")
        else:
            autosub.FALLBACKTOENG = True

        if cfg.has_option("config", "subeng"):
            autosub.SUBENG = cfg.get("config", "subeng")
        else:
            autosub.SUBENG = 'en'

        if cfg.has_option("config", "subnl"):
            autosub.SUBNL = cfg.get("config", "subnl")
        else:
            autosub.SUBNL = u""

        if cfg.has_option("config", "notifyen"):
            autosub.NOTIFYEN = cfg.getboolean("config", "notifyen")
        else:
            autosub.NOTIFYEN = True

        if cfg.has_option("config", "notifynl"):
            autosub.NOTIFYNL = cfg.getboolean("config", "notifynl")
        else:
            autosub.NOTIFYNL = True

        if cfg.has_option("config", "workdir"):
            autosub.PATH = cfg.get("config", "workdir")
            print "Config WARNING: Workdir is an old variable. Replace it with 'path'."

        if cfg.has_option("config", "logfile"):
            autosub.LOGFILE = cfg.get("config", "logfile")
        else:
            print "Config ERROR: Variable LOGFILE is missing. This is required! Using 'AutoSubService.log' instead."
            autosub.LOGFILE = u"AutoSubService.log"

        if cfg.has_option("config", "subcodec"):
            autosub.SUBCODEC = cfg.get("config", "subcodec")
        else:
            autosub.SUBCODEC = u'windows-1252'
        
        if cfg.has_option("config", "configversion"):
            autosub.CONFIGVERSION = int(cfg.get("config", "configversion"))
        else:
            autosub.CONFIGVERSION = 1

        if cfg.has_option("config", "postprocesscmd"):
            autosub.POSTPROCESSCMD = cfg.get("config", "postprocesscmd")
        
        if cfg.has_option("config", "configversion"):
            autosub.CONFIGVERSION = int(cfg.get("config", "configversion"))
        else:
            autosub.CONFIGVERSION = 1
            
        if cfg.has_option("config", "launchbrowser"):
            autosub.LAUNCHBROWSER = cfg.getboolean("config", "launchbrowser")
        
        if cfg.has_option("config", "skiphiddendirs"):
            autosub.SKIPHIDDENDIRS = cfg.getboolean("config", "skiphiddendirs")
        else:
            autosub.SKIPHIDDENDIRS = False
        
        if cfg.has_option("config", "homelayoutfirst"):
            autosub.HOMELAYOUTFIRST = cfg.get("config", "homelayoutfirst")
        else:
            autosub.HOMELAYOUTFIRST = u"Wanted"
        
        if cfg.has_option("config", "englishsubdelete"):
            autosub.ENGLISHSUBDELETE = cfg.getboolean("config", "englishsubdelete")
        else:
            autosub.ENGLISHSUBDELETE = False
            
        if cfg.has_option("config", "podnapisilang"):
            autosub.PODNAPISILANG = cfg.get("config", "podnapisilang")
        else:
            autosub.PODNAPISILANG = u"Both"
            
        if cfg.has_option("config", "subscenelang"):
            autosub.SUBSCENELANG = cfg.get("config", "subscenelang")
        else:
            autosub.SUBSCENELANG = u"Both"
                     
        if cfg.has_option("config", "opensubtitleslang"):
            autosub.OPENSUBTITLESLANG = cfg.get("config", "opensubtitleslang")
        else:
            autosub.OPENSUBTITLESLANG = u"Both"

        if cfg.has_option("config", "opensubtitlesuser"):
            autosub.OPENSUBTITLESUSER = cfg.get("config", "opensubtitlesuser")
        else:
            autosub.OPENSUBTITLESUSER = u""

        if cfg.has_option("config", "opensubtitlespasswd"):
            autosub.OPENSUBTITLESPASSWD = cfg.get("config", "opensubtitlespasswd")
        else:
            autosub.OPENSUBTITLESPASSWD = u"" 
            
        if cfg.has_option("config", "addic7edlang"):
            autosub.ADDIC7EDLANG = cfg.get("config", "addic7edlang")
        else:
            autosub.ADDIC7EDLANG = u"None"

        if cfg.has_option("config", "addic7eduser"):
            autosub.ADDIC7EDUSER = cfg.get("config", "addic7eduser")
        else:
            autosub.ADDIC7EDUSER = u""

        if cfg.has_option("config", "addic7edpasswd"):
            autosub.ADDIC7EDPASSWD = cfg.get("config", "addic7edpasswd")
        else:
            autosub.ADDIC7EDPASSWD = u""
            
        if cfg.has_option("config", "webdl"):
            autosub.WEBDL = cfg.get("config", "webdl")
        else:
            autosub.WEBDL = u"Both"
        
        
    else:
        # config section is missing
        print "Config ERROR: Config section is missing. This is required, it contains vital options! Using default values instead!"
        print "Config ERROR: Variable ROOTPATH is missing. This is required! Using current working directory instead."
        autosub.PATH = unicode(os.getcwd(), autosub.SYSENCODING)
        autosub.DOWNLOADENG = False
        autosub.DOWNLOADDUTCH = True        
        autosub.MINMATCHSCORE = 8
        autosub.SCHEDULERCHECKSUB = 28800
        print "Config ERROR: Variable ROOTPATH is missing. This is required! Using current working directory instead."
        autosub.ROOTPATH = unicode(os.getcwd(), autosub.SYSENCODING)
        autosub.FALLBACKTOENG = True
        autosub.SUBENG = u'en'
        autosub.SUBNL = u""
        autosub.NOTIFYEN = True
        autosub.NOTIFYNL = True
        autosub.SKIPHIDDENDIRS = False
        print "Config ERROR: Variable LOGFILE is missing. This is required! Using 'AutoSubService.log' instead."
        autosub.LOGFILE = u"AutoSubService.log"
        autosub.CONFIGVERSION = version.configversion
        autosub.HOMELAYOUTFIRST = u"Wanted"
        autosub.ENGLISHSUBDELETE = False
        autosub.PODNAPISILANG = u"Both"
        autosub.SUBSCENELANG = u"Both"
        autosub.OPENSUBTITLESLANG = u"Both"
        autosub.OPENSUBTITLESUSER = u""
        autosub.OPENSUBTITLESPASSWD = u""
        autosub.ADDIC7EDLANG = u"None"
        autosub.ADDIC7EDUSER = u""
        autosub.ADDIC7EDPASSWD = u""
        autosub.WEBDL = u"Both"
        autosub.SUBCODEC = u'windows=1252'

    if cfg.has_section('logfile'):
        if cfg.has_option("logfile", "loglevel"):
            autosub.LOGLEVEL = cfg.get("logfile", "loglevel")
            if autosub.LOGLEVEL.lower() == u'error':
                autosub.LOGLEVEL = logging.ERROR
            elif autosub.LOGLEVEL.lower() == u"warning":
                autosub.LOGLEVEL = logging.WARNING
            elif autosub.LOGLEVEL.lower() == u"debug":
                autosub.LOGLEVEL = logging.DEBUG
            elif autosub.LOGLEVEL.lower() == u"info":
                autosub.LOGLEVEL = logging.INFO
            elif autosub.LOGLEVEL.lower() == u"critical":
                autosub.LOGLEVEL = logging.CRITICAL
        else:
            autosub.LOGLEVEL = logging.INFO

        if cfg.has_option("logfile", "loglevelconsole"):
            autosub.LOGLEVELCONSOLE = cfg.get("logfile", "loglevelconsole")
            if autosub.LOGLEVELCONSOLE.lower() == u'error':
                autosub.LOGLEVELCONSOLE = logging.ERROR
            elif autosub.LOGLEVELCONSOLE.lower() == u"warning":
                autosub.LOGLEVELCONSOLE = logging.WARNING
            elif autosub.LOGLEVELCONSOLE.lower() == u"debug":
                autosub.LOGLEVELCONSOLE = logging.DEBUG
            elif autosub.LOGLEVELCONSOLE.lower() == u"info":
                autosub.LOGLEVELCONSOLE = logging.INFO
            elif autosub.LOGLEVELCONSOLE.lower() == u"critical":
                autosub.LOGLEVELCONSOLE = logging.CRITICAL
        else:
            autosub.LOGLEVELCONSOLE = logging.ERROR

        if cfg.has_option("logfile", "logsize"):
            autosub.LOGSIZE = int(cfg.get("logfile", "logsize"))
        else:
            autosub.LOGSIZE = 1000000

        if cfg.has_option("logfile", "lognum"):
            autosub.LOGNUM = int(cfg.get("logfile", "lognum"))
        else:
            autosub.LOGNUM = 3

    else:
        # Logfile section is missing, so set defaults for all options
        autosub.LOGLEVEL = logging.INFO
        autosub.LOGLEVELCONSOLE = logging.ERROR
        autosub.LOGSIZE = 1000000
        autosub.LOGNUM = 1

    if cfg.has_section('webserver'):
        if cfg.has_option('webserver', 'webserverip') and cfg.has_option('webserver', 'webserverport'):
            autosub.WEBSERVERIP = cfg.get('webserver', 'webserverip')
            autosub.WEBSERVERPORT = int(cfg.get('webserver', 'webserverport'))
            
        else:
            print "Config ERROR: Webserver IP and port are required! Now setting the default values (0.0.0.0:8083)."
            autosub.WEBSERVERIP = "0.0.0.0"
            autosub.WEBSERVERPORT = 8083
            
        if cfg.has_option('webserver', 'webroot'):
            autosub.WEBROOT = cfg.get('webserver', 'webroot')
        else:
            autosub.WEBROOT = ''
            
        if cfg.has_option('webserver', 'username') and cfg.has_option('webserver', 'password'):
            autosub.USERNAME = cfg.get('webserver', 'username')
            autosub.PASSWORD = cfg.get('webserver', 'password')
        elif cfg.has_option('webserver', 'username') or cfg.has_option('webserver', 'password'):
            print "Config ERROR: Both username and password are required! Now starting without authentication!"
    else:
        print "Config ERROR: The webserver section is required! Now setting the default values (0.0.0.0:8083)."
        print "Config WARNING: The webserver is started without authentication!"
        autosub.WEBSERVERIP = '0.0.0.0'
        autosub.WEBSERVERPORT = 8083
        autosub.WEBROOT = ''

    if cfg.has_section('skipshow'):
        # Try to read skipshow section in the config
        autosub.SKIPSHOW = dict(cfg.items('skipshow'))
        # The following 4 lines convert the skipshow to uppercase. And also convert the variables to a list
        autosub.SKIPSHOWUPPER = {}
        for x in autosub.SKIPSHOW:
            autosub.SKIPSHOWUPPER[x.upper()] = [y.strip() for y in autosub.SKIPSHOW[x].split(',')]
    else:
        autosub.SKIPSHOW = {}
        autosub.SKIPSHOWUPPER = {}

    if cfg.has_section('namemapping'):
        autosub.USERNAMEMAPPING = dict(cfg.items('namemapping'))
        autosub.USERNAMEMAPPINGUPPER = {}
        for x in autosub.USERNAMEMAPPING.keys():
            autosub.USERNAMEMAPPINGUPPER[x.upper()] = autosub.USERNAMEMAPPING[x]
    else:
        autosub.USERNAMEMAPPING = {}
        autosub.USERNAMEMAPPINGUPPER = {}
    
    if cfg.has_section('addic7edmapping'):
        autosub.USERADDIC7EDMAPPING = dict(cfg.items('addic7edmapping'))
        autosub.USERADDIC7EDMAPPINGUPPER = {}
        for x in autosub.USERADDIC7EDMAPPING.keys():
            autosub.USERADDIC7EDMAPPINGUPPER[x.upper()] = autosub.USERADDIC7EDMAPPING[x]
    else:
        autosub.USERADDIC7EDMAPPING = {}
        autosub.USERADDIC7EDMAPPINGUPPER = {}

    if cfg.has_section('notify'):
            #Mail
            if cfg.has_option('notify', 'notifymail'):
                autosub.NOTIFYMAIL = cfg.getboolean('notify', 'notifymail')
            else:
                autosub.NOTIFYMAIL = False

            if cfg.has_option('notify', 'mailsrv'):
                autosub.MAILSRV = cfg.get('notify', 'mailsrv')
            else:
                autosub.MAILSRV = u"smtp.gmail.com:587"

            if cfg.has_option('notify', 'mailfromaddr'):
                autosub.MAILFROMADDR = cfg.get('notify', 'mailfromaddr')
            else:
                autosub.MAILFROMADDR = u"example@gmail.com"

            if cfg.has_option('notify', 'mailtoaddr'):
                autosub.MAILTOADDR = cfg.get('notify', 'mailtoaddr')
            else:
                autosub.MAILTOADDR = u"example@gmail.com"

            if cfg.has_option('notify', 'mailusername'):
                autosub.MAILUSERNAME = cfg.get('notify', 'mailusername')
            else:
                autosub.MAILUSERNAME = u"example@gmail.com"

            if cfg.has_option('notify', 'mailpassword'):
                autosub.MAILPASSWORD = cfg.get('notify', 'mailpassword')
            else:
                autosub.MAILPASSWORD = u"mysecretpassword"

            if cfg.has_option('notify', 'mailsubject'):
                autosub.MAILSUBJECT = cfg.get('notify', 'mailsubject')
            else:
                autosub.MAILSUBJECT = u"Auto-Sub downloaded"

            if cfg.has_option('notify', 'mailencryption'):
                autosub.MAILENCRYPTION = cfg.get('notify', 'mailencryption')
            else:
                autosub.MAILENCRYPTION = u"TLS"
                
            if cfg.has_option('notify', 'mailauth'):
                autosub.MAILAUTH = cfg.get('notify', 'mailauth')
            else:
                autosub.MAILAUTH = u""
       
            #Growl
            if cfg.has_option('notify', 'notifygrowl'):
                autosub.NOTIFYGROWL = cfg.getboolean('notify', 'notifygrowl')
            else:
                autosub.NOTIFYGROWL = False

            if cfg.has_option('notify', 'growlhost'):
                autosub.GROWLHOST = cfg.get('notify', 'growlhost')
            else:
                autosub.GROWLHOST = u"127.0.0.1"

            if cfg.has_option('notify', 'growlport'):
                autosub.GROWLPORT = cfg.get('notify', 'growlport')
            else:
                autosub.GROWLPORT = u"23053"

            if cfg.has_option('notify', 'growlpass'):
                autosub.GROWLPASS = cfg.get('notify', 'growlpass')
            else:
                autosub.GROWLPASS = u"mysecretpassword"

            #Twitter
            if cfg.has_option('notify', 'notifytwitter'):
                autosub.NOTIFYTWITTER = cfg.getboolean('notify', 'notifytwitter')
            else:
                autosub.NOTIFYTWITTER = False

            if cfg.has_option('notify', 'twitterkey'):
                autosub.TWITTERKEY = cfg.get('notify', 'twitterkey')
            else:
                autosub.TWITTERKEY = u"token key"

            if cfg.has_option('notify', 'twittersecret'):
                autosub.TWITTERSECRET = cfg.get('notify', 'twittersecret')
            else:
                autosub.TWITTERSECRET = u"token secret"

            #Notify My Android
            if cfg.has_option('notify', 'notifynma'):
                autosub.NOTIFYNMA = cfg.getboolean('notify', 'notifynma')
            else:
                autosub.NOTIFYNMA = False

            if cfg.has_option('notify', 'nmaapi'):
                autosub.NMAAPI = cfg.get('notify', 'nmaapi')
            else:
                autosub.NMAAPI = u"API key"
            
            if cfg.has_option('notify', 'nmapriority'):
                autosub.NMAPRIORITY = int(cfg.get('notify', 'nmapriority'))
            else:
                autosub.NMAPRIORITY = 0
            
            #Prowl    
            if cfg.has_option('notify', 'notifyprowl'):
                autosub.NOTIFYPROWL = cfg.getboolean('notify', 'notifyprowl')
            else:
                autosub.NOTIFYPROWL = False

            if cfg.has_option('notify', 'prowlapi'):
                autosub.PROWLAPI = cfg.get('notify', 'prowlapi')
            else:
                autosub.PROWLAPI = u"API key"
            
            if cfg.has_option('notify', 'prowlpriority'):
                autosub.PROWLPRIORITY = int(cfg.get('notify', 'prowlpriority'))
            else:
                autosub.PROWLPRIORITY = 0
            
            #Pushalot - Windows Phone and Windows 8 notifier.
            if cfg.has_option('notify', 'notifypushalot'):
                autosub.NOTIFYPUSHALOT = cfg.getboolean('notify', 'notifypushalot')
            else:
                autosub.NOTIFYPUSHALOT = False

            if cfg.has_option('notify', 'pushalotapi'):
                autosub.PUSHALOTAPI = cfg.get('notify', 'pushalotapi')
            else:
                autosub.PUSHALOTAPI = u"API key"

            #Pushbullet.
            if cfg.has_option('notify', 'notifypushbullet'):
                autosub.NOTIFYPUSHBULLET = cfg.getboolean('notify', 'notifypushbullet')
            else:
                autosub.NOTIFYPUSHBULLET = False

            if cfg.has_option('notify', 'pushbulletapi'):
                autosub.PUSHBULLETAPI = cfg.get('notify', 'pushbulletapi')
            else:
                autosub.PUSHBULLETAPI = u"API key"
            
            #Pushover.
            if cfg.has_option('notify', 'notifypushover'):
                autosub.NOTIFYPUSHOVER = cfg.getboolean('notify', 'notifypushover')
            else:
                autosub.NOTIFYPUSHOVER = False

            if cfg.has_option('notify', 'pushoverapi'):
                autosub.PUSHOVERAPI = cfg.get('notify', 'pushoverapi')
            else:
                autosub.PUSHOVERAPI = u"API key"
            
            #Boxcar - iOS and OSX notifier.
            if cfg.has_option('notify', 'notifyboxcar2'):
                autosub.NOTIFYBOXCAR2 = cfg.getboolean('notify', 'notifyboxcar2')
            else:
                autosub.NOTIFYBOXCAR2 = False
            
            if cfg.has_option('notify', 'boxcar2token'):
                autosub.BOXCAR2TOKEN = cfg.get('notify', 'boxcar2token')
            else:
                autosub.BOXCAR2TOKEN = u"Boxcar2 access token"
            
            #Plex Media Server
            if cfg.has_option('notify', 'notifyplex'):
                autosub.NOTIFYPLEX = cfg.getboolean('notify', 'notifyplex')
            else:
                autosub.NOTIFYPLEX = False
            
            if cfg.has_option('notify', 'plexserverhost'):
                autosub.PLEXSERVERHOST = cfg.get('notify', 'plexserverhost')
            else:
                autosub.PLEXSERVERHOST = u"127.0.0.1"
            
            if cfg.has_option('notify', 'plexserverport'):
                autosub.PLEXSERVERPORT = cfg.get('notify', 'plexserverport')
            else:
                autosub.PLEXSERVERPORT = u"32400"
            
    else:
        # notify section is missing
        autosub.NOTIFYMAIL = False
        autosub.MAILSRV = u"smtp.gmail.com:587"
        autosub.MAILFROMADDR = u"example@gmail.com"
        autosub.MAILTOADDR = u"example@gmail.com"
        autosub.MAILUSERNAME = u"example@gmail.com"
        autosub.MAILPASSWORD = u"mysecretpassword"
        autosub.MAILSUBJECT = u"Subs info"
        autosub.MAILENCRYPTION = u"TLS"
        autosub.NOTIFYGROWL = False
        autosub.GROWLHOST = u"127.0.0.1"
        autosub.GROWLPORT = u"23053"
        autosub.GROWLPASS = u"mysecretpassword"
        autosub.NOTIFYTWITTER = False
        autosub.TWITTERKEY = u"token key"
        autosub.TWITTERSECRET = u"token secret"
        autosub.NOTIFYNMA = False
        autosub.NMAAPI = u"API key"
        autosub.NMAPRIORITY = 0
        autosub.PROWLAPI = u"API key"
        autosub.NOTIFYPROWL = False
        autosub.PROWLPRIORITY = 0
        autosub.NOTIFYPUSHALOT = False
        autosub.PUSHALOTAPI = u"API key"
        autosub.NOTIFYPUSHBULLET = False
        autosub.PUSHBULLETAPI = u"API key"
        autosub.NOTIFYPUSHOVER = False
        autosub.PUSHOVERAPI = u"API key"
        autosub.NOTIFYBOXCAR2 = False
        autosub.BOXCAR2TOKEN = u"Boxcar2 access token"
        autosub.NOTIFYPLEX = False
        autosub.PLEXSERVERHOST = u"127.0.0.1"
        autosub.PLEXSERVERPORT = u"32400"

    if cfg.has_section('dev'):
        if cfg.has_option('dev', 'apikey'):
            autosub.APIKEY = cfg.get('dev', 'apikey')

    # Settings
    autosub.SHOWID_CACHE = {}

    autosub.NAMEMAPPING = {
            "Against the Wall" :"1836237",
            "alcatraz" :"1728102",
            "almost human" :"2654580",
            "alphas" :"1183865",
            "american dad" :"0397306",
            "american horror story" :"1844624",
            "appropriate adult" :"1831575",
            "Are You There Chelsea" :"1826989",
            "atlantis" :"2705602",
            "atlantis 2013" :"2705602",
            "awkward" : "1663676",
            "back in the game" : "2655470",
            "Bates Motel" :"2188671",
            "beauty and the beast" :"2193041",
            "beauty and the beast 2012" :"2193041",
            "betrayal" :"2751074",
            "blue bloods" :"1595859",
            "boardwalk empire" : "0979432",
            "bob's burgers" :"1561755",
            "bobs burgers" :"1561755",
            "Body of Proof" :"1587669",
            "borgen" :"1526318",
            "breakout kings" :"1590961",
            "breaking bad" : "903747",
            "Castle (2009)" :"1219024",
            "castle 2009" :"1219024",
            "charlie's angels 2011" :"1760943",
            "Charlies Angels 2011" :"1760943",
            "chicago fire" : "2261391",
            "chicago fire (2012)" : "2261391",
            "chicago pd" : "2805096",
            "Common Law 2012" :"1771072",
            "continuum" : "1954347",
            "covert affairs" :"1495708",
            "cracked (2013)" : "2078576",
            "criminal minds" :"0452046",
            "csi" :"0247082",
            "csi crime scene investigation" :"0247082",
            "Csi Miami" :"0313043",
            "csi new york" :"0395843",
            "csi ny" :"0395843",
            "Da Vinci's Demons" :"2094262",
            "Dallas 2012" :"1723760",
            "desperate housewives" :"0410975",
            "devious maids" : "2226342",
            "Doctor Who" : "0436992",
            "Doctor Who (2005)" : "0436992",
            "don't trust the b---- in apartment 23" :"1819509",
            "dont trust the bitch in apartment 23" :"1819509",
            "dracula" :"2296682",
            "dracula (2013)" :"2296682",
            "DreamWorks Dragons: Riders of Berk" :"2325846",
            "eastbound & down" :"0866442",
            "eastbound and down" :"0866442",
            "emily owens m d" :"2290339",
            "Falling skies" :"1462059",
            "Fast N Loud" : "2346169",
            "Femme Fatales" :"1841108",
            "Franklin and Bash" :"1600199",
            "Free Agents" :"1839481",
            "Free Agents Us" :"1839481",
            "fringe" :"1119644",
            "game of thrones" : "0944947",
            "Glee" : "1327801",
            "Grey's Anatomy" :"0413573",
            "Greys Anatomy" :"0413573",
            "grimm" :"1830617",
            "harry's law" :"1582453",
            "Harrys Law" :"1582453",
            "haven" :"1519931",
            "Hawaii Five 0" :"1600194",
            "Hawaii Five 0 2010" :"1600194",
            "Hawaii Five-0" :"1600194",
            "hawaii five-0 2010" :"1600194",
            "hello ladies" :"2378794",
            "homeland" :"1796960",
            "hostages" :"2647258",
            "house of cards 2013" :"1856010",
            "how i met your mother" : "0460649",
            "How To Survive The End Of The World" : "3377330",
            "Intelligence us" : "2693776",
            "king" :"1804880",
            "kings of crash" : "2623754",
            "Last Man Standing" : "1828327",
            "Last Man Standing Us" : "1828327",
            "law and order svu" :"0203259",
            "law and order uk" :"1166893",
            "longmire" : "1836037",
            "luck" :"1578887",
            "luther" :"1474684",
            "Man Up" :"1828238",
            "marvel's agents of s h i e l d" :"2364582",
            "marvels agents of s h i e l d" :"2364582",
            "marvel agents of shield": "2364582",
            "agents of s h i e l d" :"2364582",
            "masters of sex" :"2137109",
            "Melissa And Joey" :"1597420",
            "Merlin" :"1199099",
            "Merlin 2008" :"1199099",
            "Mike and Molly" :"1608180",
            "missing 2012" :"1828246",
            "mockingbird lane" :"2130271",
            "modern family" :"1442437",
            "moonshiners" : "1877005",
            "Mr Sunshine" :"1583638",
            "nashville" :"2281375",
            "nashville 2012" :"2281375",
            "ncis" :"0364845",
            "Ncis Los Angeles" :"1378167",
            "Necessary Roughness" :"1657505",
            "new girl" : "1826940",
            "new tricks" :"0362357",
            "nip tuck" :"0361217",
            "nip-tuck" :"0361217",
            "once upon a time" :"1843230",
            "once upon time" :"1843230",
            "once upon a time 2011" :"1843230",
            "once upon a time in wonderland" :"2802008",
            "oppenheimer (1980)" : "0078037",
            "Parks and Recreation" : "1266020",
            "person of interest" :"1839578",
            "played" :"2886812",
            "pretty little liars" : "1578873",
            "Prime Suspect Us" :"1582456",
            "primeval new world" :"2295953",
            "ray donovan" :"2249007",
            "reign 2013" :"2710394",
            "Revolution" :"2070791",
            "Revolution 2012" :"2070791",
            "Rizzoli And Isles" :"1551632",
            "rookie blue" : "1442065",
            "Scandal" :"1837576",
            "scandal (2012)" :"1837576",
            "Scandal 2012" :"1837576",
            "Scandal US" :"1837576",
            "scott and bailey" :"1843678",
            "sean saves the world" :"2715776",
            "Shameless Us" :"1586680",
            "silent witness" :"0115355",
            "Sinbad" :"1979918",
            "sleepy hollow" :"2647544",
            "snooki and jwoww" : "2083701",
            "sons of anarchy" : "1124373",
            "South Park" : "0121955",
            "Spartacus" :"1442449",
            "Spartacus Blood And Sand" :"1442449",
            "Spartacus Gods Of The Arena" :"1758429",
            "spartacus vengeance" :"1442449",
            "star wars the clone wars" :"0458290",
            "suburgatory" :"1741256",
            "suits" :"1632701",
            "sun, sex and suspicious parents" : "1832153",
            "super fun night" :"2298477",
            "The After" : "3145422",
            "the americans 2013" : "2149175",
            "the americans (2013)" : "2149175",
            "the americans" : "2149175",
            "the big bang theory" : "898266",
            "the biggest loser" :"0429318",
            "the blacklist" :"2741602",
            "the client list" :"2022170",
            "the closer" :"0458253",
            "the dukes of hazzard" : "78607",
            "the gadget show" :"0830851",
            "The Kennedys" :"1567215",
            "the killing (2011)" :"1637727",
            "The La Complex" :"1794147",
            "The Legend Of Korra" :"1695360",
            "the lying game" :"1798274",
            "the mentalist" :"1196946",
            "the newsroom (2012)" :"1870479",
            "the newsroom 2012" :"1870479",
            "the o c" :"0362359",
            "the office us" :"0386676",
            "the originals" :"2632424",
            "the piglet files" : "0098895",
            "the protector" :"1836417",
            "The River" :"1836195",
            "the tomorrow people us" :"2660734",
            "the walking dead" : "1520211",
            "the wire" : "306414",
            "the wrong mans" :"2603596",
            "thundercats 2011" :"1666278",
            "Touch" :"1821681",
            "trophy wife" :"2400736",
            "two and a half men" : "0369179",
            "under the dome" : "1553656",
            "unforgettable" :"1842530",
            "untouchables-the venture bros" :"0417373",
            "Up All Night 2011" :"1843323",
            "utopia" :"2384811",
            "Vegas" :"2262383",
            "white collar" :"1358522",
            "xiii the series 2011" :"1713938"
    }
    
    autosub.NAMEMAPPINGUPPER = {}
    for x in autosub.NAMEMAPPING.keys():
        autosub.NAMEMAPPINGUPPER[x.upper()] = autosub.NAMEMAPPING[x]

    autosub.LASTESTDOWNLOAD = []

    if autosub.CONFIGVERSION < version.configversion:
        upgradeConfig(autosub.CONFIGVERSION, version.configversion)
    elif autosub.CONFIGVERSION > version.configversion:
        print "Config: ERROR! Config version higher then this version of AutoSub supports. Update AutoSub!"
        os._exit(1)

def SaveToConfig(section=None, variable=None, value=None):
    """
    Add a variable and value to section in the config file.
    
    Keyword arguments:
    section -- Section to with the variable - value pair will be added
    variable -- Option that will be added to the config file
    value -- Value of the variable that will be added
    """

    cfg = SafeConfigParser()
    try:
        with codecs.open(autosub.CONFIGFILE, 'r', autosub.SYSENCODING) as f:
            cfg.readfp(f)
    except:
        #no config yet
        pass

    if cfg.has_section(section):
        cfg.set(section, variable.encode('utf8'), value.encode('utf8'))
        edited = True
    else:
        cfg.add_section(section)
        cfg.set(section, variable.encode('utf8'), value.encode('utf8'))
        edited = True

    if edited:
        with open(autosub.CONFIGFILE, 'wb') as cfile:
            cfg.write(cfile)


def applynameMapping():
    """
    Read namemapping in the config file.
    """
    cfg = SafeConfigParser()
    try:
        with codecs.open(autosub.CONFIGFILE, 'r', autosub.SYSENCODING) as f:
            cfg.readfp(f)
    except:
        #no config yet
        pass
    
    autosub.SHOWID_CACHE = {}
    if cfg.has_section("namemapping"):
        autosub.USERNAMEMAPPING = dict(cfg.items('namemapping'))
    else:
        autosub.USERNAMEMAPPING = {}
    autosub.USERNAMEMAPPINGUPPER = {}
    for x in autosub.USERNAMEMAPPING.keys():
        autosub.USERNAMEMAPPINGUPPER[x.upper()] = autosub.USERNAMEMAPPING[x]

def applyAddic7edMapping():
    """
    Read addic7edmapping in the config file.
    """
    cfg = SafeConfigParser()
    try:
        with codecs.open(autosub.CONFIGFILE, 'r', autosub.SYSENCODING) as f:
            cfg.readfp(f)
    except:
        #no config yet
        pass
    
    autosub.SHOWID_CACHE = {}
    if cfg.has_section("addic7edmapping"):
        autosub.USERADDIC7EDMAPPING = dict(cfg.items('addic7edmapping'))
    else:
        autosub.USERADDIC7EDMAPPING = {}
    autosub.USERADDIC7EDMAPPINGUPPER = {}
    for x in autosub.USERADDIC7EDMAPPING.keys():
        autosub.USERADDIC7EDMAPPINGUPPER[x.upper()] = autosub.USERADDIC7EDMAPPING[x]

def applyskipShow():
    """
    Read skipshow in the config file.
    """
    cfg = SafeConfigParser()
    try:
        with codecs.open(autosub.CONFIGFILE, 'r', autosub.SYSENCODING) as f:
            cfg.readfp(f)
    except:
        #no config yet
        pass
    
    if cfg.has_section('skipshow'):
        autosub.SKIPSHOW = dict(cfg.items('skipshow'))
    else:
        autosub.SKIPSHOW = {}
    autosub.SKIPSHOWUPPER = {}
    for x in autosub.SKIPSHOW:
        autosub.SKIPSHOWUPPER[x.upper()] = autosub.SKIPSHOW[x].split(',')


def applyAllSettings():
    """
    Read namemapping and skipshow from the config file.
    """
    applynameMapping()
    applyAddic7edMapping()
    applyskipShow()


def displaySkipshow():
    """
    Return a string containing all info from skipshow.
    After each shows skip info an '\n' is added to create multiple rows
    in a textarea.
    """
    s = ""
    for x in autosub.SKIPSHOW:
        s += x + " = " + str(autosub.SKIPSHOW[x]) + "\n"
    return s


def displayNamemapping():
    """
    Return a string containing all info from user namemapping.
    After each shows namemapping an '\n' is added to create multiple rows
    in a textarea.
    """
    s = ""
    for x in autosub.USERNAMEMAPPING:
        s += x + " = " + str(autosub.USERNAMEMAPPING[x]) + "\n"
    return s

def displayAddic7edmapping():
    """
    Return a string containing all info from user namemapping.
    After each shows addic7edmapping an '\n' is added to create multiple rows
    in a textarea.
    """
    s = ""
    for x in autosub.USERADDIC7EDMAPPING:
        s += x + " = " + str(autosub.USERADDIC7EDMAPPING[x]) + "\n"
    return s

def stringToDict(items=None):
    """
    Return a correct dict from a string
    """
    items = items.split('\r\n')
    returnitems = []

    for item in items:
        if item:
            showinfo = []
            for x in item.split('='):
                if x[-1:] == ' ':
                    x = x[:-1]
                elif x[:1] == ' ':
                    x = x[1:]
                showinfo.append(x)
            showinfo = tuple(showinfo)
            returnitems.append(showinfo)
    returnitems = dict(returnitems)
    return returnitems


def saveConfigSection():
    """
    Save stuff
    """
    section = 'config'

    cfg = SafeConfigParser()
    try:
        with codecs.open(autosub.CONFIGFILE, 'r', autosub.SYSENCODING) as f:
            cfg.readfp(f)
    except:
        #no config yet
        cfg = SafeConfigParser()
        pass

    if not cfg.has_section(section):
        cfg.add_section(section)
    
    cfg.set(section, "path", autosub.PATH)
    cfg.set(section, "downloadeng", str(autosub.DOWNLOADENG))
    cfg.set(section, "downloaddutch", str(autosub.DOWNLOADDUTCH))    
    cfg.set(section, "minmatchscore", str(autosub.MINMATCHSCORE))
    cfg.set(section, "checksub", str(autosub.SCHEDULERCHECKSUB))
    cfg.set(section, "rootpath", autosub.ROOTPATH)
    cfg.set(section, "fallbacktoeng", str(autosub.FALLBACKTOENG))
    cfg.set(section, "subeng", autosub.SUBENG)
    cfg.set(section, "subnl", autosub.SUBNL)
    cfg.set(section, "notifyen", str(autosub.NOTIFYEN))
    cfg.set(section, "notifynl", str(autosub.NOTIFYNL))
    cfg.set(section, "logfile", autosub.LOGFILE)
    cfg.set(section, "postprocesscmd", autosub.POSTPROCESSCMD)
    cfg.set(section, "configversion", str(autosub.CONFIGVERSION))
    cfg.set(section, "launchbrowser", str(autosub.LAUNCHBROWSER))
    cfg.set(section, "skiphiddendirs", str(autosub.SKIPHIDDENDIRS))
    cfg.set(section, "webdl", autosub.WEBDL)
    cfg.set(section, "subcodec", autosub.SUBCODEC)
    cfg.set(section, "homelayoutfirst", autosub.HOMELAYOUTFIRST)
    cfg.set(section, "englishsubdelete", str(autosub.ENGLISHSUBDELETE))
    cfg.set(section, "podnapisilang", autosub.PODNAPISILANG)
    cfg.set(section, "subscenelang", autosub.SUBSCENELANG)
    cfg.set(section, "opensubtitleslang", autosub.OPENSUBTITLESLANG)
    cfg.set(section, "opensubtitlesuser", autosub.OPENSUBTITLESUSER)
    cfg.set(section, "opensubtitlespasswd", autosub.OPENSUBTITLESPASSWD)
    cfg.set(section, "addic7edlang", autosub.ADDIC7EDLANG)
    cfg.set(section, "addic7eduser", autosub.ADDIC7EDUSER)
    cfg.set(section, "addic7edpasswd", autosub.ADDIC7EDPASSWD)
    
    with codecs.open(autosub.CONFIGFILE, 'wb', encoding=autosub.SYSENCODING) as cfile:
        cfg.write(cfile)


def saveLogfileSection():
    """
    Save stuff
    """
    section = 'logfile'

    cfg = SafeConfigParser()
    try:
        with codecs.open(autosub.CONFIGFILE, 'r', autosub.SYSENCODING) as f:
            cfg.readfp(f)
    except:
        #no config yet
        cfg = SafeConfigParser()
        pass

    if not cfg.has_section(section):
        cfg.add_section(section)

    cfg.set(section, "loglevel", logging.getLevelName(int(autosub.LOGLEVEL)).lower())
    cfg.set(section, "loglevelconsole", logging.getLevelName(int(autosub.LOGLEVELCONSOLE)).lower())
    cfg.set(section, "logsize", str(autosub.LOGSIZE))
    cfg.set(section, "lognum", str(autosub.LOGNUM))

    with open(autosub.CONFIGFILE, 'wb') as cfile:
        cfg.write(cfile)


def saveWebserverSection():
    """
    Save stuff
    """
    section = 'webserver'

    cfg = SafeConfigParser()
    try:
        with codecs.open(autosub.CONFIGFILE, 'r', autosub.SYSENCODING) as f:
            cfg.readfp(f)
    except:
        #no config yet
        cfg = SafeConfigParser()
        pass

    if not cfg.has_section(section):
        cfg.add_section(section)

    cfg.set(section, "webserverip", str(autosub.WEBSERVERIP))
    cfg.set(section, 'webserverport', str(autosub.WEBSERVERPORT))
    cfg.set(section, "username", autosub.USERNAME)
    cfg.set(section, "password", autosub.PASSWORD)
    cfg.set(section, "webroot", autosub.WEBROOT)

    with open(autosub.CONFIGFILE, 'wb') as cfile:
        cfg.write(cfile)


def saveSkipshowSection():
    """
    Save stuff
    """
    section = 'skipshow'

    cfg = SafeConfigParser()
    try:
        with codecs.open(autosub.CONFIGFILE, 'r', autosub.SYSENCODING) as f:
            cfg.readfp(f)
    except:
        #no config yet
        cfg = SafeConfigParser()
        pass
    
    if cfg.has_section(section):
        cfg.remove_section(section)
        cfg.add_section(section)
        with open(autosub.CONFIGFILE, 'wb') as cfile:
            cfg.write(cfile)

    for x in autosub.SKIPSHOW:
        SaveToConfig('skipshow', x, autosub.SKIPSHOW[x])

    # Set all skipshow stuff correct
    applyskipShow()

def saveUsernamemappingSection():
    """
    Save stuff
    """
    section = 'namemapping'

    cfg = SafeConfigParser()
    try:
        with codecs.open(autosub.CONFIGFILE, 'r', autosub.SYSENCODING) as f:
            cfg.readfp(f)
    except:
        #no config yet
        cfg = SafeConfigParser()
        pass

    if cfg.has_section(section):
        cfg.remove_section(section)
        cfg.add_section(section)
        with open(autosub.CONFIGFILE, 'wb') as cfile:
            cfg.write(cfile)

    for x in autosub.USERNAMEMAPPING:
        SaveToConfig('namemapping', x, autosub.USERNAMEMAPPING[x])

    # Set all namemapping stuff correct
    applynameMapping()
    
def saveUserAddic7edmappingSection():
    """
    Save stuff
    """
    section = 'addic7edmapping'

    cfg = SafeConfigParser()
    try:
        with codecs.open(autosub.CONFIGFILE, 'r', autosub.SYSENCODING) as f:
            cfg.readfp(f)
    except:
        #no config yet
        cfg = SafeConfigParser()
        pass

    if cfg.has_section(section):
        cfg.remove_section(section)
        cfg.add_section(section)
        with open(autosub.CONFIGFILE, 'wb') as cfile:
            cfg.write(cfile)

    for x in autosub.USERADDIC7EDMAPPING:
        SaveToConfig('addic7edmapping', x, autosub.USERADDIC7EDMAPPING[x])

    # Set all addic7edmapping stuff correct
    applyAddic7edMapping()

def saveNotifySection():
    """
    Save stuff
    """
    section = 'notify'

    cfg = SafeConfigParser()
    try:
        with codecs.open(autosub.CONFIGFILE, 'r', autosub.SYSENCODING) as f:
            cfg.readfp(f)
    except:
        #no config yet
        cfg = SafeConfigParser()
        pass

    if not cfg.has_section(section):
        cfg.add_section(section)

    cfg.set(section, "notifymail", str(autosub.NOTIFYMAIL))
    cfg.set(section, "mailsrv", autosub.MAILSRV)
    cfg.set(section, 'mailfromaddr', autosub.MAILFROMADDR)
    cfg.set(section, "mailtoaddr", autosub.MAILTOADDR)
    cfg.set(section, "mailusername", autosub.MAILUSERNAME)
    cfg.set(section, "mailpassword", autosub.MAILPASSWORD)
    cfg.set(section, "mailsubject", autosub.MAILSUBJECT)
    cfg.set(section, "mailencryption", autosub.MAILENCRYPTION)
    cfg.set(section, "mailauth", autosub.MAILAUTH)
    cfg.set(section, "notifygrowl", str(autosub.NOTIFYGROWL))
    cfg.set(section, "growlhost", autosub.GROWLHOST)
    cfg.set(section, "growlport", autosub.GROWLPORT)
    cfg.set(section, "growlpass", autosub.GROWLPASS)
    cfg.set(section, "notifynma", str(autosub.NOTIFYNMA))
    cfg.set(section, "nmaapi", autosub.NMAAPI)
    cfg.set(section, "nmapriority", str(autosub.NMAPRIORITY))
    cfg.set(section, "notifytwitter", str(autosub.NOTIFYTWITTER))
    cfg.set(section, "twitterkey", autosub.TWITTERKEY)
    cfg.set(section, "twittersecret", autosub.TWITTERSECRET)
    cfg.set(section, "notifyprowl", str(autosub.NOTIFYPROWL))
    cfg.set(section, "prowlapi", autosub.PROWLAPI)
    cfg.set(section, "prowlpriority", str(autosub.PROWLPRIORITY))
    cfg.set(section, "notifypushalot", str(autosub.NOTIFYPUSHALOT))
    cfg.set(section, "pushalotapi", autosub.PUSHALOTAPI)
    cfg.set(section, "notifypushbullet", str(autosub.NOTIFYPUSHBULLET))
    cfg.set(section, "pushbulletapi", autosub.PUSHBULLETAPI)
    cfg.set(section, "notifypushover", str(autosub.NOTIFYPUSHOVER))
    cfg.set(section, "pushoverapi", autosub.PUSHOVERAPI)
    cfg.set(section, "notifyboxcar2", str(autosub.NOTIFYBOXCAR2))
    cfg.set(section, "boxcar2token", autosub.BOXCAR2TOKEN)
    cfg.set(section, "notifyplex", str(autosub.NOTIFYPLEX))
    cfg.set(section, "plexserverhost", autosub.PLEXSERVERHOST)
    cfg.set(section, "plexserverport", autosub.PLEXSERVERPORT)
    
    with open(autosub.CONFIGFILE, 'wb') as cfile:
        cfg.write(cfile)

def checkForRestart():
    """
    Check if internal variables are different from the config file.
    Only check the variables the require a restart to take effect
    """
    #TODO: This function is very ugly and should be rewritten comletely. This is not a way to check it!
    cfg = SafeConfigParser()
    try:
        with codecs.open(autosub.CONFIGFILE, 'r', autosub.SYSENCODING) as f:
            cfg.readfp(f)
    except:
        #no config yet
        cfg = SafeConfigParser()
        pass

    # Set the default values
    schedulerchecksub = 86400
    loglevel = logging.INFO
    loglevelconsole = logging.ERROR
    logsize = 1000000
    lognum = 1
    webserverip = '0.0.0.0'
    webserverport = 8083
    webroot = ''
    username = ''
    password = ''

    # Check if an option excists in the config file, if so replace the default value
    if cfg.has_section('config'):
        if cfg.has_option('config', 'checksub'):
            schedulerchecksub = int(cfg.get('config', 'checksub'))

    if cfg.has_option("config", "logfile"):
        logfile = cfg.get("config", "logfile")

    if cfg.has_section('logfile'):
        if cfg.has_option("logfile", "loglevel"):
            loglevel = cfg.get("logfile", "loglevel")
            if loglevel.lower() == 'error':
                loglevel = logging.ERROR
            elif loglevel.lower() == "warning":
                loglevel = logging.WARNING
            elif loglevel.lower() == "debug":
                loglevel = logging.DEBUG
            elif loglevel.lower() == "info":
                loglevel = logging.INFO
            elif loglevel.lower() == "critical":
                loglevel = logging.CRITICAL

        if cfg.has_option("logfile", "loglevelconsole"):
            loglevelconsole = cfg.get("logfile", "loglevelconsole")
            if loglevelconsole.lower() == 'error':
                loglevelconsole = logging.ERROR
            elif loglevelconsole.lower() == "warning":
                loglevelconsole = logging.WARNING
            elif loglevelconsole.lower() == "debug":
                loglevelconsole = logging.DEBUG
            elif loglevelconsole.lower() == "info":
                loglevelconsole = logging.INFO
            elif loglevelconsole.lower() == "critical":
                loglevelconsole = logging.CRITICAL

        if cfg.has_option("logfile", "logsize"):
            logsize = int(cfg.get("logfile", "logsize"))

        if cfg.has_option("logfile", "lognum"):
            lognum = int(cfg.get("logfile", "lognum"))

    if cfg.has_section('webserver'):
        if cfg.has_option('webserver', 'webserverip') and cfg.has_option('webserver', 'webserverport'):
            webserverip = cfg.get('webserver', 'webserverip')
            webserverport = int(cfg.get('webserver', 'webserverport'))
        if cfg.has_option('webserver', 'webroot'):
            webroot = cfg.get('webserver', 'webroot')
        if cfg.has_option('webserver', 'username') and cfg.has_option('webserver', 'password'):
            username = cfg.get('webserver', 'username')
            password = cfg.get('webserver', 'password')

    # Now compare the values, if one differs a restart is required.
    if schedulerchecksub != autosub.SCHEDULERCHECKSUB or loglevel != autosub.LOGLEVEL or loglevelconsole != autosub.LOGLEVELCONSOLE or logsize != autosub.LOGSIZE or lognum != autosub.LOGNUM or webserverip != autosub.WEBSERVERIP or webserverport != autosub.WEBSERVERPORT or username != autosub.USERNAME or password != autosub.PASSWORD or webroot != autosub.WEBROOT:
        return True
    else:
        return False


def WriteConfig(configsection=None):
    """
    Save all settings to the config file.
    Return message about the write.
    """
    # Read config file
    cfg = SafeConfigParser()
    
    try:
        # A config file is set so we use this to add the settings
        with codecs.open(autosub.CONFIGFILE, 'r', autosub.SYSENCODING) as f:
            cfg.readfp(f)
    except:
        # No config file so we create one in autosub.PATH
        if not autosub.CONFIGFILE:
            autosub.CONFIGFILE = "config.properties"
        open(autosub.CONFIGFILE, 'w').close() 
        with codecs.open(autosub.CONFIGFILE, 'r', autosub.SYSENCODING) as f:
            cfg.readfp(f)

    # Before we save everything to the config file we need to test if
    # the app needs to be restarted for all changes to take effect, like
    # logfile and webserver sections
    restart = checkForRestart()
    
    if configsection == "notifications":
        saveNotifySection()
    else:
        saveConfigSection()
        saveLogfileSection()
        saveWebserverSection()
        saveSkipshowSection()
        saveUsernamemappingSection()
        saveUserAddic7edmappingSection()

    if restart:
        # This needs to be replaced by a restart thingy, until then, just re-read the config and tell the users to do a manual restart
        ReadConfig(autosub.CONFIGFILE)
        return "Configuration has been saved.<br> A manual restart is needed for all changes to take effect."
    else:
        # For some reason the needs to be read again, otherwise all pages get an error
        ReadConfig(autosub.CONFIGFILE)
        return "Configuration has been saved."

def upgradeConfig(from_version, to_version):
    print "Config: Upgrading config version from %d to %d" %(from_version, to_version)
    upgrades = to_version - from_version
    if upgrades != 1:
        print "Config: More than 1 upgrade required. Starting subupgrades"
        for x in range (0, upgrades):
            upgradeConfig(from_version + x, from_version + x + 1)
    else:
        if from_version == 1 and to_version == 2:
            print "Config: Upgrading minmatchscores"
            print "Config: Old value's Minmatchscore: %d" %(autosub.MINMATCHSCORE)
            
            if (autosub.MINMATCHSCORE % 2) == 0:
                autosub.MINMATCHSCORE = (autosub.MINMATCHSCORE * 2) + 2
            else:
                autosub.MINMATCHSCORE = (autosub.MINMATCHSCORE * 2) + 1
           
            print "Config: New value's Minmatchscore: %d" %(autosub.MINMATCHSCORE)
            print "Config: Config upgraded to version 2"
            autosub.CONFIGVERSION = 2
            autosub.CONFIGUPGRADED = True
        elif from_version == 2 and to_version == 3:
            for title in autosub.SKIPSHOWUPPER:
                items = autosub.SKIPSHOWUPPER[title]
                items = ['-1' if x=='0' else x for x in items]
                items = ['0' if x=='00' else x for x in items]
                string_items = ','.join(items)
                SaveToConfig('skipshow', title, string_items)
                applyskipShow()
            autosub.CONFIGVERSION = 3
            autosub.CONFIGUPGRADED = True

