#
# The Autosub downloadSubs module
# Scrapers are used for websites:
# Podnapisi.net, Subscene.com, Undertexter.se, OpenSubtitles
# and addic7ed.com
#
import autosub
import logging
from autosub.OpenSubtitles import OpenSubtitlesNoOp
from bs4 import BeautifulSoup
import zipfile
from StringIO import StringIO
import re 
from urlparse import urljoin

import os
import time
import tempfile
import autosub

from autosub.Db import lastDown
import autosub.notify as notify
import autosub.Helpers

try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET
import library.requests as requests
import library.requests.packages.chardet as chardet
import xmlrpclib, io, gzip
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
        Session = requests.session()
        Result = Session.get(url)
    except:
        log.debug("unzip: Zip file at %s couldn't be retrieved" % url)
        return None
    try: 
       zip =  zipfile.ZipFile(io.BytesIO(Result.content))
    except Exception as error:
        log.debug("unzip: Expected a zip file but got error for link %s" % url)
        log.debug("unzip: %s is likely a dead link" % url)
        return None
    nameList = zip.namelist()
    for name in nameList:
        # sometimes .nfo files are in the zip container
        if name.lower().endswith('srt'):
            try:
                Codec = chardet.detect(zip.read(name))['encoding']
                fpr = io.TextIOWrapper(zip.open(name),encoding = Codec,newline='')
                SubData = fpr.read()
                fpr.close()
                if SubData:
                    return SubData
            except Exception as error:
                pass
    log.debug("unzip: No subtitle files was found in the zip archive for %s" % url)
    return None
  

def openSubtitles(SubId, SubCodec):

    log.debug("OpenSubtitles: Download subtitle: %s" % SubId)
    time.sleep(6)
    if not OpenSubtitlesNoOp():
        return None
    try:
        Result = autosub.OPENSUBTITLESSERVER.DownloadSubtitles(autosub.OPENSUBTITLESTOKEN, [SubId])
    except:
        autosub.OPENSUBTITLESTOKEN = None
        log.error('Opensubtitles: Error from Opensubtitles download API')
        return   

    if Result['status'] == '200 OK':
        CompressedData = Result['data'][0]['data'].decode('base64')
        if not CompressedData:
            log.debug('DownloadSub: No data returned from DownloadSubtitles API call. Skipping this one.')
            return None
        SubDataBytes = gzip.GzipFile(fileobj=io.BytesIO(CompressedData)).read()
        # Opensubtitles makes no difference in UTF-8 and UTF8-SIG so we check with chardet the correct encoding
        # also if Opensubtile does not know the encoding
        if SubCodec == 'UTF-8' or SubCodec == 'Unknown' or not SubCodec:
            SubCodec = chardet.detect(SubDataBytes)['encoding']
        if SubCodec:
            SubData = SubDataBytes.decode(SubCodec)
            return(SubData)
        else:
            log.debug('Opensubtitles: Could not determine the codec from the sub so skipping it.')
            return None
    else:
        log.debug('Opensubtitles: Error from Opensubtitles downloadsubs API. Message : %s' % Result['status'])
        return None



def subseeker(subSeekerLink,website):

    baselink = 'http://www.' + website 
    Session = requests.session()
    SubLinkPage = Session.get(subSeekerLink)

    try:
        SubLink = re.findall('Download : <a href="(.*?)"', SubLinkPage.text)[0]
    except Exception as error:
        log.error("subseeker: Failed to find the redirect link on SubtitleSeekers")        
        return None
    try:
        Result= requests.get(SubLink)
    except:
        log.debug('subseeker: Link from SubtitleSeeker not found, maybe outdated. Link is: %s' % subSeekerLink)
        return None

    if Result.status_code > 399 or not Result.text:
        return False
    Result.encoding = 'utf-8'
    try:
        if website == 'podnapisi.net':
            try:
                DownLoadLink = re.findall('form-inline download-form\" action=(.*?)>', Result.text)[0]
            except:
                log.error("subseeker: Could not find the subseeker link on the podnapisi website.") 
                return None
            DownLoadLink = urljoin(baselink, DownLoadLink) if DownLoadLink else None
        elif website =='subscene.com':
            try:
                DownLoadLink = re.findall('<a href=\"/subtitle/download(.*?)\"', Result.text)[0]
            except:
                log.error("subseeker: Could not find the subseeker link on the subscene website.") 
                return None
            DownLoadLink = urljoin(baselink + '/subtitle/download', DownLoadLink) if DownLoadLink else None
        if not DownLoadLink:
            log.error('downloadsubs: Could not find the downloadlink %s on %s' % (DownLoadLink, website))
        try:
            SubData = unzip(DownLoadLink)
            return(SubData)
        except:
            log.error('downloadsubs:Problem unzipping file %s from %s.' % (DownLoadLink,website))
        return None
    except:
        log.error('downloadsubs:Problem downloading file %s from %s.' % (DownLoadLink,website))
        return None

