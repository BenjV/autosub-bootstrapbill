#
# Autosub Webserver.py - https://github.com/Donny87/autosub-bootstrapbill
#
# The Webserver module
#


import cherrypy
import logging
from ast import literal_eval

log = logging.getLogger('thelogger')

try:
    from Cheetah.Template import Template
except:
    print "ERROR!!! Cheetah is not installed yet. Download it from: http://pypi.python.org/pypi/Cheetah/2.4.4"

import threading
import time
import autosub.Config
from autosub.Db import lastDown, flushcache

import autosub.notify as notify

import autosub.Helpers

from autosub.Addic7ed import Addic7edAPI
from autosub.OpenSubtitles import OpenSubtitlesLogin

def redirect(abspath, *args, **KWs):
    assert abspath[0] == '/'
    raise cherrypy.HTTPRedirect(autosub.WEBROOT + abspath, *args, **KWs)


class PageTemplate (Template):
    #Placeholder for future, this object can be used to add stuff to the template
    pass

class Config:
    @cherrypy.expose
    def index(self):
        redirect("/config/settings")

    @cherrypy.expose
    def info(self):
        tmpl = PageTemplate(file="interface/templates/config-info.tmpl")
        return str(tmpl)  

    @cherrypy.expose
    def liveinfo(self):
        tmpl = PageTemplate(file="interface/templates/config-liveinfo.tmpl")
        return str(tmpl)  

    @cherrypy.expose
    def settings(self):
        tmpl = PageTemplate(file="interface/templates/config-settings.tmpl")
        return str(tmpl)  

    @cherrypy.expose
    def notifications(self):
        tmpl = PageTemplate(file="interface/templates/config-notification.tmpl")
        return str(tmpl)  

    @cherrypy.expose
    def skipShow(self, title, season=None, episode=None):
        episodestoskip = None
        if not season:
            tmpl = PageTemplate(file="interface/templates/config-skipshow.tmpl")
            tmpl.title = title
            return str(tmpl)
        else:
            season = int(season)
            tmpl = PageTemplate(file="interface/templates/home.tmpl")
            if not title:
                raise cherrypy.HTTPError(400, "No show supplied")
            if title.upper() in autosub.SKIPSHOWUPPER:
                for x in autosub.SKIPSHOWUPPER[title.upper()]:
                    x = literal_eval(x)
                    x_season = int(x)
                    x_episode = int(round((x-x_season) * 100))
                    if x == -1 or (x_season == season and (x_episode == 0 or (episode and x_episode == int(episode)))):
                        tmpl.message = "This show/season/episode is already being skipped"
                        tmpl.displaymessage = "Yes"
                        tmpl.modalheader = "Information"
                        return str(tmpl)
                if episode:
                    episodestoskip = str(season + float(episode)/100)
                else:
                    episodestoskip = str(season)
                episodestoskip = episodestoskip + ',' + ','.join(autosub.SKIPSHOWUPPER[title.upper()])
            else:
                if episode:
                    episodestoskip = str(season + float(episode)/100)
                else:
                    episodestoskip = str(season)

            autosub.Config.SaveToConfig('skipshow',title,episodestoskip)
            autosub.Config.applyskipShow()

            print season, episode

            if season == -1:
                tmpl.message = "<strong>%s</strong> will be skipped.<br> This will happen the next time that Auto-Sub checks for subtitles" % title.title()
            elif episode:
                tmpl.message = "<strong>%s</strong> season <strong>%s</strong> episode <strong>%s</strong> will be skipped.<br> This will happen the next time that Auto-Sub checks for subtitles" % (title.title(), season, episode)
            else:
                tmpl.message = "<strong>%s</strong> season <strong>%s</strong> will be skipped.<br> This will happen the next time that Auto-Sub checks for subtitles" % (title.title(), season)
            
            tmpl.displaymessage = "Yes"
            tmpl.modalheader = "Information"
            return str(tmpl)
    
    @cherrypy.expose
    def applyConfig(self):
        autosub.Config.applyAllSettings()
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        tmpl.message = "Settings read & applied"
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"
        return str(tmpl)

    @cherrypy.expose  
    def saveConfig(self, subeng, checksub, scandisk, skiphiddendirs, webdl, subnl, postprocesscmd, 
                   path, logfile, rootpath, launchbrowser, fallbacktoeng, downloadeng, englishsubdelete, username, 
                   password, webroot, skipshow, lognum, loglevelconsole, logsize, loglevel, 
                   webserverip, webserverport, usernamemapping, useraddic7edmapping, notifyen, notifynl, homelayoutfirst,
                   podnapisilang, subscenelang, undertexterlang, opensubtitleslang, opensubtitlesuser, opensubtitlespasswd,
                   addic7edlang, addic7eduser, addic7edpasswd, downloaddutch,
                   mmssource = None, mmsquality = None, mmscodec = None, mmsrelease = None):
                   
        # Set all internal variables
        autosub.PATH = path
        autosub.ROOTPATH = rootpath
        autosub.LOGFILE = logfile
        autosub.FALLBACKTOENG = fallbacktoeng
        autosub.DOWNLOADENG = downloadeng
        autosub.DOWNLOADDUTCH = downloaddutch
        autosub.SUBENG = subeng
        autosub.SUBNL = subnl
        autosub.NOTIFYEN = notifyen
        autosub.NOTIFYNL = notifynl
        autosub.POSTPROCESSCMD = postprocesscmd
        autosub.LAUNCHBROWSER = launchbrowser
        autosub.SKIPHIDDENDIRS = skiphiddendirs
        autosub.HOMELAYOUTFIRST = homelayoutfirst
        autosub.ENGLISHSUBDELETE = englishsubdelete
        autosub.PODNAPISILANG = podnapisilang
        autosub.SUBSCENELANG = subscenelang
        autosub.OPENSUBTITLESLANG = opensubtitleslang
        autosub.OPENSUBTITLESUSER = opensubtitlesuser
        autosub.OPENSUBTITLESPASSWD = opensubtitlespasswd.replace("%","%%")
        autosub.UNDERTEXTERLANG = undertexterlang
        autosub.ADDIC7EDLANG = addic7edlang
        autosub.ADDIC7EDUSER = addic7eduser
        autosub.ADDIC7EDPASSWD = addic7edpasswd.replace("%","%%")
        autosub.WEBDL = webdl
        
        autosub.MINMATCHSCORE = 0
        if mmssource:
            autosub.MINMATCHSCORE += 8
        if mmsquality:
            autosub.MINMATCHSCORE += 4
        if mmscodec:
            autosub.MINMATCHSCORE += 2
        if mmsrelease:
            autosub.MINMATCHSCORE += 1 
               
        autosub.SCHEDULERSCANDISK = int(scandisk)
        autosub.SCHEDULERCHECKSUB = int(checksub)
        autosub.LOGLEVEL = int(loglevel)
        autosub.LOGNUM = int(lognum)
        autosub.LOGSIZE = int(logsize)
        autosub.LOGLEVELCONSOLE = int(loglevelconsole)
        autosub.WEBSERVERIP = webserverip
        autosub.WEBSERVERPORT = int(webserverport)
        autosub.USERNAME = username
        autosub.PASSWORD = password
        autosub.WEBROOT = webroot
        autosub.SKIPSHOW = autosub.Config.stringToDict(skipshow)
        autosub.USERNAMEMAPPING = autosub.Config.stringToDict(usernamemapping)
        autosub.USERADDIC7EDMAPPING = autosub.Config.stringToDict(useraddic7edmapping)

        # Now save to the configfile
        message = autosub.Config.WriteConfig(configsection="")

        tmpl = PageTemplate(file="interface/templates/config-settings.tmpl")
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"
        return str(tmpl)

    @cherrypy.expose
    def saveNotification(self, notifymail, notifygrowl, notifynma, notifytwitter, mailsrv, mailfromaddr, mailtoaddr, 
                         mailusername, mailpassword, mailsubject, mailencryption, mailauth, growlhost, growlport, 
                         growlpass, nmaapi, twitterkey, twittersecret, notifyprowl, prowlapi, prowlpriority, 
                         notifypushalot, pushalotapi, notifypushbullet, pushbulletapi, notifypushover, pushoverapi, 
                         nmapriority, notifyboxcar2, boxcar2token, notifyplex, plexserverhost, plexserverport):

        # Set all internal notify variables
        autosub.NOTIFYMAIL = notifymail
        autosub.MAILSRV = mailsrv
        autosub.MAILFROMADDR = mailfromaddr
        autosub.MAILTOADDR = mailtoaddr
        autosub.MAILUSERNAME = mailusername
        autosub.MAILPASSWORD = mailpassword
        autosub.MAILSUBJECT = mailsubject
        autosub.MAILENCRYPTION = mailencryption
        autosub.MAILAUTH = mailauth
        autosub.NOTIFYGROWL = notifygrowl
        autosub.GROWLHOST = growlhost
        autosub.GROWLPORT = growlport
        autosub.GROWLPASS = growlpass
        autosub.NOTIFYNMA = notifynma
        autosub.NMAAPI = nmaapi
        autosub.NMAPRIORITY = int(nmapriority)
        autosub.NOTIFYTWITTER = notifytwitter
        autosub.TWITTERKEY = twitterkey
        autosub.TWITTERSECRET = twittersecret
        autosub.NOTIFYPROWL = notifyprowl
        autosub.PROWLAPI = prowlapi
        autosub.PROWLPRIORITY = int(prowlpriority)
        autosub.NOTIFYPUSHALOT = notifypushalot
        autosub.PUSHALOTAPI = pushalotapi
        autosub.NOTIFYPUSHBULLET = notifypushbullet
        autosub.PUSHBULLETAPI = pushbulletapi
        autosub.NOTIFYPUSHOVER = notifypushover
        autosub.PUSHOVERAPI = pushoverapi
        autosub.NOTIFYBOXCAR2 = notifyboxcar2
        autosub.BOXCAR2TOKEN = boxcar2token
        autosub.NOTIFYPLEX = notifyplex
        autosub.PLEXSERVERHOST = plexserverhost
        autosub.PLEXSERVERPORT = plexserverport

        # Now save to the configfile
        message = autosub.Config.WriteConfig(configsection="notifications")

        tmpl = PageTemplate(file="interface/templates/config-notification.tmpl")
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"
        return str(tmpl)

    @cherrypy.expose
    def flushCache(self):
        flushcache()
        message = 'Cache flushed'
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"
        return str(tmpl)
    
    @cherrypy.expose
    def flushLastdown(self):
        lastDown().flushLastdown()
        message = 'Downloaded subtitles database flushed'
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"
        return str(tmpl)
    
    @cherrypy.expose
    def checkVersion(self):
        checkversion = autosub.Helpers.CheckVersion()
        
        if checkversion == 0:
            message = 'You are running the latest version!'
        elif checkversion == 1:
            message = 'There is a new version available!'
        elif checkversion == 2:
            message = 'There is a new major release available for your version.<br> For example, you are running an Alpha version and there is a Beta version available.'
        elif checkversion == 3:
            message = 'There is a newer testing version available. Only the risk-takers should upgrade!'
        elif checkversion == 4:
            message = 'What are you doing here??? It is time to upgrade!'
        else:
            message = 'Something went wrong there, is Google-Project reachable?<br> Or are you running a really old release?'

        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"
        
        return str(tmpl)   
    
    @cherrypy.expose
    def testPushalot(self, pushalotapi):
        
        log.info("Notification: Testing Pushalot")
        result = notify.pushalot.test_notify(pushalotapi)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Pushalot</strong>."
        else:
            return "Failed to send a test message with <strong>Pushalot</strong>."

    @cherrypy.expose
    def testPushbullet(self, pushbulletapi):
        
        log.info("Notification: Testing Pushbullet")
        result = notify.pushbullet.test_notify(pushbulletapi)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Pushbullet</strong>."
        else:
            return "Failed to send a test message with <strong>Pushbullet</strong>."
    
    @cherrypy.expose
    def testMail(self, mailsrv, mailfromaddr, mailtoaddr, mailusername, mailpassword, mailsubject, mailencryption, mailauth):  
        
        log.info("Notification: Testing Mail")
        result = notify.mail.test_notify(mailsrv, mailfromaddr, mailtoaddr, mailusername, mailpassword, mailsubject, mailencryption, mailauth)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Mail</strong>."
        else:
            return "Failed to send a test message with <strong>Mail</strong>."
    
    @cherrypy.expose
    def testTwitter(self, twitterkey, twittersecret):
        
        log.info("Notification: Testing Twitter")  
        result = notify.twitter.test_notify(twitterkey, twittersecret)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Twitter</strong>."
        else:
            return "Failed to send a test message with <strong>Twitter</strong>."
    
    @cherrypy.expose
    def testNotifyMyAndroid(self, nmaapi, nmapriority):
        
        log.info("Notification: Testing Notify My Android")     
        result = notify.nma.test_notify(nmaapi, nmapriority)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Notify My Android</strong>."
        else:
            return "Failed to send a test message with <strong>Notify My Android</strong>."
    
    @cherrypy.expose
    def testPushover(self, pushoverapi):
        
        log.info("Notification: Testing Pushover")
        result = notify.pushover.test_notify(pushoverapi)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Pushover</strong>."
        else:
            return "Failed to send a test message with <strong>Pushover</strong>."
    
    @cherrypy.expose
    def testGrowl(self, growlhost, growlport, growlpass):
        
        log.info("Notification: Testing Growl")
        result = notify.growl.test_notify(growlhost, growlport, growlpass)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Growl</strong>."
        else:
            return "Failed to send a test message with <strong>Growl</strong>."
    
    @cherrypy.expose
    def testProwl(self, prowlapi, prowlpriority):
        
        log.info("Notification: Testing Prowl")
        result = notify.prowl.test_notify(prowlapi, prowlpriority)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Prowl</strong>."
        else:
            return "Failed to send a test message with <strong>Prowl</strong>."
    
    @cherrypy.expose
    def testBoxcar2(self, boxcar2token):
        
        log.info("Notification: Testing Boxcar2")
        result = notify.boxcar2.test_notify(boxcar2token)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Boxcar2</strong>."
        else:
            return "Failed to send a test message with <strong>Boxcar2</strong>."
    
    @cherrypy.expose
    def testAddic7ed(self, addic7eduser, addic7edpasswd):
        
        log.info("Addic7ed: Testing Login")
        result = autosub.Addic7ed.Addic7edAPI().login(addic7eduser, addic7edpasswd)
        if result:
            return "Auto-Sub successfully logged on to <strong>Addic7ed</strong>."
        else:
            return "Failed to login to <strong>Addic7ed</strong>."
    
    @cherrypy.expose
    def testPlex(self, plexserverhost, plexserverport):
        
        log.info("Notification: Testing Plex Media Server")
        result = notify.plexmediaserver.test_update_library(plexserverhost, plexserverport)
        if result:
            return "Auto-Sub successfully updated the media library on your <strong>Plex Media Server</strong>."
        else:
            return "Failed to update the media library on your <strong>Plex Media Server</strong>."
    
    @cherrypy.expose
    def RetrieveAddic7edCount(self):
        if autosub.WANTEDQUEUELOCK != True:
            log.info("Addic7ed: Retrieving Addic7ed download count")
            result = Addic7edAPI().checkCurrentDownloads()
            if result:
                return "Addic7ed count: %s of %s" % (autosub.DOWNLOADS_A7, autosub.DOWNLOADS_A7MAX)
            else:
                return "Unable to retrieve count at the moment."
        else:
            return "Auto-Sub is currently checking Addic7ed for subtitles, unable to refresh data at the moment."
    
    @cherrypy.expose
    def testOpenSubtitles(self, opensubtitlesuser, opensubtitlespasswd):
        log.info('OpenSubtitles: Testing Login with user %s' % opensubtitlesuser)
        result= OpenSubtitlesLogin(opensubtitlesuser,opensubtitlespasswd)
        if result:
            log.info('OpenSubtitles: login successful')
            return "Auto-Sub successfully logged on to <strong>OpenSubtitles</strong>."
        else:
            return "Failed to login to <strong>OpenSubtitles</strong>."
    
    @cherrypy.expose
    def regTwitter(self, token_key=None, token_secret=None, token_pin=None):
        import library.oauth2 as oauth
        import autosub.notify.twitter as notifytwitter 
        try:
            from urlparse import parse_qsl
        except:
            from cgi import parse_qsl
        
        if not token_key and not token_secret:
            consumer = oauth.Consumer(key=notifytwitter.CONSUMER_KEY, secret=notifytwitter.CONSUMER_SECRET)
            oauth_client = oauth.Client(consumer)
            response, content = oauth_client.request(notifytwitter.REQUEST_TOKEN_URL, 'GET')
            if response['status'] != '200':
                message = "Something went wrong when trying to register Twitter"
                tmpl = PageTemplate(file="interface/templates/config-settings.tmpl")
                tmpl.message = message
                tmpl.displaymessage = "Yes"
                tmpl.modalheader = "Error"
                return str(tmpl)
            else:
                request_token = dict(parse_qsl(content))
                tmpl = PageTemplate(file="interface/templates/config-twitter.tmpl")
                tmpl.url = notifytwitter.AUTHORIZATION_URL + "?oauth_token=" + request_token['oauth_token']
                token_key = request_token['oauth_token']
                token_secret = request_token['oauth_token_secret']
                tmpl.token_key = token_key
                tmpl.token_secret = token_secret
                return str(tmpl)
        
        if token_key and token_secret and token_pin:
            
            token = oauth.Token(token_key, token_secret)
            token.set_verifier(token_pin)
            consumer = oauth.Consumer(key=notifytwitter.CONSUMER_KEY, secret=notifytwitter.CONSUMER_SECRET)
            oauth_client2 = oauth.Client(consumer, token)
            response, content = oauth_client2.request(notifytwitter.ACCESS_TOKEN_URL, method='POST', body='oauth_verifier=%s' % token_pin)
            access_token = dict(parse_qsl(content))

            if response['status'] != '200':
                message = "Something went wrong when trying to register Twitter"
                tmpl = PageTemplate(file="interface/templates/config-settings.tmpl")
                tmpl.message = message
                tmpl.displaymessage = "Yes"
                tmpl.modalheader = "Error"
                return str(tmpl)
            else:
                autosub.TWITTERKEY = access_token['oauth_token']
                autosub.TWITTERSECRET = access_token['oauth_token_secret']
                
                message = "Twitter registration complete.<br> Remember to save your configuration and test Twitter!"
                tmpl = PageTemplate(file="interface/templates/config-settings.tmpl")
                tmpl.message = message
                tmpl.displaymessage = "Yes"
                tmpl.modalheader = "Information"
                return str(tmpl)
                

