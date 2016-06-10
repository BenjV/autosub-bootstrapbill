import Config
import logging.handlers
import time,os
from autosub.version import autosubversion


BOOTSTRAPVERSION='3.3.5'
ROOTPATH = None
BROWSERREFRESH = int(1)
REFRESHSTRING = None
FALLBACKTOENG = None
DOWNLOADENG = None
DOWNLOADDUTCH = None
SUBENG = u"en"
LOGFILE = None
SUBNL = u""
SKIPHIDDENDIRS = True
NOTIFYNL = None
NOTIFYEN = None
LOGLEVEL = None
LOGLEVELCONSOLE = None
LOGSIZE = int(1048576)
LOGNUM = int(1)
SKIPSHOW = None
SKIPSHOWUPPER = None
USERNAMEMAPPING = None
USERNAMEMAPPINGUPPER = None
USERADDIC7EDMAPPING = None
USERADDIC7EDMAPPINGUPPER = None
NAMEMAPPING = None
NAMEMAPPINGUPPER = None
SHOWID_CACHE = None
POSTPROCESSCMD = None
CONFIGFILE = None
PATH = None
MINMATCHSCORE = int(8)
CONFIGVERSION = None
WANTEDFIRST = None
ENGLISHSUBDELETE = None
PODNAPISI = None
SUBSCENE = None
OPENSUBTITLES = None
ADDIC7ED = None
ADDIC7EDUSER = None
ADDIC7EDPASSWD = None
ADDIC7EDLOGGED_IN = False

OPENSUBTITLESUSER = None
OPENSUBTITLESPASSWD = None
OPENSUBTITLESAPI = None
OPENSUBTITLESURL = None
OPENSUBTITLESTOKEN = None

OPENSUBTITLESTIME = float(0)

ADDIC7EDAPI = None
WANTEDQUEUE = []
LASTESTDOWNLOAD = None

APIKEY = None
API = None
IMDBAPI = None

APICALLSLASTRESET_TVDB = None
APICALLSLASTRESET_SUBSEEKER = None
APICALLSRESETINT_TVDB = None
APICALLSRESETINT_SUBSEEKER = None
APICALLSMAX_TVDB = None
APICALLSMAX_SUBSEEKER = None
APICALLS_TVDB = None
APICALLS_SUBSEEKER = None

TIMEOUT = 300
DOWNLOADS_A7 = int(0)
DOWNLOADS_A7MAX = int(40)

SEARCHINTERVAL = None
SEARCHTIME= float(0)
SCANDISK = None
CHECKSUB = None
DOWNLOADSUBS = None
SUBCODEC = u'windows-1252'

WEBSERVERIP = None
WEBSERVERPORT = None
LAUNCHBROWSER=True
USERNAME = None
PASSWORD = None
WEBROOT = None

NOTIFYMAIL = None
MAILSRV = None
MAILFROMADDR = None
MAILTOADDR = None
MAILUSERNAME = None
MAILPASSWORD = None
MAILSUBJECT = None
MAILAUTH = None
MAILENCRYPTION = None
NOTIFYGROWL = None
GROWLHOST = None
GROWLPORT = None
GROWLPASS = None
NOTIFYTWITTER = None
TWITTERKEY = None
TWITTERSECRET = None
NOTIFYNMA = None
NMAAPI = None
NOTIFYPROWL = None
PROWLAPI = None
PROWLPRIORITY = None
PUSHALOTAPI = None
NOTIFYPUSHALOT = None
PUSHBULLETAPI = None
NOTIFYPUSHBULLET = None
NOTIFYPUSHOVER = None
PUSHOVERAPPKEY = None
PUSHOVERUSERKEY = None
NMAPRIORITY = None
NOTIFYBOXCAR2 = None
BOXCAR2TOKEN = None
NOTIFYPLEX = None
PLEXSERVERHOST = None
PLEXSERVERPORT = None

DAEMON = None

DBFILE = None
DBVERSION = None
DBCONNECTION = None
DBIDCACHE = None

VERSIONURL = None
USERAGENT = None

SYSENCODING = None
MOBILEUSERAGENTS = None
MOBILEAUTOSUB = True

