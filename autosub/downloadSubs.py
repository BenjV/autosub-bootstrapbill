# Autosub downloadSubs.py - https://github.com/Donny87/autosub-bootstrapbill
#
# The Autosub downloadSubs module
# Scrapers are used for websites:
# Podnapisi.net, Subscene.com, Undertexter.se, OpenSubtitles
# and addic7ed.com
#
import autosub
import logging

from bs4 import BeautifulSoup
from zipfile import ZipFile
from StringIO import StringIO
import re 
from urlparse import urljoin

import os
import time
import tempfile
import autosub

from autosub.Db import lastDown
from autosub.OpenSubtitles import TimeOut
import autosub.notify as notify
import autosub.Helpers

import xml.etree.cElementTree as ET
import library.requests as requests

# Settings
log = logging.getLogger('thelogger')

def getSoup(url):
    try:
        api = autosub.Helpers.API(url)
        soup = BeautifulSoup(api.resp.read())
        api.close()
        return soup
    except:
        log.error("getSoup: The server returned an error for request %s" % url)
        return None   

def unzip(url):
    # returns a file-like StringIO object    
    try:
        api = autosub.Helpers.API(url)
        tmpfile = StringIO(api.resp.read())
    except:
        log.debug("unzip: Zip file at %s couldn't be retrieved" % url)
        return None     
    try: 
        zipfile = ZipFile(tmpfile)
    except:
        log.debug("unzip: Expected a zip file but got error for link %s" % url)
        log.debug("unzip: %s is likely a dead link, this is known for opensubtitles.org" % url)
        return None

    nameList = zipfile.namelist()
    for name in nameList:
        # sometimes .nfo files are in the zip container
        tmpname = name.lower()
        if tmpname.endswith('srt'):
            subtitleFile = StringIO(zipfile.open(name).read())
            log.debug("unzip: Retrieving zip file for %s was succesful" % url )
            return subtitleFile
        else: 
            log.debug("unzip: No subtitle files was found in the zip archive for %s" % url)
            log.debug("unzip: Subtitle with different extention than .srt?")
            return None  

def openSubtitles(DownloadPage):

    log.debug("OpenSubtitles: DownloadPage: %s" % DownloadPage)

    try:
        TimeOut()
        RequestResult = autosub.OPENSUBTTITLESSESSION.get(DownloadPage, timeout=10)
        autosub.OPENSUBTTITLESSESSION.headers.update({'referer': DownloadPage})
    except:
        log.debug('openSubtitles: Could not connect to OpenSubtitles.')
        return None
    if 'text/xml' not in RequestResult.headers['Content-Type']:
        log.error('openSubtitles: OpenSubtitles responded with an error')
        return None
    try:
        root = ET.fromstring(RequestResult.content)
    except:
        log.debug('openSubtitles: Serie with IMDB ID %s could not be found on OpenSubtitles.' %ImdbId)
        return None
    try:
        DownloadId = root.find('.//SubBrowse/Subtitle/SubtitleFile/File').get('ID')
    except:
        log.debug('openSubtitles: Could not get the download link from OpenSubtitles')
        return None
    try:
        DownloadUrl = autosub.OPENSUBTITLESDL + DownloadId
        TimeOut()
        RequestResult = autosub.OPENSUBTTITLESSESSION.get( DownloadUrl, timeout=10)
        autosub.OPENSUBTTITLESSESSION.headers.update({'referer': DownloadUrl})
    except:
        log.debug('openSubtitles: Could not connect to Opensubtitles.org.')
        return None
    if RequestResult.headers['Content-Type'] == 'text/html':
        log.error('openSubtitles: Expected srt file but got HTML; report this!')
        log.debug("openSubtitles: Response content: %s" % r.content)
        return None
    return StringIO(RequestResult.content)

def undertexter(subSeekerLink):
    engSub = 'http://www.engsub.net/getsub.php?id='    
    soup = getSoup(subSeekerLink)
    if soup:
        tag = soup.find('iframe', src=True)
        link = tag['src'].strip('/')     
    else:
        log.error("Undertexter: Failed to extract download link using SubtitleSeekers's link")        
        return None
    try:
        zipUrl = engSub + link.split('/')[3].encode('utf8')
    except:
        log.error("Undertexter: Something went wrong with parsing the downloadlink")        
        return None
    subtitleFile = unzip(zipUrl)
    return subtitleFile

def podnapisi(subSeekerLink):
    baseLink = 'http://www.podnapisi.net/'
    soup = getSoup(subSeekerLink)    
    if soup:
        linkToPodnapisi = soup.select('p > a[href]')[0]['href'].strip('/')
    else:
        log.error("Podnapisi: Failed to find the redirect link using SubtitleSeekers's link")        
        return None
    if baseLink in linkToPodnapisi:
        soup = getSoup(linkToPodnapisi)
    else:
        log.error("Podnapisi: Failed to find the Podnapisi page.")
        return None
    if soup:
        downloadLink = soup.find('form', class_='form-inline download-form').get('action')
    else:
        log.error("Podnapisi: Failed to find the download link on Podnapisi page")     
        return None
    zipUrl = urljoin(baseLink,downloadLink.encode('utf8'))
    subtitleFile = unzip(zipUrl)
    return subtitleFile

def subscene(subSeekerLink):
    baseLink = 'http://subscene.com/'
    soup = getSoup(subSeekerLink)
    if soup:
        linkToSubscene = soup.select('p > a[href]')[0]['href'].strip('/')
    else:
        log.error("Subscene: Failed to find the redirect link using SubtitleSeekers's link")        
        return None
    if baseLink in linkToSubscene :
        soup = getSoup(linkToSubscene)
    else:
        log.error("subscene: Failed to find the subscene page.")
        return None
    if soup:
        downloadLink = soup.select('div.download > a[href]')[0]['href'].strip('/')
    else:
        log.error("Subscene: Failed to find the download link on Subscene.com")        
        return None
    zipUrl = urljoin(baseLink,downloadLink.encode('utf8'))
    subtitleFile = unzip(zipUrl)
    return subtitleFile               

