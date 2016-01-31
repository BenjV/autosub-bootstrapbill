import urllib, urllib2
import logging
import autosub

log = logging.getLogger('thelogger')

API_URL = "https://api.pushover.net/1/messages.json"
AUTOSUB_TOKEN = "aF9PCUbt6EmKwAHEFUaXBBxibmpdyw"

def test_notify(pushoverapi):
    message = "Testing Pushover settings from AutoSub"
    return _send_notify(pushoverapi, message)

def send_notify(lang, subtitlefile, videofile, website):
    log.debug("Pushover: Trying to send a notification")
    message = "Auto-Sub just downloaded the following subtitle: \n%s from %s" %(subtitlefile, website)
    pushoverapi = autosub.PUSHOVERAPI
    return _send_notify(pushoverapi, message)

def _send_notify(pushoverapi, message):
    """
    Sends a pushover notification to the address provided
        
    msg: The message to send (unicode)
    title: The title of the message
    userKey: The pushover user id to send the message to (or to subscribe with)
        
    returns: True if the message succeeded, False otherwise
    """
    
    if not pushoverapi:
        pushoverapi = autosub.PUSHOVERAPI
      
    data = urllib.urlencode({
        'token': AUTOSUB_TOKEN,
        'title': "Auto-Sub",
        'user': pushoverapi,
        'message': message.encode('utf-8'),
    })


    # send the request to pushover
    try:
        req = urllib2.Request(API_URL)
        handle = urllib2.urlopen(req, data)
        handle.close()
            
    except urllib2.URLError, e:
        # if we get an error back that doesn't have an error code then who knows what's really happening
        if not hasattr(e, 'code'):
            log.error("Pushover: notification failed.")
            return False
        else:
            log.error("Pushover: notification failed. Error code: " + str(e.code))

        # HTTP status 404 if the provided email address isn't a Pushover user.
        if e.code == 404:
            log.warning("Pushover: Username is wrong/not a pushover email. Pushover will send an email to it")
            return False
            
        # For HTTP status code 401's, it is because you are passing in either an invalid token, or the user has not added your service.
        elif e.code == 401:
                
            #HTTP status 401 if the user doesn't have the service added
            subscribeNote = _send_notify(pushoverapi, message)
            if subscribeNote:
                log.debug("Pushover: Subscription send")
                return True
            else:
                log.error("Pushover: Subscription could not be send")
                return False
            
        # If you receive an HTTP status code of 400, it is because you failed to send the proper parameters
        elif e.code == 400:
            log.error("Pushover: Wrong data sent")
            return False

    log.info("Pushover: notification sent.")
    return True
