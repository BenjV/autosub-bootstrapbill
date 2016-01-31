import autosub
import logging

import urllib
import urllib2
import base64

from xml.dom import minidom

log = logging.getLogger('thelogger')

def test_update_library(plexserverhost, plexserverport):
    log.debug("Plex Media Server: Trying to update the TV shows library.")
    return _update_library(plexserverhost, plexserverport)

def send_update_library():
    log.debug("Plex Media Server: Trying to update the TV shows library.")
    plexserverhost = autosub.PLEXSERVERHOST
    plexserverport = int(autosub.PLEXSERVERPORT)
    return _update_library(plexserverhost, plexserverport)

def _update_library(plexserverhost, plexserverport):
    if not plexserverhost:
        plexserverhost = autosub.PLEXSERVERHOST
    
    if not plexserverport:
        plexserverport = int(autosub.PLEXSERVERPORT)
    
    url = "http://%s:%s/library/sections" % (plexserverhost, plexserverport)
    try:
        xml_sections = minidom.parse(urllib.urlopen(url))
    except IOError, e:
        log.error("Plex Media Server: Error while trying to contact: %s" % e)
        return False

    sections = xml_sections.getElementsByTagName('Directory')
    if not sections:
        log.debug("Plex Media Server: Server not running on: %s:%s" % (plexserverhost, plexserverport))
        return False

    for s in sections:
        if s.getAttribute('type') == "show":
            url = "http://%s:%s/library/sections/%s/refresh" % (plexserverhost, plexserverport, s.getAttribute('key'))
            try:
                urllib.urlopen(url)
                log.info("Plex Media Server: TV Shows library is currently updating.")
                return True
            except Exception, e:
                log.error("Plex Media Server: Error updating library section: %s" % e)
                return False