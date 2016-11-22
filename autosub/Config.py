# coding: latin-1

# Autosub Config.py
#
# The Autosub config Module
#

# python 2.5 support

from __future__ import with_statement

import os,re
import logging
import codecs

from ConfigParser import SafeConfigParser

import autosub
import autosub.version as version
import autosub.ID_lookup

# Autosub specific modules

# Settings -----------------------------------------------------------------------------------------------------------------------------------------
# Location of the configuration file:
# configfile = "config.properties"
# Set the logger
log = logging.getLogger('thelogger')
#/Settings -----------------------------------------------------------------------------------------------------------------------------------------


def ReadConfig():
    """
    Read the config file and set all the variables.
    """

    # Read config file
    cfg = SafeConfigParser()
    cfg.optionxform = lambda option: option

    try:
        with codecs.open(autosub.CONFIGFILE, 'r', autosub.SYSENCODING) as f:
            cfg.readfp(f)
    except:
        #No config found so we create a default config
        Message = WriteConfig()
        return

    # First we check whether the config has been upgraded
    if autosub.CONFIGVERSION < version.configversion:
        upgradeConfig(cfg, autosub.CONFIGVERSION, version.configversion)
    elif autosub.CONFIGVERSION > version.configversion:
        print "Config: ERROR! Config version higher then this version of AutoSub supports. Update AutoSub!"
        os._exit(1)

    section = 'config'
    if not cfg.has_section(section):  cfg.add_section(section)
    if cfg.has_option(section, "configversion"):        autosub.CONFIGVERSION       = cfg.getint("config", "configversion") 
    if cfg.has_option(section, "wantedfirst"):          autosub.WANTEDFIRST         = cfg.getboolean(section, "wantedfirst")
    if cfg.has_option(section, 'downloaddutch'):        autosub.DOWNLOADDUTCH       = cfg.getboolean(section, 'downloaddutch')
    if cfg.has_option(section, 'downloadeng'):          autosub.DOWNLOADENG         = cfg.getboolean(section, 'downloadeng')
    if cfg.has_option(section, "fallbacktoeng"):        autosub.FALLBACKTOENG       = cfg.getboolean(section, "fallbacktoeng")
    if cfg.has_option(section, "notifyen"):             autosub.NOTIFYEN            = cfg.getboolean(section, "notifyen")
    if cfg.has_option(section, "notifynl"):             autosub.NOTIFYNL            = cfg.getboolean(section, "notifynl")
    if cfg.has_option(section, "launchbrowser"):        autosub.LAUNCHBROWSER       = cfg.getboolean(section, "launchbrowser")
    if cfg.has_option(section, "skiphiddendirs"):       autosub.SKIPHIDDENDIRS      = cfg.getboolean(section, "skiphiddendirs")
    if cfg.has_option(section, "englishsubdelete"):     autosub.ENGLISHSUBDELETE    = cfg.getboolean(section, "englishsubdelete")
    if cfg.has_option(section, "podnapisi"):            autosub.PODNAPISI           = cfg.getboolean(section, "podnapisi")
    if cfg.has_option(section, "subscene"):             autosub.SUBSCENE            = cfg.getboolean(section, "subscene")
    if cfg.has_option(section, "addic7ed"):             autosub.ADDIC7ED            = cfg.getboolean(section, "addic7ed")
    if cfg.has_option(section, "opensubtitles"):        autosub.OPENSUBTITLES       = cfg.getboolean(section, "opensubtitles")
    if cfg.has_option(section, "hearingimpaired"):      autosub.HI                  = cfg.getboolean(section, "hearingimpaired")
    if cfg.has_option(section, 'minmatchscore'):        autosub.MINMATCHSCORE       = cfg.getint(section, 'minmatchscore')
    if cfg.has_option(section, 'searchinterval'):       autosub.SEARCHINTERVAL      = cfg.getint(section, 'searchinterval')
    if cfg.has_option(section, "browserrefresh"):       autosub.BROWSERREFRESH      = cfg.getint(section, "browserrefresh")
    if cfg.has_option(section, "path"):                 autosub.PATH                = cfg.get(section, "path")
    if cfg.has_option(section, "rootpath"):             autosub.SERIESPATH          = cfg.get(section, "rootpath")
    if cfg.has_option(section, "seriespath"):           autosub.SERIESPATH          = cfg.get(section, "seriespath")
    if cfg.has_option(section, "subeng"):               autosub.SUBENG              = cfg.get(section, "subeng")
    if cfg.has_option(section, "subnl"):                autosub.SUBNL               = cfg.get(section, "subnl")
    if cfg.has_option(section, "postprocesscmd"):       autosub.POSTPROCESSCMD      = cfg.get(section, "postprocesscmd")
    if cfg.has_option(section, "opensubtitlesuser"):    autosub.OPENSUBTITLESUSER   = cfg.get(section, "opensubtitlesuser")
    if cfg.has_option(section, "opensubtitlespasswd"):  autosub.OPENSUBTITLESPASSWD = cfg.get(section, "opensubtitlespasswd") 
    if cfg.has_option(section, "addic7eduser"):         autosub.ADDIC7EDUSER        = cfg.get(section, "addic7eduser")
    if cfg.has_option(section, "addic7edpasswd"):       autosub.ADDIC7EDPASSWD      = cfg.get(section, "addic7edpasswd") 
    if cfg.has_option(section, "logfile"):              autosub.LOGFILE             = cfg.get(section, "logfile")
    if cfg.has_option(section, "subcodec"):             autosub.SUBCODEC            = cfg.get(section, "subcodec")
    if cfg.has_option(section, "skipstringnl"):         autosub.SKIPSTRINGNL        = cfg.get(section, "skipstringnl")
    if cfg.has_option(section, "skipstringen"):         autosub.SKIPSTRINGEN        = cfg.get(section, "skipstringen")
    if cfg.has_option(section, "skipfoldersnl"):        autosub.SKIPFOLDERSNL       = cfg.get(section, "skipfoldersnl")
    if cfg.has_option(section, "skipfoldersen"):        autosub.SKIPFOLDERSEN       = cfg.get(section, "skipfoldersen")



    # *******************
    # * Logfile Section *
    # *******************
    section = 'logfile'
    if not cfg.has_section(section): cfg.add_section(section)
    if cfg.has_option(section, "logfile"): autosub.LOGFILE = cfg.get(section, "logfile")
    if cfg.has_option(section, "loglevel"):
        LogLevel = cfg.get(section, "loglevel").upper()
        if LogLevel == u'ERROR':
            autosub.LOGLEVEL = logging.ERROR
        elif LogLevel == u"WARNING":
            autosub.LOGLEVEL = logging.WARNING
        elif LogLevel == u"DEBUG":
            autosub.LOGLEVEL = logging.DEBUG
        elif LogLevel == u"INFO":
            autosub.LOGLEVEL = logging.INFO
        elif LogLevel == u"CRITICAL":
            autosub.LOGLEVEL = logging.CRITICAL

    if cfg.has_option(section, "loglevelconsole"):
        LogLevel = cfg.get(section, "loglevelconsole").upper()
        if LogLevel == u'ERROR':
            autosub.LOGLEVELCONSOLE = logging.ERROR
        elif LogLevel == u"WARNING":
            autosub.LOGLEVELCONSOLE = logging.WARNING
        elif LogLevel == u"DEBUG":
            autosub.LOGLEVELCONSOLE = logging.DEBUG
        elif LogLevel == u"INFO":
            autosub.LOGLEVELCONSOLE = logging.INFO
        elif LogLevel == u"CRITICAL":
            autosub.LOGLEVELCONSOLE = logging.CRITICAL

    if cfg.has_option(section, "logsize"): autosub.LOGSIZE = cfg.getint(section, "logsize")
    if cfg.has_option(section, "lognum"):  autosub.LOGNUM  = cfg.getint(section, "lognum")

    # ******************************
    # * Cherrypy Webserver Section *
    # ******************************
    section = 'webserver'
    if not cfg.has_section(section): cfg.add_section(section)

    if cfg.has_option(section, 'webserverip'):   autosub.WEBSERVERIP   = cfg.get(section, 'webserverip')
    if cfg.has_option(section, 'webserverport'): autosub.WEBSERVERPORT = int(cfg.get(section, 'webserverport'))
    if cfg.has_option(section, 'webroot'):       autosub.WEBROOT       = cfg.get(section, 'webroot')
    if cfg.has_option(section, 'username'):      autosub.USERNAME      = cfg.get(section, 'username')
    if cfg.has_option(section, 'password'):      autosub.PASSWORD      = cfg.get(section, 'password')

    # ********************
    # * SkipShow Section *
    # ********************
    section = 'skipshow'
    if not cfg.has_section(section): cfg.add_section(section)

    autosub.SKIPSHOWUPPER = {}
    autosub.SKIPSHOW      = {}
    SkipShows = dict(cfg.items(section))
        #autosub.SKIPSHOW = dict(cfg.items('skipshow'))
        # The following 5 lines convert the skipshow to uppercase. And also convert the variables to a list
        # also replace the "~" with ":" neccesary because the config parser sees ":" as a delimiter
        # The UPPER version is for searching, the normal for dispaly in the user interface
    for show in SkipShows:
        if re.match("^[0-9 ,.-]+$", SkipShows[show]):
            autosub.SKIPSHOW[show.replace('~',':')] = SkipShows[show]
            autosub.SKIPSHOWUPPER[show.upper().replace('~',':')] = [Item.strip() for Item in SkipShows[show].split(',')]


    # ********************************
    # * Addic7ed Namemapping Section *
    # ********************************
    section = 'addic7edmapping'
    if not cfg.has_section(section): cfg.add_section(section)
    autosub.USERADDIC7EDMAPPING={}
    try:
        autosub.USERADDIC7EDMAPPING = dict(cfg.items(section))
    except:
        pass
    for ImdbId in autosub.USERADDIC7EDMAPPING.iterkeys():
        if not (ImdbId.isdigit and autosub.USERADDIC7EDMAPPING[ImdbId].isdigit()):
            del autosub.USERADDIC7EDMAPPING[ImdbId]
            print'ReadConfig: Addic7ed mapping has an unkown format.',ImdbId,' = ', autosub.USERADDIC7EDMAPPING[ImdbId]

    # Settings

    

    # ****************************
    # * User Namemapping Section *
    # ****************************
    section = 'namemapping'
    if not cfg.has_section(section): cfg.add_section(section)
    NameMapping = dict(cfg.items(section))
    autosub.USERNAMEMAPPING={}
    for ConfigName in NameMapping.iterkeys():
        if NameMapping[ConfigName].isdigit():
            Name = ConfigName.replace('~',':')
            if not Name.upper() in autosub.NAMEMAPPING.keys():
                autosub.NAMEMAPPING[Name.upper()]  = [NameMapping[ConfigName].strip(),u'']
            autosub.USERNAMEMAPPING[Name] = NameMapping[ConfigName].strip()
        else:
            print 'ReadConfig: Username mapping has an unknown format.',ConfigName,' = ',NameMapping[ConfigName] 
   
    # ******************
    # * Notify Section *
    # ******************
    section = 'notify'
    if not cfg.has_section(section): cfg.add_section(section)

    if cfg.has_option(section, 'notifymail'): autosub.NOTIFYMAIL                    = cfg.getboolean(section, 'notifymail')
    if cfg.has_option(section, 'mailsrv'): autosub.MAILSRV                          = cfg.get(section, 'mailsrv')
    if cfg.has_option(section, 'mailfromaddr'): autosub.MAILFROMADDR                = cfg.get(section, 'mailfromaddr')
    if cfg.has_option(section, 'mailtoaddr'): autosub.MAILTOADDR                    = cfg.get(section, 'mailtoaddr')
    if cfg.has_option(section, 'mailusername'): autosub.MAILUSERNAME                = cfg.get(section, 'mailusername')
    if cfg.has_option(section, 'mailpassword'): autosub.MAILPASSWORD                = cfg.get(section, 'mailpassword')
    if cfg.has_option(section, 'mailsubject'): autosub.MAILSUBJECT                  = cfg.get(section, 'mailsubject')
    if cfg.has_option(section, 'mailencryption'): autosub.MAILENCRYPTION            = cfg.get(section, 'mailencryption')
    if cfg.has_option(section, 'mailauth'): autosub.MAILAUTH                        = cfg.get(section, 'mailauth')
    if cfg.has_option(section, 'notifygrowl'): autosub.NOTIFYGROWL                  = cfg.getboolean(section, 'notifygrowl')
    if cfg.has_option(section, 'growlhost'): autosub.GROWLHOST                      = cfg.get(section, 'growlhost')
    if cfg.has_option(section, 'growlport'): autosub.GROWLPORT                      = cfg.get(section, 'growlport')
    if cfg.has_option(section, 'growlpass'): autosub.GROWLPASS                      = cfg.get(section, 'growlpass')
    if cfg.has_option(section, 'notifytwitter'): autosub.NOTIFYTWITTER              = cfg.getboolean(section, 'notifytwitter')
    if cfg.has_option(section, 'twitterkey'): autosub.TWITTERKEY                    = cfg.get(section, 'twitterkey')
    if cfg.has_option(section, 'twittersecret'): autosub.TWITTERSECRET              = cfg.get(section, 'twittersecret')
    if cfg.has_option(section, 'notifynma'): autosub.NOTIFYNMA                      = cfg.getboolean(section, 'notifynma')
    if cfg.has_option(section, 'nmaapi'): autosub.NMAAPI                            = cfg.get(section, 'nmaapi')
    if cfg.has_option(section, 'nmapriority'): autosub.NMAPRIORITY                  = cfg.getint(section, 'nmapriority')
    if cfg.has_option(section, 'notifyprowl'): autosub.NOTIFYPROWL                  = cfg.getboolean(section, 'notifyprowl')
    if cfg.has_option(section, 'prowlapi'): autosub.PROWLAPI                        = cfg.get(section, 'prowlapi')
    if cfg.has_option(section, 'prowlpriority'): autosub.PROWLPRIORITY              = cfg.getint(section, 'prowlpriority')
    if cfg.has_option(section, 'notifytelegram'): autosub.NOTIFYTELEGRAM            = cfg.getboolean(section, 'notifytelegram')
    if cfg.has_option(section, 'telegramapi'): autosub.TELEGRAMAPI                  = cfg.get(section, 'telegramapi')
    if cfg.has_option(section, 'telegramid'): autosub.TELEGRAMID                    = cfg.get(section, 'telegramid')
    if cfg.has_option(section, 'notifypushalot'): autosub.NOTIFYPUSHALOT            = cfg.getboolean(section, 'notifypushalot')
    if cfg.has_option(section, 'pushalotapi'): autosub.PUSHALOTAPI                  = cfg.get(section, 'pushalotapi')
    if cfg.has_option(section, 'notifypushbullet'): autosub.NOTIFYPUSHBULLET        = cfg.getboolean(section, 'notifypushbullet')
    if cfg.has_option(section, 'pushbulletapi'): autosub.PUSHBULLETAPI              = cfg.get(section, 'pushbulletapi')
    if cfg.has_option(section, 'notifypushover'): autosub.NOTIFYPUSHOVER            = cfg.getboolean(section, 'notifypushover')
    if cfg.has_option(section, 'pushoverappkey'): autosub.PUSHOVERAPPKEY            = cfg.get(section, 'pushoverappkey')
    if cfg.has_option(section, 'pushoveruserkey'): autosub.PUSHOVERUSERKEY          = cfg.get(section, 'pushoveruserkey')
    if cfg.has_option(section, 'notifyboxcar2'): autosub.NOTIFYBOXCAR2              = cfg.getboolean(section, 'notifyboxcar2')
    if cfg.has_option(section, 'boxcar2token'): autosub.BOXCAR2TOKEN                = cfg.get(section, 'boxcar2token')
    if cfg.has_option(section, 'notifyplex'): autosub.NOTIFYPLEX                    = cfg.getboolean(section, 'notifyplex')
    if cfg.has_option(section, 'plexserverhost'): autosub.PLEXSERVERHOST            = cfg.get(section, 'plexserverhost')
    if cfg.has_option(section, 'plexserverport'): autosub.PLEXSERVERPORT            = cfg.get(section, 'plexserverport')
    if cfg.has_option(section, 'plexserverusername'): autosub.PLEXSERVERUSERNAME    = cfg.get(section, 'plexserverusername')
    if cfg.has_option(section, 'plexserverpassword'): autosub.PLEXSERVERPASSWORD    = cfg.get(section, 'plexserverpassword')


