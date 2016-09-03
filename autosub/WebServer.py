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
from autosub.version import autosubversion
import autosub.notify as notify

import autosub.Helpers

from autosub.Addic7ed import Addic7edAPI
from autosub.OpenSubtitles import OpenSubtitlesLogin

def redirect(abspath, *args, **KWs):
    assert abspath[0] == '/'
    raise cherrypy.HTTPRedirect(autosub.WEBROOT + abspath, *args, **KWs)

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
        title = title.decode("utf-8")
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
            autosub.SKIPSHOW[title] = episodestoskip
            autosub.SKIPSHOWUPPER[title.upper()] = episodestoskip
            message = autosub.Config.WriteConfig()

            #print season, episode
            Name = 'ImdbId' if title.isnumeric() else 'title'

            if season == -1:
                tmpl.message = "Serie with %s: <strong>%s</strong> will be skipped.<br> This will happen the next time that Auto-Sub checks for subtitles" % (Name, title.title())
            elif episode:
                tmpl.message = "Serie with %s: <strong>%s</strong> season <strong>%s</strong> episode <strong>%s</strong> will be skipped.<br> This will happen the next time that Auto-Sub checks for subtitles" % (Name, title.title(), season, episode)
            else:
                tmpl.message = "Serie with %s: <strong>%s</strong> season <strong>%s</strong> will be skipped.<br> This will happen the next time that Auto-Sub checks for subtitles" % (Name, title.title(), season)
            
            tmpl.displaymessage = "Yes"
            tmpl.modalheader = "Information"
            return str(tmpl)

    @cherrypy.expose  
    def saveConfig(self, subeng, skipstringnl, skipstringen, skipfoldersnl,skipfoldersen, subnl, postprocesscmd, 
                   logfile, seriespath, subcodec,  username, 
                   password, webroot, skipshow, lognum, loglevelconsole, loglevel, 
                   webserverip, webserverport, usernamemapping, useraddic7edmapping,
                   opensubtitlesuser, opensubtitlespasswd,  addic7eduser, addic7edpasswd, addic7ed=None,opensubtitles=None, podnapisi=None, subscene=None, 
                   wantedfirst = None, browserrefresh = None, skiphiddendirs = None,useaddic7ed=None,launchbrowser=None,interval = None, logsize=None,
                   fallbacktoeng = None, downloadeng = None, englishsubdelete = None, notifyen = None, notifynl = None, downloaddutch = None,
                   mmssource = u'0', mmsquality = u'0', mmscodec = u'0', mmsrelease = u'0',hearingimpaired = None):

        if autosub.SEARCHBUSY:
            tmpl = PageTemplate(file="interface/templates/config-settings.tmpl")
            tmpl.message = "Search is busy, not possible to save the config now"
            tmpl.displaymessage = "Yes"
            tmpl.modalheader = "Information"
            return str(tmpl)
                   
        # Set all internal variables
        autosub.SERIESPATH = seriespath
        autosub.LOGFILE = logfile
        autosub.DOWNLOADENG = True if downloadeng else False
        autosub.DOWNLOADDUTCH = True if downloaddutch else False
        autosub.FALLBACKTOENG = True if fallbacktoeng else False
        autosub.ENGLISHSUBDELETE = True if englishsubdelete else False
        autosub.SUBENG = subeng
        autosub.SUBNL = subnl
        autosub.NOTIFYEN = True if notifyen else False 
        autosub.NOTIFYNL = True if notifynl else False
        autosub.POSTPROCESSCMD = postprocesscmd
        autosub.SUBCODEC = subcodec
        autosub.LAUNCHBROWSER = True if launchbrowser else False
        autosub.SKIPHIDDENDIRS = True if skiphiddendirs else False
        autosub.WANTEDFIRST = True if wantedfirst else False
        autosub.PODNAPISI = True if podnapisi else False
        autosub.SUBSCENE = True if subscene else False
        autosub.OPENSUBTITLES = True if opensubtitles else False
        autosub.OPENSUBTITLESUSER = opensubtitlesuser
        autosub.OPENSUBTITLESPASSWD = opensubtitlespasswd.replace("%","%%")
        autosub.ADDIC7ED = True if addic7ed else False
        autosub.ADDIC7EDUSER = addic7eduser
        autosub.ADDIC7EDPASSWD = addic7edpasswd.replace("%","%%")
        autosub.BROWSERREFRESH = browserrefresh
        autosub.SKIPSTRINGNL = skipstringnl
        autosub.SKIPSTRINGEN = skipstringen
        autosub.SKIPFOLDERSNL = skipfoldersnl
        autosub.SKIPFOLDERSEN = skipfoldersen
        autosub.MINMATCHSCORE = int(mmssource) + int(mmsquality) + int(mmscodec) + int(mmsrelease)
        autosub.SEARCHINTERVAL = int(interval)*3600
    # here we change the loglevels if neccessary
        if autosub.LOGLEVEL != int(loglevel):
            autosub.LOGLEVEL = int(loglevel)
            log.setLevel(autosub.LOGLEVEL)
            autosub.LOGHANDLER.setLevel(autosub.LOGLEVEL)
        if autosub.LOGNUM != int(lognum):
            autosub.LOGNUM = int(lognum)
            autosub.LOGHANDLER.backupCount = autosub.LOGNUM
        if autosub.LOGSIZE != int(logsize)*1024:
            autosub.LOGSIZE = int(logsize)*1024
            autosub.LOGHANDLER.maxBytes = autosub.LOGSIZE

        if autosub.LOGLEVELCONSOLE != int(loglevelconsole):
            autosub.LOGLEVELCONSOLE =int(loglevelconsole)
            autosub.CONSOLE.level = autosub.LOGLEVELCONSOLE
        autosub.WEBSERVERIP = webserverip
        autosub.WEBSERVERPORT = int(webserverport)
        autosub.USERNAME = username
        autosub.PASSWORD = password.replace("%","%%")
        autosub.WEBROOT = webroot
        autosub.SKIPSHOW = stringToDict(skipshow)
        autosub.USERNAMEMAPPING = stringToDict(usernamemapping)
        autosub.USERADDIC7EDMAPPING = stringToDict(useraddic7edmapping)
        autosub.HI = True if hearingimpaired else False
        Reboot = False
        if autosub.WEBSERVERIP != webserverip or autosub.WEBSERVERPORT != int(webserverport) or autosub.USERNAME != username or autosub.PASSWORD != password or autosub.WEBROOT != webroot:
            Reboot = True
        # Now save to the configfile
        message = autosub.Config.WriteConfig()
        if Reboot:
            message += '\n There are settings changed which need a reboot. Please do a manual reboot'
        tmpl = PageTemplate(file="interface/templates/config-settings.tmpl")
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"
        return str(tmpl)

    @cherrypy.expose
    def saveNotification(self, notifymail, notifygrowl, notifynma, notifytwitter, mailsrv, mailfromaddr, mailtoaddr, 
                         mailusername, mailpassword, mailsubject, mailencryption, mailauth, growlhost, growlport, 
                         growlpass, nmaapi, twitterkey, twittersecret, notifyprowl, prowlapi, prowlpriority, 
                         notifypushalot, pushalotapi, notifypushbullet, pushbulletapi, notifypushover, pushoverappkey,pushoveruserkey, 
                         nmapriority, notifyboxcar2, boxcar2token, notifyplex, plexserverhost, plexserverport, plexserverusername, plexserverpassword):

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
        autosub.PUSHOVERAPPKEY = pushoverappkey
        autosub.PUSHOVERUSERKEY = pushoveruserkey
        autosub.NOTIFYBOXCAR2 = notifyboxcar2
        autosub.BOXCAR2TOKEN = boxcar2token
        autosub.NOTIFYPLEX = notifyplex
        autosub.PLEXSERVERHOST = plexserverhost
        autosub.PLEXSERVERPORT = plexserverport
        autosub.PLEXSERVERUSERNAME = plexserverusername
        autosub.PLEXSERVERPASSWORD = plexserverpassword

        # Now save to the configfile
        message = autosub.Config.WriteConfig()

        tmpl = PageTemplate(file="interface/templates/config-notification.tmpl")
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"
        return str(tmpl)
     
    @cherrypy.expose
    def testPushalot(self, pushalotapi, dummy):
        
        log.info("Notification: Testing Pushalot")
        result = notify.pushalot.test_notify(pushalotapi)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Pushalot</strong>."
        else:
            return "Failed to send a test message with <strong>Pushalot</strong>."

    @cherrypy.expose
    def testPushbullet(self, pushbulletapi, dummy):
        
        log.info("Notification: Testing Pushbullet")
        result = notify.pushbullet.test_notify(pushbulletapi)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Pushbullet</strong>."
        else:
            return "Failed to send a test message with <strong>Pushbullet</strong>."
    
    @cherrypy.expose
    def testMail(self, mailsrv, mailfromaddr, mailtoaddr, mailusername, mailpassword, mailsubject, mailencryption, mailauth, dummy):  
        
        log.info("Notification: Testing Mail")
        result = notify.mail.test_notify(mailsrv, mailfromaddr, mailtoaddr, mailusername, mailpassword, mailsubject, mailencryption, mailauth)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Mail</strong>."
        else:
            return "Failed to send a test message with <strong>Mail</strong>."
    
    @cherrypy.expose
    def testTwitter(self, twitterkey, twittersecret, dummy):
        
        log.info("Notification: Testing Twitter")  
        result = notify.twitter.test_notify(twitterkey, twittersecret)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Twitter</strong>."
        else:
            return "Failed to send a test message with <strong>Twitter</strong>."
    
    @cherrypy.expose
    def testNotifyMyAndroid(self, nmaapi, nmapriority, dummy):
        
        log.info("Notification: Testing Notify My Android")     
        result = notify.nma.test_notify(nmaapi, nmapriority)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Notify My Android</strong>."
        else:
            return "Failed to send a test message with <strong>Notify My Android</strong>."
    
    @cherrypy.expose
    def testPushover(self, pushoverappkey, pushoveruserkey, dummy):
        
        log.info("Notification: Testing Pushover")
        result = notify.pushover.test_notify(pushoverappkey, pushoveruserkey)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Pushover</strong>."
        else:
            return "Failed to send a test message with <strong>Pushover</strong>."
    
    @cherrypy.expose
    def testGrowl(self, growlhost, growlport, growlpass, dummy):
        
        log.info("Notification: Testing Growl")
        result = notify.growl.test_notify(growlhost, growlport, growlpass)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Growl</strong>."
        else:
            return "Failed to send a test message with <strong>Growl</strong>."
    
    @cherrypy.expose
    def testProwl(self, prowlapi, prowlpriority, dummy):
        
        log.info("Notification: Testing Prowl")
        result = notify.prowl.test_notify(prowlapi, prowlpriority)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Prowl</strong>."
        else:
            return "Failed to send a test message with <strong>Prowl</strong>."
    
    @cherrypy.expose
    def testBoxcar2(self, boxcar2token, dummy):
        
        log.info("Notification: Testing Boxcar2")
        result = notify.boxcar2.test_notify(boxcar2token)
        if result:
            return "Auto-Sub successfully sent a test message with <strong>Boxcar2</strong>."
        else:
            return "Failed to send a test message with <strong>Boxcar2</strong>."
   
   
    @cherrypy.expose
    def testPlex(self, plexserverhost, plexserverport, plexserverusername, plexserverpassword, dummy):
        
        log.info("Notification: Testing Plex Media Server")
        result = notify.plexmediaserver.test_update_library(plexserverhost, plexserverport, plexserverusername, plexserverpassword)
        if result:
            return "Auto-Sub successfully updated the media library on your <strong>Plex Media Server</strong>."
        else:
            return "Failed to update the media library on your <strong>Plex Media Server</strong>."
    
    @cherrypy.expose
    def RetrieveAddic7edCount(self):

        log.info("Addic7ed: Retrieving Addic7ed download count")
        #result = Addic7edAPI().checkCurrentDownloads()
        result = True
        if result:
            return "Addic7ed count: %s of %s" % (autosub.DOWNLOADS_A7, autosub.DOWNLOADS_A7MAX)
        else:
            return "Unable to retrieve count at the moment."

    @cherrypy.expose
    def testAddic7ed(self, addic7eduser, addic7edpasswd, dummy):
        if autosub.Addic7ed.Addic7edAPI().login(addic7eduser, addic7edpasswd):
            return "<strong>Success</strong>."
        else:
            return "<strong>Failure</strong>."

    @cherrypy.expose
    def testOpenSubtitles(self, opensubtitlesuser, opensubtitlespasswd, dummy):
        if  OpenSubtitlesLogin(opensubtitlesuser,opensubtitlespasswd):
            return "<strong>Success</strong>."
        else:
            return "<strong>Failure</strong>."
    
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
        useragent = cherrypy.request.headers.get("User-Agent", '')
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        if autosub.Helpers.CheckMobileDevice(useragent) and autosub.MOBILEAUTOSUB:
            tmpl = PageTemplate(file="interface/templates/mobile/message.tmpl")

        if not hasattr(autosub.CHECKSUB, 'runnow'):
            tmpl.message = "Auto-Sub is already running, no need to rerun"
            tmpl.displaymessage = "Yes"
            tmpl.modalheader = "Information"
            return str(tmpl)

        autosub.CHECKSUB.runnow = True

        tmpl.message = "Auto-Sub is now checking for subtitles!"
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"

        return str(tmpl)
    @cherrypy.expose
    def stopSearch(self):
        message = 'Search will be stopped after the current sub search has ended'
        autosub.SEARCHSTOP = True
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"     
        return str(tmpl)


    @cherrypy.expose
    def checkVersion(self):
        message = 'Active version &emsp;: ' + autosubversion + '<BR>Github version&emsp;: ' + autosub.Helpers.CheckVersion()
        tmpl = PageTemplate(file="interface/templates/home.tmpl")
        tmpl.message = message
        tmpl.displaymessage = "Yes"
        tmpl.modalheader = "Information"     
        return str(tmpl)

    @cherrypy.expose
    def UpdateAutoSub(self):
        threading.Thread(target=autosub.Helpers.UpdateAutoSub).start()
        redirect("/home")

    @cherrypy.expose
    def RebootAutoSub(self):
        threading.Timer(1,autosub.Helpers.RebootAutoSub).start()
        redirect("/home")

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
        threading.Timer(5, autosub.AutoSub.stop).start()
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