class Home:
    @cherrypy.expose
    def index(self):
        useragent = cherrypy.request.headers.get("User-Agent", '')
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        if autosub.Helpers.CheckMobileDevice(useragent) and autosub.MOBILEAUTOSUB:
            tmpl = PageTemplate(file="interface/templates/mobile/home.tmpl")
        return str(tmpl)
    
    @cherrypy.expose
    def runNow(self):
        #time.sleep is here to prevent a timing issue, where checksub is runned before scandisk
        useragent = cherrypy.request.headers.get("User-Agent", '')
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        if autosub.Helpers.CheckMobileDevice(useragent) and autosub.MOBILEAUTOSUB:
            tmpl = PageTemplate(file="interface/templates/mobile/message.tmpl")

        if not hasattr(autosub.CHECKSUB, 'runnow'):
            tmpl.message = "Auto-Sub is already running, no need to rerun"
            tmpl.displaymessage = "Yes"
            tmpl.modalheader = "Information"
            return str(tmpl)

        autosub.SCANDISK.runnow = True
        time.sleep(5)
        autosub.CHECKSUB.runnow = True

        tmpl.message = "Auto-Sub is now checking for subtitles!"
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"

        return str(tmpl)

    @cherrypy.expose
    def exitMini(self):
        if autosub.MOBILEAUTOSUB:
            autosub.MOBILEAUTOSUB = False
            redirect("/home")
        else:
            autosub.MOBILEAUTOSUB = True
            redirect("/home")
    
    @cherrypy.expose
    def shutdown(self):
        tmpl = PageTemplate(file="interface/templates/stopped.tmpl")
        
        if not hasattr(autosub.CHECKSUB, 'stop'):
            tmpl = PageTemplate(file="interface/templates/home.tmpl")
            tmpl.message = "Auto-Sub is still running CheckSub, you cannot shutdown at the moment.<br>Please wait a few minutes."
            tmpl.displaymessage = "Yes"
            tmpl.modalheader = "Information"
            return str(tmpl)
        
        threading.Timer(2, autosub.AutoSub.stop).start()
        return str(tmpl)