def WriteConfig():
    cfg = SafeConfigParser()
    cfg.optionxform = lambda option: option

    section = 'config'
    cfg.add_section(section)
    cfg.set(section, "path", autosub.PATH )
    cfg.set(section, "seriespath", autosub.SERIESPATH) 
    cfg.set(section, 'downloaddutch', str(autosub.DOWNLOADDUTCH))
    cfg.set(section, 'downloadeng', str(autosub.DOWNLOADENG))
    cfg.set(section, "subeng", autosub.SUBENG)
    cfg.set(section, "subnl", autosub.SUBNL)
    cfg.set(section, "fallbacktoeng", str(autosub.FALLBACKTOENG))
    cfg.set(section, "notifyen", str(autosub.NOTIFYEN))
    cfg.set(section, "notifynl", str(autosub.NOTIFYNL))
    cfg.set(section, "wantedfirst", str(autosub.WANTEDFIRST))
    cfg.set(section, "launchbrowser", str(autosub.LAUNCHBROWSER))
    cfg.set(section, "skiphiddendirs", str(autosub.SKIPHIDDENDIRS))
    cfg.set(section, "englishsubdelete", str(autosub.ENGLISHSUBDELETE))
    cfg.set(section, "addic7ed", str(autosub.ADDIC7ED))
    cfg.set(section, "opensubtitles", str(autosub.OPENSUBTITLES))
    cfg.set(section, "podnapisi", str(autosub.PODNAPISI))
    cfg.set(section, "subscene", str(autosub.SUBSCENE))
    cfg.set(section, "hearingimpaired", str(autosub.HI))
    cfg.set(section, 'minmatchscore', str(autosub.MINMATCHSCORE))
    cfg.set(section, "configversion", str(autosub.CONFIGVERSION ))  
    cfg.set(section, 'searchinterval', str(autosub.SEARCHINTERVAL))
    cfg.set(section, "browserrefresh", str(autosub.BROWSERREFRESH))
    cfg.set(section, "postprocesscmd", autosub.POSTPROCESSCMD)
    cfg.set(section, "opensubtitlesuser", autosub.OPENSUBTITLESUSER)
    cfg.set(section, "opensubtitlespasswd", autosub.OPENSUBTITLESPASSWD)
    cfg.set(section, "addic7eduser", autosub.ADDIC7EDUSER)
    cfg.set(section, "addic7edpasswd", autosub.ADDIC7EDPASSWD)
    cfg.set(section, "subcodec", autosub.SUBCODEC)
    cfg.set(section, "skipstringnl", autosub.SKIPSTRINGNL)
    cfg.set(section, "skipstringen", autosub.SKIPSTRINGEN)
    cfg.set(section, "skipfoldersnl", autosub.SKIPFOLDERSNL)
    cfg.set(section, "skipfoldersen", autosub.SKIPFOLDERSEN)

    section = 'webserver'
    cfg.add_section(section)
    cfg.set(section, "webserverip", str(autosub.WEBSERVERIP))
    cfg.set(section, 'webserverport', str(autosub.WEBSERVERPORT))
    cfg.set(section, "username", autosub.USERNAME)
    cfg.set(section, "password", autosub.PASSWORD)
    cfg.set(section, "webroot", autosub.WEBROOT)

    section = 'logfile'
    cfg.add_section(section)
    cfg.set(section, "logfile", autosub.LOGFILE)
    cfg.set(section, "loglevel", logging.getLevelName(autosub.LOGLEVEL))
    cfg.set(section, "loglevelconsole", logging.getLevelName(autosub.LOGLEVELCONSOLE))
    cfg.set(section, "logsize", str(autosub.LOGSIZE))
    cfg.set(section, "lognum", str(autosub.LOGNUM))


    section = 'notify'
    cfg.add_section(section)
    if autosub.NOTIFYMAIL:
        cfg.set(section, "notifymail", str(autosub.NOTIFYMAIL))
        cfg.set(section, "mailsrv", autosub.MAILSRV)
        cfg.set(section, 'mailfromaddr', autosub.MAILFROMADDR)
        cfg.set(section, "mailtoaddr", autosub.MAILTOADDR)
        cfg.set(section, "mailusername", autosub.MAILUSERNAME)
        cfg.set(section, "mailpassword", autosub.MAILPASSWORD)
        cfg.set(section, "mailsubject", autosub.MAILSUBJECT)
        cfg.set(section, "mailencryption", autosub.MAILENCRYPTION)
        cfg.set(section, "mailauth", autosub.MAILAUTH)
    if autosub.NOTIFYGROWL:
        cfg.set(section, "notifygrowl", str(autosub.NOTIFYGROWL))
        cfg.set(section, "growlhost", autosub.GROWLHOST)
        cfg.set(section, "growlport", autosub.GROWLPORT)
        cfg.set(section, "growlpass", autosub.GROWLPASS)
    if autosub.NOTIFYNMA:
        cfg.set(section, "notifynma", str(autosub.NOTIFYNMA))
        cfg.set(section, "nmaapi", autosub.NMAAPI)
        cfg.set(section, "nmapriority", str(autosub.NMAPRIORITY))
    if autosub.NOTIFYTWITTER:
        cfg.set(section, "notifytwitter", str(autosub.NOTIFYTWITTER))
        cfg.set(section, "twitterkey", autosub.TWITTERKEY)
        cfg.set(section, "twittersecret", autosub.TWITTERSECRET)
    if autosub.NOTIFYPROWL:
        cfg.set(section, "notifyprowl", str(autosub.NOTIFYPROWL))
        cfg.set(section, "prowlapi", autosub.PROWLAPI)
        cfg.set(section, "prowlpriority", str(autosub.PROWLPRIORITY))
    if autosub.NOTIFYTELEGRAM:
        cfg.set(section, "notifytelegram", str(autosub.NOTIFYTELEGRAM))
        cfg.set(section, "telegramapi", autosub.TELEGRAMAPI)
        cfg.set(section, "telegramid", autosub.TELEGRAMID)
    if autosub.NOTIFYPUSHALOT:
        cfg.set(section, "notifypushalot", str(autosub.NOTIFYPUSHALOT))
        cfg.set(section, "pushalotapi", autosub.PUSHALOTAPI)
    if autosub.NOTIFYPUSHBULLET:
        cfg.set(section, "notifypushbullet", str(autosub.NOTIFYPUSHBULLET))
        cfg.set(section, "pushbulletapi", autosub.PUSHBULLETAPI)
    if autosub.NOTIFYPUSHOVER:
        cfg.set(section, "notifypushover", str(autosub.NOTIFYPUSHOVER))
        cfg.set(section, "pushoverappkey", autosub.PUSHOVERAPPKEY)
        cfg.set(section, "pushoveruserkey", autosub.PUSHOVERUSERKEY)
    if autosub.NOTIFYBOXCAR2:
        cfg.set(section, "notifyboxcar2", str(autosub.NOTIFYBOXCAR2))
        cfg.set(section, "boxcar2token", autosub.BOXCAR2TOKEN)
    if autosub.NOTIFYPLEX:
        cfg.set(section, "notifyplex", str(autosub.NOTIFYPLEX))
        cfg.set(section, "plexserverhost", autosub.PLEXSERVERHOST)
        cfg.set(section, "plexserverport", autosub.PLEXSERVERPORT)
        cfg.set(section, "plexserverusername", autosub.PLEXSERVERUSERNAME)
        cfg.set(section, "plexserverpassword", autosub.PLEXSERVERPASSWORD)

    section = 'skipshow'
    cfg.add_section(section)
    for Show in autosub.SKIPSHOW:
        if re.match("^[0-9 ,.-]+$", autosub.SKIPSHOW[Show]):
            cfg.set(section, Show.replace(':','~'), autosub.SKIPSHOW[Show])

    section = 'namemapping'
    cfg.add_section(section)
    for Name in autosub.USERNAMEMAPPING:
        cfg.set(section, Name.replace(':','~'), autosub.USERNAMEMAPPING[Name])

    section = 'addic7edmapping'
    cfg.add_section(section)
    for Name in autosub.USERADDIC7EDMAPPING:
        cfg.set(section, Name, autosub.USERADDIC7EDMAPPING[Name])

    try:
        with open(autosub.CONFIGFILE, 'wb') as cfile:
            cfg.write(cfile)
    except Exception as error:
        return error
    # here we read the config back because the the UPPERCASE variants of the config (for searching) has to be filled
    ReadConfig()
    return 'Config has been saved.'

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


