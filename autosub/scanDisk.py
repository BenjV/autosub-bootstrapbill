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

# Autosub specific modules
import autosub
import autosub.Helpers as Helpers
from autosub.ProcessFilename import ProcessFilename
# Settings
log = logging.getLogger('thelogger')

def walkDir(path):
    SkipListNL = []
    SkipListEN = []
    SkipListNL = autosub.SKIPSTRINGNL.split(",")
    SkipListEN = autosub.SKIPSTRINGEN.split(",")

    for dirname, dirnames, filenames in os.walk(path):

        log.debug("scanDisk: directory name: %s" %dirname)
        if re.search('_unpack_', dirname, re.IGNORECASE):
            log.debug("scanDisk: found a unpack directory, skipping")
            continue

        if autosub.SKIPHIDDENDIRS and os.path.split(dirname)[1].startswith(u'.'):
            continue

        if re.search('_failed_', dirname, re.IGNORECASE):
            log.debug("scanDisk: found a failed directory, skipping")
            continue

        if re.search('@eaDir', dirname, re.IGNORECASE):
            log.debug("scanDisk: found a Synology indexing directory, skipping this folder and all subfolders.")
            tmpdirs = dirnames[:]
            for dir in tmpdirs:
                dirnames.remove(dir)
            continue

        if re.search("@.*thumb", dirname, re.IGNORECASE):
            # Ingnore QNAP multimedia thumbnail folders
            continue

        for filename in filenames:
            splitname = filename.split(".")
            ext = os.path.splitext(filename)[1]
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
                lang=[]
                #Check what the Dutch subtitle would be.
                if autosub.SUBNL != "":
                    srtfilenl = os.path.splitext(filename)[0] + u"." + autosub.SUBNL + u".srt"
                else:
                    srtfilenl = os.path.splitext(filename)[0] + u".srt"
                #Check what the English subtitle would be.
                if autosub.SUBENG == "":
                    # Check for overlapping names
                    if autosub.SUBNL != "" or not autosub.DOWNLOADDUTCH:
                        srtfileeng = os.path.splitext(filename)[0] + u".srt"
                    # Hardcoded fallback
                    else:
                        srtfileeng = os.path.splitext(filename)[0] + u".en.srt"
                else:
                    srtfileeng = os.path.splitext(filename)[0] + u"." + autosub.SUBENG + u".srt"

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
                    elif os.path.exists(os.path.join(dirname, srtfilenl)):
                        log.debug("scanDir: %s skipped because the Dutch subtitle already exists" % filename) 
                    else:
                        # If the Dutch subtitle not skipped and doesn't exist, then add it to the wanted list
                        lang.append(autosub.DUTCH)

                if autosub.DOWNLOADENG or (autosub.FALLBACKTOENG and autosub.DOWNLOADDUTCH and not Skipped):
                    Skipped = False
                    for SkipItem in SkipListEN:
                        if not SkipItem: break
                        if re.search(SkipItem.lower(), filename.lower()):
                            Skipped = True
                            break
                    if Skipped:
                        log.info("scanDir: %s found in %s so skipped for English subs" % (SkipItem, filename))
                    elif os.path.exists(os.path.join(dirname, srtfilenl)):
                        log.debug("scanDir: %s skipped because the English subtitle already exists" % filename) 
                    else:
                        # If the Dutch subtitle not skipped and doesn't exist, then add it to the wanted list
                        if not os.path.exists(os.path.join(dirname, srtfileeng)):
                            if autosub.DOWNLOADENG or ( autosub.FALLBACKTOENG and autosub.DOWNLOADDUTCH ):
                                lang.append(autosub.ENGLISH)
                if not lang:
                    # nothing to do for this file
                    continue

                FileDict = ProcessFilename(os.path.splitext(filename)[0], ext)
                if 'title' in FileDict.keys() and 'season' in FileDict.keys() and 'episode' in FileDict.keys():
                    if not FileDict['releasegrp'] and not FileDict['source'] and not FileDict['quality'] and not FileDict['source']:
                        log.error("scanDir: Not enough info in filename: %s" % filename)
                        continue
                    if autosub.Helpers.SkipShow(FileDict['title'], FileDict['season'], FileDict['episode']) == True:
                        log.info("scanDir: Skipping %s - Season %s Episode %s" % (FileDict['title'], FileDict['season'], FileDict['episode']))
                        continue
                    if len(lang) == 1:
                        log.info("scanDir: %s subtitle wanted for %s and added to wantedQueue" % (lang[0], filename))
                    else:
                        log.info("scanDir: %s subtitles wanted for %s and added to wantedQueue" % (' and '.join(map(str,lang)), filename))
                    FileDict['originalFileLocationOnDisk'] = os.path.join(dirname, filename)
                    FileDict['timestamp'] = unicode(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(FileDict['originalFileLocationOnDisk']))))
                    FileDict['lang'] = lang
                    FileDict['container'] = ext
                    FileDict['ImdbId'],FileDict['A7Id'], FileDict['TvdbId'], FileDict['title'] = Helpers.getShowid(FileDict['title'],autosub.ADDIC7EDLOGGED_IN)
                    autosub.WANTEDQUEUE.append(FileDict)
                else:
                    log.error("scanDir: Not enough info in filename: %s" % filename)
                    continue

class scanDisk():
    """
    Scan the specified path for episodes without Dutch or (if wanted) English subtitles.
    If found add these Dutch or English subtitles to the WANTEDQUEUE.
    """
    def run(self):
        log.info("scanDisk: Starting round of local disk checking at %s" % autosub.ROOTPATH)
        UseAddic= False
        if autosub.ADDIC7EDUSER and autosub.ADDIC7EDPASSWD and autosub.ADDIC7EDLANG != 'None':
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

            # Temporary to try and figure out the problem
            try:
                walkDir(seriespath)
            except:
                log.error("scanDir: Something went wrong when traversing directory %s" % seriespath)
                return False

        log.info("scanDir: Finished round of local disk checking")
        return True