class Log:
    @cherrypy.expose
    def index(self, loglevel = ''):
        redirect("/log/viewLog")
    
    @cherrypy.expose
    def viewLog(self, loglevel = ''):
        tmpl = PageTemplate(file="interface/templates/viewlog.tmpl")
        if loglevel == '':
            tmpl.loglevel = 'All'
        else:
            tmpl.loglevel = loglevel
        result = autosub.Helpers.DisplayLogFile(loglevel)
        tmpl.logentries = result
        
        return str(tmpl)   
    
    @cherrypy.expose
    def clearLog(self):
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        tmpl.message = autosub.Helpers.ClearLogFile()
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"
        return str(tmpl)

class Mobile:
    @cherrypy.expose
    def index(self):
        tmpl = PageTemplate(file="interface/templates/mobile/home.tmpl")
        return str(tmpl)

class WebServerInit():
    @cherrypy.expose
    def index(self):
        redirect("/home")
    
    home = Home()
    config = Config()
    log = Log()
    mobile = Mobile()

    def error_page_401(status, message, traceback, version):
        return "Error %s - You don't have access to this resource." %status
    
    def error_page_404(status, message, traceback, version):
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        message = "Page could not be found.<br><br><center><textarea rows='15' wrap='off' class='traceback'>%s</textarea></center>" %traceback
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Error %s" %status
        return str(tmpl)
    
    def error_page_500(status, message, traceback, version):
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        message = "Try again. If this error doesn't go away, please report the issue.<br><br><center><textarea rows='15' wrap='off' class='traceback'>%s</textarea></center>" %traceback
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Error %s" %status
        return str(tmpl)

    _cp_config = {'error_page.401':error_page_401,
                  'error_page.404':error_page_404,
                  'error_page.500':error_page_500}
