#
# Autosub Tvdb.py -  https://github.com/Donny87/autosub-bootstrapbill
#
# The Tvdb API module
#

import logging

import urllib
import xml.etree.cElementTree as ET
from xml.dom import minidom
import autosub
import autosub.Helpers
from autosub.Db import EpisodeIdCache

# Settings
log = logging.getLogger('thelogger')


def getShowidApi(showName):
    """
    Search for the IMDB ID by using the TvDB API and the name of the show.
    Keyword arguments:
    showName -- Name of the show to search the showid for
    """
    
    api = autosub.IMDBAPI
    
    getShowIdUrl = "%sGetSeries.php?seriesname=%s" % (api, urllib.quote(showName.encode('utf8')))
    log.debug("getShowidApi: TvDB API request for %s: %s" % (showName, getShowIdUrl))
    if autosub.Helpers.checkAPICallsTvdb(use=True):
        try:
            tvdbapi = autosub.Helpers.API(getShowIdUrl)
            dom = minidom.parse(tvdbapi.resp)
            tvdbapi.resp.close()
        except:
            log.error("getShowidApi: The server returned an error for request %s" % getShowIdUrl)
            return None, None, None
        try:
            Result = dom.getElementsByTagName('SeriesName')
            Name = Result[0].firstChild.data if Result else u''
            Result = dom.getElementsByTagName('IMDB_ID')
            ImdbId = Result[0].firstChild.data[2:] if Result else u''
        except:
            return None,None
        return ImdbId,Name
    else:
        log.error("API: out of api calls for TvDB API")
        return None, None

def getShowName(imdbID):
    """
    Search for the official TV show name using the IMDB ID
    """
    
    api = autosub.IMDBAPI
    
    getShowIdUrl = "%sGetSeriesByRemoteID.php?imdbid=%s" % (api, imdbID)
    log.debug("getShowName: TvDB API request for imdbID %s %s" % (imdbID, getShowIdUrl))
    if autosub.Helpers.checkAPICallsTvdb(use=True):
        try:
            tvdbapi = autosub.Helpers.API(getShowIdUrl)
            dom = minidom.parse(tvdbapi.resp)
            tvdbapi.resp.close()
        except:
            log.error("getShowName: The server returned an error for request %s" % getShowIdUrl)
            return None
        
        if not dom or len(dom.getElementsByTagName('Series')) == 0:
            return None
        
        for sub in dom.getElementsByTagName('Series'):
            # Assume that first match is best, maybe adapt this in future
            try:
                TVShowName = sub.getElementsByTagName('SeriesName')[0].firstChild.data
            except:
                log.error("getShowName: Error while retrieving the official release name for %s." % imdbID)
                #log.error("getShowName: Recommend to add the IMDB ID for %s manually for the time being." % imdbID)
                return None    
            return TVShowName
    else:
        log.error("API: out of api calls for TvDB API")
        return None
    
