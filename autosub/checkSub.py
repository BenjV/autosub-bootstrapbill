# Autosub checkSub.py - https://github.com/Donny87/autosub-bootstrapbill
#
# The Autosub checkSub module
#

import logging
import os
import time
import sqlite3

# Autosub specific modules
import autosub.getSubLinks
from autosub.Db import idCache, EpisodeIdCache
import autosub.Helpers as Helpers
from autosub.downloadSubs import DownloadSub
from autosub.OpenSubtitles import OpenSubtitlesLogin, OpenSubtitlesLogout, GetEpisodeId

# Settings
log = logging.getLogger('thelogger')


class checkSub():
    """
    Check the SubtitleSeeker API for subtitles of episodes that are in the WANTEDQUEUE.
    If the subtitles are found, call DownloadSub
    """
    def run(self):
        log.debug("checkSub: Starting round of checkSub")
        # First we check if checksub in not still running
        if autosub.WANTEDQUEUELOCK:
            log.info("checkSub: Exiting, another threat is using the queues. Will try again in 60 seconds")
            time.sleep(60)
            return False
        else:
            autosub.WANTEDQUEUELOCK = True
        autosub.DBCONNECTION = sqlite3.connect(autosub.DBFILE)
        autosub.DBIDCACHE = idCache()
        autosub.DBEPISODECACHE = EpisodeIdCache()

        toDelete_wantedQueue = []
        if not Helpers.checkAPICallsTvdb() or not Helpers.checkAPICallsSubSeeker():            
            log.warning("checkSub: out of api calls")
            return True
                             
        # Initiate the Addic7ed API and check the current number of downloads
        UseAddic= False
        if autosub.ADDIC7EDUSER and autosub.ADDIC7EDPASSWD and autosub.ADDIC7EDLANG != 'None':
            try:
                # Sets autosub.DOWNLOADS_A7 and autosub.DOWNLOADS_A7MAX
                # and gives a True response if it's ok to download from a7
                autosub.ADDIC7EDAPI = autosub.Addic7ed.Addic7edAPI()
                UseAddic= autosub.ADDIC7EDAPI.checkCurrentDownloads(logout=False)
            except:
                log.debug("checkSub: Couldn't connect with Addic7ed.com")
        # Initiate a session to OpenSubtitles and log in if OpenSubtitles is choosen
        if autosub.OPENSUBTITLESLANG != 'None' and autosub.OPENSUBTITLESUSER and autosub.OPENSUBTITLESPASSWD:
            UseOpensubtitles = OpenSubtitlesLogin()
        else:
            UseOpensubtitles = False
        for index, wantedItem in enumerate(autosub.WANTEDQUEUE):
            title = wantedItem['title']
            season = wantedItem['season']
            episode = wantedItem['episode']
            originalfile = wantedItem['originalFileLocationOnDisk']
            languages = wantedItem['lang']
                        
            
            if not Helpers.checkAPICallsTvdb() or not Helpers.checkAPICallsSubSeeker():
                #Make sure that we are allow to connect to SubtitleSeeker and TvDB
                log.warning("checkSub: out of api calls")
                break
            
            if autosub.SUBNL != "":
                nlsrtfile = os.path.splitext(originalfile)[0] + u"." + autosub.SUBNL + u".srt"
            else:
                nlsrtfile = os.path.splitext(originalfile)[0] + u".srt"
                        
            if autosub.SUBENG == "":
                # Check for overlapping names
                if autosub.SUBNL != "" or not autosub.DOWNLOADDUTCH:
                    engsrtfile = os.path.splitext(originalfile)[0] + u".srt"
                # Hardcoded fallback
                else:
                    engsrtfile = os.path.splitext(originalfile)[0] + u".en.srt"
            else:
                engsrtfile = os.path.splitext(originalfile)[0] + u"." + autosub.SUBENG + u".srt"

            
            #lets try to find a showid; no showid? skip this item
            showid,a7_id, OsId = Helpers.getShowid(title, UseAddic, UseOpensubtitles)
            if UseOpensubtitles and OsId:
                EpisodeId = GetEpisodeId(OsId, season, episode)
            else:
                EpisodeId = None
            log.debug("checkSub: ID's - IMDB: %s, Addic7ed: %s, OpenSubtitles: %s" %(showid,a7_id, OsId))
            if not showid:
                continue
            
            for lang in languages[:]:
                downloadItem = wantedItem.copy()
                downloadItem['downlang'] = lang

                # Check if Addic7ed download limit has been reached
                if UseAddic and autosub.DOWNLOADS_A7 >= autosub.DOWNLOADS_A7MAX:
                    UseAddic= False            
                    log.debug("checkSub: You have reached your 24h limit of %s  Addic7ed downloads!" % autosub.DOWNLOADS_A7MAX)

                log.debug("checkSub: trying to get a downloadlink for %s, language is %s" % (originalfile, lang))
                # get all links higher than the minmatch as input for downloadSub
                allResults = autosub.getSubLinks.getSubLinks(showid, a7_id, EpisodeId, lang, wantedItem)
                
                if not allResults:
                    log.debug("checkSub: no suitable subtitles were found for %s based on your minmatchscore" % downloadItem['originalFileLocationOnDisk'])
                    continue                                 

                if lang == autosub.DUTCH:
                    downloadItem['destinationFileLocationOnDisk'] = nlsrtfile
                elif lang == autosub.ENGLISH:
                    downloadItem['destinationFileLocationOnDisk'] = engsrtfile
                    
                if allResults:                   
                    log.info("checkSub: The episode %s - Season %s Episode %s has 1 or more matching subtitles on SubtitleSeeker, downloading it!" % (title, season, episode))
                    log.debug("checkSub: destination filename %s" % downloadItem['destinationFileLocationOnDisk'])
                
                    
                if not DownloadSub(allResults, UseAddic, downloadItem):
                    continue
                
                #Remove downloaded language
                languages.remove(lang)
                
                if lang == autosub.DUTCH:
                    if (autosub.FALLBACKTOENG and not autosub.DOWNLOADENG) and autosub.ENGLISH in languages:
                        log.debug('checkSub: We found a Dutch subtitle and fallback is true. Removing the English subtitle from the wantedlist.')
                        languages.remove(autosub.ENGLISH)
                
                    if autosub.ENGLISHSUBDELETE:
                        log.info("checkSub: Clean up English enabled")
                        if os.path.exists(engsrtfile):
                            log.debug("checkSub: Trying to delete English subtitle: %s" % engsrtfile)
                            try:
                                os.unlink(engsrtfile)
                                log.info("checkSub: Removed English subtitle: %s" % engsrtfile)
                            except:
                                log.error("checkSub: Error while trying to remove subtitle %s." % engsrtfile)
                        else:
                            log.info("checkSub: English subtitle not found.")
                
                if len(languages) == 0:
                    toDelete_wantedQueue.append(index)
                    break

        autosub.DBCONNECTION.close()
        del autosub.DBCONNECTION
        del autosub.DBIDCACHE
        del  autosub.DBEPISODECACHE
        if autosub.ADDIC7EDAPI:
            autosub.ADDIC7EDAPI.logout()

        if autosub.OPENSUBTITLESLOGGED_IN:
            OpenSubtitlesLogout()
                                        
        i = len(toDelete_wantedQueue) - 1
        while i >= 0:
            log.debug("checkSub: Removed item from the wantedQueue at index %s" % toDelete_wantedQueue[i])
            autosub.WANTEDQUEUE.pop(toDelete_wantedQueue[i])
            i = i - 1

        log.debug("checkSub: Finished round of checkSub")
        autosub.WANTEDQUEUELOCK = False
        return True
