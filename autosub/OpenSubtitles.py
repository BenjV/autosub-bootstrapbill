
import autosub
import xmlrpclib
import logging
import time

log = logging.getLogger('thelogger')


def OpenSubtitlesLogin(opensubtitlesusername=None,opensubtitlespasswd=None):

    autosub.OPENSUBTITLESSERVER = xmlrpclib.Server(autosub.OPENSUBTITLESURL)
        # Expose to test login
        # When fields are empty it will check the config file
    if opensubtitlesusername and opensubtitlespasswd:
        try:
            Result = autosub.OPENSUBTITLESSERVER.LogIn(opensubtitlesusername, opensubtitlespasswd, 'dut', autosub.OPENSUBTITLESUSERAGENT)
        except:
            log.debug('OpenSubtitlesLogin: Login with user %s failed.'  % opensubtitlesusername)
            return False
        log.info('OpenSubtitlesLogin: Test Login with User %s. Result is: %s' %  (opensubtitlesusername,Result['status']))
        if Result['status'] == '200 OK':
            autosub.OPENSUBTITLESTIME = time.time()
            autosub.OPENSUBTITLESTOKEN = Result['token']
            return True
        else:
            autosub.OPENSUBTITLESTOKEN = None
            return False
        return True
    else:
        if not autosub.OPENSUBTITLESUSER or not autosub.OPENSUBTITLESPASSWD:
            return False
        if not autosub.OPENSUBTITLESTOKEN:
            try:
                Result = autosub.OPENSUBTITLESSERVER.LogIn(autosub.OPENSUBTITLESUSER, autosub.OPENSUBTITLESPASSWD, 'dut', autosub.OPENSUBTITLESUSERAGENT)
            except:
                log.debug('OpenSubtitlesLogin: Login with user %s failed.'  % autosub.OPENSUBTITLESUSER)
                return False
            log.info('OpenSubtitlesLogin: Login with User %s. Message is: %s' %  (autosub.OPENSUBTITLESUSER, Result['status']))
            if Result['status'] == '200 OK':
                autosub.OPENSUBTITLESTOKEN = Result['token']
            else:            
                autosub.OPENSUBTITLESTOKEN = None
                return False
        else:
            log.debug('OpenSubtitlesLogin: Already Logged in with user %s'  % autosub.OPENSUBTITLESUSER)
            return True

def OpenSubtitlesLogout():
    if autosub.OPENSUBTITLESTOKEN:
        
        try:
            Result = autosub.OPENSUBTITLESSERVER.LogOut(autosub.OPENSUBTITLESTOKEN)['status']
        except:
            autosub.OPENSUBTITLESTOKEN = None
            log.info('OpenSubtitles: Logout with User %s failed.')
            return False
        if Result == '200 OK':
            autosub.OPENSUBTITLESTOKEN = None
            log.info('OpenSubtitlesLogout: User: %s logged out.', autosub.OPENSUBTITLESUSER)
            return True
        else:
            log.info('OpenSubtitles: Logout with User %s failed. Message is: %s' %  (autosub.OPENSUBTITLESUSER, Result))
            return False