ENGLISH = None
DUTCH = None
UPDATED = False
SKIPSTRINGNL= u''
SKIPSTRINGEN= u''
NODE_ID = None
VERSION = int(0)
HI = False
OPENSUBTITLESSERVER = None
OPENSUBTITLESTOKEN  = None
ENGLISH = 'English'
DUTCH = 'Dutch'
CERTIFICATEPATH=u""
MOBILEUSERAGENTS = ["midp", "240x320", "blackberry", "netfront", "nokia", "panasonic", 
                    "portalmmm", "sharp", "sie-", "sonyericsson", "symbian", "windows ce", 
                    "benq", "mda", "mot-", "opera mini", "philips", "pocket pc", "sagem",
                    "samsung", "sda", "sgh-", "vodafone", "xda", "palm", "iphone", "ipod", 
                    "ipad", "android", "windows phone"]
DBFILE = 'database.db'

def Initialize():
    global ROOTPATH,LOGFILE, LOGLEVEL, LOGLEVELCONSOLE, LOGSIZE, LOGNUM,  \
    CONFIGFILE, CERTIFICATEPATH, ZIPURL, APIKEY, API, IMDBAPI,  \
    APICALLSLASTRESET_TVDB, APICALLSLASTRESET_SUBSEEKER, APICALLSRESETINT_TVDB, APICALLSRESETINT_SUBSEEKER, \
    APICALLSMAX_TVDB, APICALLSMAX_SUBSEEKER, APICALLS_TVDB, APICALLS_SUBSEEKER, \
    SEARCHINTERVAL, SCHEDULERDOWNLOADSUBS, \
    USERAGENT, VERSION, VERSIONURL, TVDBURL, \
    OPENSUBTITLESURL, OPENSUBTITLESUSERAGENT

    if 'Alpha' in autosubversion:
        release = autosubversion.split(' ')[0]
        versionnumber = autosubversion.split(' ')[1]
    else:
        versionnumber = autosubversion

    VERSION = int(versionnumber.split('.')[0]) * 1000 + int(versionnumber.split('.')[1]) * 100 + int(versionnumber.split('.')[2]) * 10
    VERSIONURL = u'https://raw.githubusercontent.com/BenjV/autosub-bootstrapbill/master/autosub/version.py'
    ZIPURL =  u'https://github.com/BenjV/autosub-bootstrapbill/archive/master.zip'
    USERAGENT = u'AutoSub/' + versionnumber
    OPENSUBTITLESUSERAGENT = u'PYAutosub V' + versionnumber

    APIKEY = "24430affe80bea1edf0e8413c3abf372a64afff2"
    TIMEOUT = 300 #default http timeout
    
    if CONFIGFILE == None:
        CONFIGFILE = "config.properties"
    
    Config.ReadConfig(CONFIGFILE)
    CERTIFICATEPATH = os.path.normpath(PATH +'/library/requests/cacert.pem')
    API = "http://api.subtitleseeker.com/get/title_subtitles/?api_key=%s" %APIKEY
    IMDBAPI = "http://thetvdb.com/api/"
    OPENSUBTITLESURL = 'http://api.opensubtitles.org/xml-rpc'

    
    APICALLSLASTRESET_TVDB = time.time()
    APICALLSLASTRESET_SUBSEEKER = time.time()
    
    APICALLSRESETINT_TVDB = 86400
    APICALLSRESETINT_SUBSEEKER = 86400
    
    APICALLSMAX_TVDB = 2500
    APICALLSMAX_SUBSEEKER = 1000
    
    APICALLS_TVDB = APICALLSMAX_TVDB
    APICALLS_SUBSEEKER = APICALLSMAX_SUBSEEKER      

    #Set the language paramater for the API query

    

def initLogging(logfile):
    global LOGLEVEL, LOGSIZE, LOGNUM, LOGLEVELCONSOLE, \
    DAEMON
    
    # initialize logging
    # A log directory has to be created below the start directory
    log = logging.getLogger("thelogger")
    log.setLevel(LOGLEVEL)

    log_script = logging.handlers.RotatingFileHandler(logfile, 'a', LOGSIZE, LOGNUM)
    log_script_formatter=logging.Formatter('%(asctime)s %(levelname)s  %(message)s')
    log_script.setFormatter(log_script_formatter)
    log_script.setLevel(LOGLEVEL)
    log.addHandler(log_script)
    
    #CONSOLE log handler
    if DAEMON!=True:
        console = logging.StreamHandler()
        console.setLevel(LOGLEVELCONSOLE)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(asctime)s %(levelname)s  %(message)s')
        console.setFormatter(formatter)
        log.addHandler(console)
        
    return log