def upgradeConfig(cfg, from_version, to_version):
    print "Config: Upgrading config version from %d to %d" %(from_version, to_version)
    upgrades = to_version - from_version
    if upgrades != 1:
        print "Config: More than 1 upgrade required. Starting subupgrades"
        for x in range (0, upgrades):
            upgradeConfig(cfg, from_version + x, from_version + x + 1)
    else:
        if from_version == 1 and to_version == 2:
            print "Config: Upgrading minmatchscores"
            print "Config: Old value's Minmatchscore: %d" %(autosub.MINMATCHSCORE)
            
            if (autosub.MINMATCHSCORE % 2) == 0:
                autosub.MINMATCHSCORE = (autosub.MINMATCHSCORE * 2) + 2
            else:
                autosub.MINMATCHSCORE = (autosub.MINMATCHSCORE * 2) + 1
            autosub.CONFIGVERSION = 2
            WriteConfig()
            print "Config: Config upgraded to version 2"
        elif from_version == 2 and to_version == 3:
            for title in autosub.SKIPSHOWUPPER:
                items = autosub.SKIPSHOWUPPER[title]
                items = ['-1' if x=='0' else x for x in items]
                items = ['0' if x=='00' else x for x in items]
                string_items = ','.join(items)
            autosub.CONFIGVERSION = 3
            WriteConfig()
            print "Config: Config upgraded to version 3"
        elif from_version == 3 and to_version == 4:
            if cfg.has_option('config', 'checksub'): autosub.SEARCHINTERVAL = cfg.getint('config', 'checksub')
            if cfg.has_option('config','homelayoutfirst'):
                if cfg.get("config", "homelayoutfirst") != "Wanted": autosub.WANTEDFIRST = False
            if cfg.has_option('config', 'podnapisilang'):
                if cfg.get("config", "podnapisilang") != 'None':     autosub.PODNAPISI = True
            if cfg.has_option('config', 'subscenelang'):
                if cfg.get("config", "subscenelang") != 'None' :     autosub.SUBSCENE = True
            if cfg.has_option('config', 'opensubtitleslang'):
                if cfg.get("config", "opensubtitleslang") != 'None': autosub.OPENSUBTITLES = True
            if cfg.has_option('config', 'addic7edlang'):
                if cfg.get("config", "addic7edlang") != 'None':      autosub.ADDIC7ED = True
                cfg.remove_option('config','addic7edlang')
            if cfg.has_option("config", "webdl"):
                Webdl = cfg.get("config", "webdl")
                if Webdl == u"DutchOnly":
                    autosub.SKIPSTRINGEN = "Web-dl"
                elif Webdl == "None":
                    autosub.SKIPSTRINGNL = autosub.SKIPSTRINGEN = u"Web-dl"
            autosub.CONFIGVERSION = 4
            WriteConfig()
            print "Config: Config upgraded to version 4"