def addic7ed(url):
    subtitleFile = autosub.ADDIC7EDAPI.download(url)
    if subtitleFile:
        autosub.DOWNLOADS_A7 += 1
        log.debug("addic7ed: Your current Addic7ed download count is: %s" % autosub.DOWNLOADS_A7)
        return StringIO(subtitleFile)
    return None

def DownloadSub(allResults, a7Response, downloadItem):    
    
    log.debug("downloadSubs: Starting DownloadSub function")    
    
    if not 'destinationFileLocationOnDisk' in downloadItem.keys():
        log.error("downloadSub: No locationOnDisk found at downloadItem, skipping")
        return False
    
    log.debug("downloadSubs: Download dict seems OK. Dumping it for debug: %r" % downloadItem) 
    destsrt = downloadItem['destinationFileLocationOnDisk']
    destdir = os.path.split(destsrt)[0]
    if not os.path.exists(destdir):
        log.debug("checkSubs: no destination directory %s" %destdir)
        return False
    elif not os.path.lexists(destdir):
        log.debug("checkSubs: no destination directory %s" %destdir)
        return False        
    
    HIfallback = {}
    fileStringIO = None
        
    for result in allResults:   
        url = result['url']
        release = result['releasename']
        website = result['website']             
       
        log.debug("downloadSubs: Trying to download subtitle from %s using this link %s" % (website,url))      

        if website == 'undertexter.se':
            log.debug("downloadSubs: Scraper for Undertexter.se is chosen for subtitle %s" % destsrt)
            fileStringIO = undertexter(url) 
        elif website == 'subscene.com':    
            log.debug("downloadSubs: Scraper for Subscene.com is chosen for subtitle %s" % destsrt)
            fileStringIO = subscene(url)
        elif website == 'podnapisi.net':
            log.debug("downloadSubs: Scraper for Podnapisi.net is chosen for subtitle %s" % destsrt)
            fileStringIO = podnapisi(url)
        elif website == 'opensubtitles.org':
            log.debug("downloadSubs: Scraper for opensubtitles.org is chosen for subtitle %s" % destsrt)
            fileStringIO = openSubtitles(url)
            time.sleep(6)
        elif website == 'addic7ed.com' and a7Response:
            log.debug("downloadSubs: Scraper for Addic7ed.com is chosen for subtitle %s" % destsrt)
            if result['HI']:
                if not HIfallback:
                    log.debug("downloadSubs: Addic7ed HI version: store as fallback")
                    HIfallback = result            
                continue
            fileStringIO = addic7ed(url)   
        else:
            log.error("downloadSubs: %s is not recognized. Something went wrong!" % website)

        if fileStringIO:
            log.debug("downloadSubs: Subtitle is downloading from %s" % website)      
            break
   
        log.debug("downloadSubs: Trying to download another subtitle for this episode")
    
    
    if not fileStringIO:
        if HIfallback:
            log.debug("downloadSubs: Downloading HI subtitle as fallback")
            fileStringIO = addic7ed(url)
            release = HIfallback['releasename']
            website = HIfallback['website']
        else: return False
    if not fileStringIO: 
        log.debug("downloadSubs: No suitable subtitle was found")
        return False
    
    #Lets first download the subtitle to a tempfile and then write it to the destination
    tmpfile = tempfile.TemporaryFile('w+b')
        
    try:
        tmpfile.write(fileStringIO.getvalue())
        tmpfile.write('\n') #If subtitle has some footer which doesn't have a line feed >.>
        tmpfile.seek(0) #Return to the start of the file
    except:
        log.error("downloadSubs: Error while downloading subtitle %s. Subtitle might be corrupt %s." % (destsrt, website))

    try:
        log.debug("downloadSubs: Trying to save the subtitle to the filesystem")
        open(destsrt, 'wb').write(tmpfile.read())
        tmpfile.close()
    except IOError:
        log.error("downloadSubs: Could not write subtitle file. Permission denied? Enough diskspace?")
        tmpfile.close()
        return False
        
    log.info("downloadSubs: DOWNLOADED: %s" % destsrt)
        
    downloadItem['subtitle'] = "%s downloaded from %s" % (release,website)
    downloadItem['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
    
    lastDown().setlastDown(dict = downloadItem)
    # Send notification        
    notify.notify(downloadItem['downlang'], destsrt, downloadItem["originalFileLocationOnDisk"], website)
    if autosub.POSTPROCESSCMD:
        postprocesscmdconstructed = autosub.POSTPROCESSCMD + ' "' + downloadItem["destinationFileLocationOnDisk"] + '" "' + downloadItem["originalFileLocationOnDisk"] + '" "' + downloadItem["downlang"] + '" "' + downloadItem["title"] + '" "' + downloadItem["season"] + '" "' + downloadItem["episode"] + '" '
        log.debug("downloadSubs: Postprocess: running %s" % postprocesscmdconstructed)
        log.info("downloadSubs: Running PostProcess")
        postprocessoutput, postprocesserr = autosub.Helpers.RunCmd(postprocesscmdconstructed)
        log.debug("downloadSubs: PostProcess Output:% s" % postprocessoutput)
        if postprocesserr:
            log.error("downloadSubs: PostProcess: %s" % postprocesserr)
            #log.debug("downloadSubs: PostProcess Output:% s" % postprocessoutput)
    
    log.debug('downloadSubs: Finished for %s' % downloadItem["originalFileLocationOnDisk"])
    return True