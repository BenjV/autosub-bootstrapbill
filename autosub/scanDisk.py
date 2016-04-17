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
                if re.search('sample', filename): continue
                
                if autosub.WEBDL == 'None':
                    if re.search('web-dl', filename.lower()): 
                        log.debug("scanDisk: WEB-DL is set to 'None', skipping %s" %filename)
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
                        log.error("scanDir: Skipping directory %s" % dirname)
                        log.error("scanDir: Skipping file %s" % filename)
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
                    # If the Dutch subtitle doesn't exist, then add it to the wanted list.
                    if not os.path.exists(os.path.join(dirname, srtfilenl)):
                        lang.append(autosub.DUTCH)

                if autosub.DOWNLOADENG:
                    # If the English subtitle doesn't exist, then add it to the wanted list.
                    if not os.path.exists(os.path.join(dirname, srtfileeng)):
                        if autosub.WEBDL == 'DutchOnly' and re.search('web-dl', filename.lower()):
                            log.debug("scanDisk: WEB-DL is set to 'Dutch Only', not adding English as wanted for %s" %filename)
                        else:
                            lang.append(autosub.ENGLISH)

                if (autosub.FALLBACKTOENG and autosub.DOWNLOADDUTCH) and not autosub.DOWNLOADENG:
                    # If the Dutch and English subtitles do not exist, then add English to the wanted list.
                    if not os.path.exists(os.path.join(dirname, srtfilenl)) and not os.path.exists(os.path.join(dirname, srtfileeng)):
                        if autosub.WEBDL == 'DutchOnly' and re.search('web-dl', filename.lower()):
                            log.debug("scanDisk: WEB-DL is set to 'Dutch Only', not adding English as wanted for %s" %filename)
                        else:
                            lang.append(autosub.ENGLISH)

                if not lang:
                    # autosub.WANTEDQUEUE empty
                    continue

                log.debug("scanDir: File %s is missing subtitle(s): %s" % (filename, ', '.join(map(str,lang))))
                filenameResults = ProcessFilename(os.path.splitext(filename)[0], ext)

                if 'title' in filenameResults.keys():
                    if 'season' in filenameResults.keys():
                        if 'episode' in filenameResults.keys():
                            title = filenameResults['title']
                            season = filenameResults['season']
                            episode = filenameResults['episode']

                            if not filenameResults['releasegrp'] and not filenameResults['source'] and not filenameResults['quality'] and not filenameResults['source']:
                                continue

                            if autosub.Helpers.SkipShow(title, season, episode) == True:
                                log.debug("scanDir: SkipShow returned True")
                                log.info("scanDir: Skipping %s - Season %s Episode %s" % (title, season, episode))
                                continue
                            if len(lang) == 1:
                                log.info("scanDir: %s subtitle wanted for %s and added to wantedQueue" % (lang[0], filename))
                            else:
                                log.info("scanDir: %s subtitles wanted for %s and added to wantedQueue" % (' and '.join(map(str,lang)), filename))
                            filenameResults['originalFileLocationOnDisk'] = os.path.join(dirname, filename)
                            filenameResults['timestamp'] = unicode(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(filenameResults['originalFileLocationOnDisk']))))
                            filenameResults['lang'] = lang
                            filenameResults['container'] = ext
                            filenameResults['ImdbId'],filenameResults['A7Id'], filenameResults['title'] = Helpers.getShowid(filenameResults['title'],autosub.ADDIC7EDLOGGED_IN)
                            autosub.WANTEDQUEUE.append(filenameResults)

                        else:
                            log.error("scanDir: Could not process the filename properly filename: %s" % filename)
                            continue
                    else:
                        log.error("scanDir: Could not process the filename properly filename: %s" % filename)
                        continue
                else:
                    log.error("scanDir: Could not process the filename properly filename: %s" % filename)
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
        autosub.ADDIC7EDLOGGED_IN = True
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