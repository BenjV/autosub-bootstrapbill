#
# The Autosub scanDisk module
#

import logging
import os
import platform
import re
import time
import unicodedata
from library.requests.packages.chardet import detect
from collections import deque

# Autosub specific modules
import autosub
import autosub.Helpers as Helpers
from autosub.ProcessFilename import ProcessFilename
# Settings
log = logging.getLogger('thelogger')

def WalkError(error):
    log.error('scanDir: Error walking the folders. Message is %s' % error)

def walkDir(path):
    SkipListNL = []
    SkipListEN = []
    SkipListNL = autosub.SKIPSTRINGNL.split(",")
    SkipListEN = autosub.SKIPSTRINGEN.split(",")

    for dirname, dirnames, filenames in os.walk(path, True, WalkError):

        log.debug("scanDisk: directory name: %s" %dirname)
        if re.search('_unpack_', dirname, re.IGNORECASE):
            log.debug("scanDisk: found a unpack directory, skipping.")
            continue

        if autosub.SKIPHIDDENDIRS and os.path.split(dirname)[1].startswith(u'.'):
            continue

        if re.search('_failed_', dirname, re.IGNORECASE):
            log.debug("scanDisk: found a failed directory, skipping.")
            continue

        if re.search('@eaDir', dirname, re.IGNORECASE):
            log.debug("scanDisk: found a Synology indexing directory, skipping.")
            tmpdirs = dirnames[:]
            for dir in tmpdirs:
                dirnames.remove(dir)
            continue

        if re.search("@.*thumb", dirname, re.IGNORECASE):
            log.debug("scanDisk: found a Qnap multimedia thumbnail folder, skipping.")
            continue
        langs = []
        FileDict = {}
        for filename in filenames:
            root,ext = os.path.splitext(filename)
            if ext[1:] in ('avi', 'mkv', 'wmv', 'ts', 'mp4'):
                if re.search('sample', filename):
                    continue
                if not platform.system() == 'Windows':
                    # Get best ascii compatible character for special characters
                    try:
                        if not isinstance(filename, unicode):
                            coding = detect(filename)['encoding']
                            filename = unicode(filename.decode(coding),errors='replace')
                        correctedFilename = ''.join((c for c in unicodedata.normalize('NFD', filename) if unicodedata.category(c) != 'Mn'))
                        if filename != correctedFilename:
                            os.rename(os.path.join(dirname, filename), os.path.join(dirname, correctedFilename))
                            log.info("scanDir: Renamed file %s" % correctedFilename)
                            filename = correctedFilename
                    except:
                        log.error("scanDir: Skipping directory, file %s, %s" % (dirname,filename))
                        continue
                # What subtitle files should we expect?
                langs = []
                NLext = u'.' + autosub.SUBNL  + u'.srt' if autosub.SUBNL  else u'.srt'
                ENext = u'.' + autosub.SUBENG + u'.srt' if autosub.SUBENG else u'.srt'
                ENext = u'.en.srt'if NLext == ENext and autosub.DOWNLOADDUTCH else ENext
                if not os.access(dirname, os.W_OK):
                    log.error('scandisk: No write access to folder: %s' % dirname)
                    continue
                # Check which languages we want to download based on user settings.
                if autosub.DOWNLOADDUTCH:
                    Skipped = False
                    for SkipItem in SkipListNL:
                        if not SkipItem: break
                        if re.search(SkipItem.lower(), filename.lower()):
                            Skipped = True
                            break
                    if Skipped:
                        log.info("scanDir: %s found in %s so skipped for Dutch subs" % (SkipItem, filename))
                    elif os.path.exists(os.path.join(dirname, root + NLext)):
                        Skipped = True
                        log.debug("scanDir: %s skipped because the Dutch subtitle already exists" % filename) 
                    else:
                        # If the Dutch subtitle not skipped and doesn't exist, then add it to the wanted list
                        langs.append(autosub.DUTCH)

                if autosub.DOWNLOADENG or (autosub.FALLBACKTOENG and autosub.DOWNLOADDUTCH and not Skipped):
                    Skipped = False
                    for SkipItem in SkipListEN:
                        if not SkipItem: break
                        if re.search(SkipItem.lower(), filename.lower()):
                            Skipped = True
                            break
                    if Skipped:
                        log.info("scanDir: %s found in %s so skipped for English subs" % (SkipItem, filename))
                    elif os.path.exists(os.path.join(dirname, root + ENext)):
                        log.debug("scanDir: %s skipped because the English subtitle already exists" % filename) 
                    else:
                        # If the English subtitle not skipped and doesn't exist, then add it to the wanted list
                        if not os.path.exists(os.path.join(dirname, root + ENext)):
                            langs.append(autosub.ENGLISH)
                if not langs:
                    # nothing to do for this file
                    continue
                FileDict = ProcessFilename(os.path.splitext(filename)[0], ext)
                if not FileDict:
                    continue
                if not 'title' in FileDict.keys() or not 'season' in FileDict.keys() or not 'episode' in FileDict.keys():
                    continue
                if not FileDict['releasegrp'] and not FileDict['source'] and not FileDict['quality'] and not FileDict['source']:
                    log.error("scanDir: Not enough info in filename: %s" % filename)
                    continue

                log.info("scanDir: %s subtitle(s) for '%s' wanted and added to Wanted Queue" % (langs, filename))
                FileDict['timestamp'] = unicode(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(os.path.join(dirname, filename)))))
                FileDict['langs'] = langs
                FileDict['NLext'] = NLext
                FileDict['ENext'] = ENext
                FileDict['file'] = root
                FileDict['container'] = ext
                FileDict['folder'] = dirname
                FileDict['ImdbId'],FileDict['A7Id'], FileDict['TvdbId'], FileDict['title'] = Helpers.getShowid(FileDict['title'],autosub.ADDIC7EDLOGGED_IN)
                if autosub.Helpers.SkipShow(FileDict['ImdbId'],FileDict['title'], FileDict['season'], FileDict['episode']):
                    continue
                autosub.WANTEDQUEUE.append(FileDict)
    return


class scanDisk():
    """
    Scan the specified path for episodes without Dutch or (if wanted) English subtitles.
    If found add these Dutch or English subtitles to the WANTEDQUEUE.
    """
    def run(self):
        log.info("scanDisk: Starting round of local disk checking at %s" % autosub.ROOTPATH)
        UseAddic= False
        if autosub.ADDIC7EDUSER and autosub.ADDIC7EDPASSWD and autosub.ADDIC7ED:
            try:
                # Sets autosub.DOWNLOADS_A7 and autosub.DOWNLOADS_A7MAX
                # and gives a True response if it's ok to download from a7
                autosub.ADDIC7EDAPI = autosub.Addic7ed.Addic7edAPI()
                autosub.ADDIC7EDLOGGED_IN = autosub.ADDIC7EDAPI.checkCurrentDownloads(logout=False)
            except:
                log.debug("checkSub: Couldn't connect with Addic7ed.com")
        else:
            autosub.ADDIC7EDLOGGED_IN = False
        seriespaths = [x.strip() for x in autosub.ROOTPATH.split(',')]
        for seriespath in seriespaths:

            if not os.path.exists(seriespath):
                log.error("scanDir: Root path %s does not exist, aborting..." % seriespath)
                continue

            try:
                walkDir(seriespath)
            except Exception as error:
                log.error('scanDir: Something went wrong scanning the folders. Message is: %s' % error)
                return False

        log.info("scanDir: Finished round of local disk checking")
        return True