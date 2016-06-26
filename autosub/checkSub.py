# Autosub checkSub.py
#
# The Autosub checkSub module
#

import logging
import os
import time
import sqlite3

# Autosub specific modules
import autosub.getSubLinks
import autosub.scanDisk
from autosub.Db import idCache
import autosub.Helpers as Helpers
from autosub.downloadSubs import DownloadSub
from autosub.OpenSubtitles import OpenSubtitlesLogin, OpenSubtitlesLogout

# Settings
log = logging.getLogger('thelogger')


class checkSub():
    """
    Check the SubtitleSeeker API for subtitles of episodes that are in the WANTEDQUEUE.
    If the subtitles are found, call DownloadSub
    """
    def run(self):
        StartTime = time.time()
        autosub.DBCONNECTION = sqlite3.connect(autosub.DBFILE)
        autosub.DBIDCACHE = idCache()
        del autosub.WANTEDQUEUE[:]
        autosub.scanDisk.scanDisk().run()

        log.info("checkSub: Starting round of subs searching." )
                             
        # Initiate a session to OpenSubtitles and log in if OpenSubtitles is choosen
        if autosub.OPENSUBTITLES and autosub.OPENSUBTITLESUSER and autosub.OPENSUBTITLESPASSWD:
            OpenSubtitlesLogin()

        Index = 0
        End = len(autosub.WANTEDQUEUE)
        # loop through the wanted list and try to find subs for the video's
        # because we remove a video from the list we cannot use the internal counter from a for loop
        # so we track the position in the list with the variable 'Index'
        while Index < End:
            time.sleep(0)
            Wanted = {}
            Wanted = autosub.WANTEDQUEUE[Index]
            if not Wanted:
                Index += 1
                continue
            #First we check we have enough info to try to find a sub else we skip this one
            Skip = False
            if   autosub.MINMATCHSCORE & 8 and not Wanted['source']    : Skip = True
            elif autosub.MINMATCHSCORE & 4 and not Wanted['quality']   : Skip = True
            elif autosub.MINMATCHSCORE & 2 and not Wanted['codec']     : Skip = True
            elif autosub.MINMATCHSCORE & 1 and not Wanted['releasegrp']: Skip = True
            elif not Wanted['ImdbId'] : Skip = True
            if Skip:
                log.debug('checkSub: Skipped for not meeting the minmatch score. File is: %s' % Wanted['file'] )
                Index += 1
                continue


            if not Wanted['ImdbId']:
                Index += 1
                continue

            log.debug("checkSub: trying to get a downloadlink for %s, language is %s" % (Wanted['file'], Wanted['langs']))
            log.debug("checkSub: ID's are. IMDB: %s, Addic7ed: %s" %(Wanted['ImdbId'],Wanted['A7Id']))
            # get all links above the minimal match score as input for downloadSub
            SubsNL,SubsEN = autosub.getSubLinks.getSubLinks(Wanted)

            if not SubsNL and not SubsEN:
                log.debug("checkSub: no suitable subs were found for %s based on your minimal match score" % Wanted['file'])
                Index += 1
                continue
            if SubsNL:
                log.debug('checkSub: Dutch Subtitle(s) found trying to download the highest scored.')
                if DownloadSub(Wanted,SubsNL):
                    Wanted['langs'].remove(autosub.DUTCH)
                    if not autosub.DOWNLOADENG and autosub.ENGLISH in Wanted['langs']:
                        Wanted['langs'].remove(autosub.ENGLISH)
                        SubsEN =[]
                    if autosub.ENGLISHSUBDELETE and os.path.exists(os.path.join(Wanted['folder'],Wanted['file'] + Wanted['ENext'])):
                        try:
                            os.unlink(os.path.join(Wanted['folder'],Wanted['file'] + Wanted['ENext']))
                            log.info("checkSub: Removed English subtitle for : %s" % Wanted['file'])
                        except Exception as error:
                            log.error("checkSub: Error while trying to remove English subtitle message is:%s." % error)
            if SubsEN:
                log.debug('checkSub: English Subtitle(s) found trying to download the highest scored.')
                if DownloadSub(Wanted,SubsEN):
                    Wanted['langs'].remove(autosub.ENGLISH)
            if len(Wanted['langs']) == 0:
                del autosub.WANTEDQUEUE[Index]
                End -= 1
            else:
                Index += 1


        autosub.DBCONNECTION.close()
        del autosub.DBCONNECTION
        del autosub.DBIDCACHE
        if autosub.ADDIC7EDAPI:
            autosub.ADDIC7EDAPI.logout()

        if autosub.OPENSUBTITLESTOKEN:
            OpenSubtitlesLogout()
                                        
        log.info("checkSub: Finished round of subs Search. Go to sleep until the next round.")
        autosub.SEARCHTIME = time.time() - StartTime
        return True