def addic7ed(url):
    SubData = autosub.ADDIC7EDAPI.download(url)
    if SubData:
        autosub.DOWNLOADS_A7 += 1
        log.debug("addic7ed: Your current Addic7ed download count is: %s" % autosub.DOWNLOADS_A7)
        return SubData
    return None

def WriteSubFile(SubData,SubFileOnDisk):
# this routine tries to download the sub and check if it is a correct sub
# this is done by checking the first two line for the correct subtitles format
    if SubData[0] == u'1':
        StartPos = 3 if SubData[1] == u'\r' else 2
        if re.match("\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}",SubData[StartPos:StartPos + 29]):
            try:
                log.debug("downloadSubs: Saving the subtitle file %s to the filesystem." % SubFileOnDisk)
                fp = io.open(SubFileOnDisk, 'wb')
                fp.write(SubData.encode('utf-8'))
                fp.close()
                return True
            except Exception as error:
                log.error('WriteSubFile: Problem writing subfile. Message is: %s' %error)
                pass
        else:
            log.debug('WriteSubFile: File is not a valid subtitle format. skipping it.')
    return False  

def DownloadSub(Wanted,SubList):    
    
    log.debug("downloadSubs: Starting DownloadSub function")    
   
    log.debug("downloadSubs: Download dict seems OK. Dumping it for debug: %r" % Wanted) 
    destsrt = Wanted['destinationFileLocationOnDisk']
    destdir = os.path.split(destsrt)[0]
    if not os.path.exists(destdir):
        log.debug("checkSubs: no destination directory %s" %destdir)
        return False
    elif not os.path.exists(destdir):
        log.debug("checkSubs: no destination directory %s" %destdir)
        return False        

    SubData = None
    Downloaded = False 
    for Sub in SubList:   
        log.debug("downloadSubs: Trying to download subtitle from %s using this link %s" % (Sub['website'],Sub['url']))      

        if Sub['website'] == 'opensubtitles.org':
            log.debug("downloadSubs: Api for opensubtitles.org is chosen for subtitle %s" % destsrt)
            SubData = openSubtitles(Sub['url'],Sub['SubCodec'])
        elif Sub['website'] == 'addic7ed.com':
            log.debug("downloadSubs: Scraper for Addic7ed.com is chosen for subtitle %s" % destsrt)
            SubData = autosub.ADDIC7EDAPI.download(Sub['url'])
        else:
            log.debug("downloadSubs: Scraper for %s is chosen for subtitle %s" % (Sub['website'],destsrt))
            SubData = subseeker(Sub['url'],Sub['website'])
        if SubData:
            if WriteSubFile(SubData,destsrt):
                Downloaded = True           
                break
    if Downloaded:
        log.info("downloadSubs: Subtitle %s is downloaded from %s" % (Sub['releaseName'],Sub['website']))
    else:
        log.error("downloadSubs: Could not download any correct subtitle file for %s" % Wanted['originalFileLocationOnDisk'])
        return False   
    Wanted['subtitle'] = "%s downloaded from %s" % (Sub['releaseName'],Sub['website'])
    Wanted['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.path.getmtime(destsrt)))

    lastDown().setlastDown(dict = Wanted)
    # Send notification 

    notify.notify(Wanted['downlang'], destsrt, Wanted["originalFileLocationOnDisk"], Sub['website'])
    if autosub.POSTPROCESSCMD:
        postprocesscmdconstructed = autosub.POSTPROCESSCMD + ' "' + Wanted['destinationFileLocationOnDisk'] + '" "' + Wanted["originalFileLocationOnDisk"] + '" "' + Wanted["downlang"] + '" "' + Wanted["title"] + '" "' + Wanted["season"] + '" "' + Wanted["episode"] + '" '
        log.debug("downloadSubs: Postprocess: running %s" % postprocesscmdconstructed)
        log.info("downloadSubs: Running PostProcess")
        postprocessoutput, postprocesserr = autosub.Helpers.RunCmd(postprocesscmdconstructed)
        log.debug("downloadSubs: PostProcess Output:% s" % postprocessoutput)
        if postprocesserr:
            log.error("downloadSubs: PostProcess: %s" % postprocesserr)
            #log.debug("downloadSubs: PostProcess Output:% s" % postprocessoutput)
    
    log.debug('downloadSubs: Finished for %s' % Wanted["originalFileLocationOnDisk"])
    return True