
import autosub
import xmlrpclib
import logging

log = logging.getLogger('thelogger')


def OpenSubtitlesLogin(opensubtitlesusername=None,opensubtitlespasswd=None):
    autosub.OPENSUBTITLESSERVER = xmlrpclib.Server(autosub.OPENSUBTITLESURL)
        # Expose to test login
        # When fields are empty it will check the config file
    if opensubtitlesusername and opensubtitlespasswd:
        Result = autosub.OPENSUBTITLESSERVER.LogIn(opensubtitlesusername, opensubtitlespasswd, 'dut', autosub.OPENSUBTITLESUSERAGENT)
        log.info('OpenSubtitlesLogin: Test Login with User %s. Result is: %s' %  (opensubtitlesusername,Result['status']))
        if Result['status'] == '200 OK':
            autosub.OPENSUBTITLESTOKEN = Result['token']
            return True
        else:
            return False
        return True
    else:
        if not autosub.OPENSUBTITLESTOKEN:
            Result = autosub.OPENSUBTITLESSERVER.LogIn(autosub.OPENSUBTITLESUSER, autosub.OPENSUBTITLESPASSWD, 'dut', autosub.OPENSUBTITLESUSERAGENT)
            log.info('OpenSubtitlesLogin: Login with User %s. Message is: %s' %  (autosub.OPENSUBTITLESUSER, Result['status']))
            if Result['status'] == '200 OK':
                autosub.OPENSUBTITLESTOKEN = Result['token']
                return True
            else:            
                autosub.OPENSUBTITLESTOKEN = None
                return False
        else:
            log.debug('OpenSubtitlesLogin: Already Logged in with user %s'  % autosub.OPENSUBTITLESUSER)
            return True

def OpenSubtitlesLogout():
    if autosub.OPENSUBTITLESTOKEN:
        Result = autosub.OPENSUBTITLESSERVER.LogOut(autosub.OPENSUBTITLESTOKEN)['status']
        if Result == '200 OK':
            autosub.OPENSUBTITLESTOKEN = None
            log.info('OpenSubtitlesLogout: User: %s logged out.', autosub.OPENSUBTITLESUSER)
            return True
        else:
            log.info('OpenSubtitles: Logout with User %s failed. Message is: %s' %  (autosub.OPENSUBTITLESUSER, Result))
            return False


