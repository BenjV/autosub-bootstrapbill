#
# Autosub getSubLinks.py - https://github.com/Donny87/autosub-bootstrapbill
#
# The getSubLinks module
#

import logging
import time
from xml.dom import minidom
try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET
import library.requests as requests
from operator import itemgetter
from bs4 import BeautifulSoup
import autosub.Helpers
from autosub.ProcessFilename import ProcessFilename
import autosub.Addic7ed
# Settings
log = logging.getLogger('thelogger')


def SubtitleSeeker(ImdbId, lang, Wanted, sourceWebsites):
    # Get the scored list for all SubtitleSeeker hits

    SearchUrl = "%s&imdb=%s&season=%s&episode=%s&language=%s&return_type=json" % (autosub.API, ImdbId, Wanted['season'], Wanted['episode'], lang)
    log.info('getSubLinks: SubtitleSeeker request URL: %s' % SearchUrl)
    if autosub.Helpers.checkAPICallsSubSeeker(use=True):
        try:
            SubseekerSession = requests.session()
            Result = SubseekerSession.get(SearchUrl).json()
            SubseekerSession.close()
        except:
            log.error("getSubLink: The server returned an error for request %s" % getSubLinkUrl)
            return
    else:
        log.error("API: out of api calls for SubtitleSeeker.com")
        return
    scoreList = []
    if int(Result['results']['total_matches']) == 0:
        return

    for Item in Result['results']['items']:
        if (Item['site'].lower() == u'podnapisi.net' and (autosub.PODNAPISILANG == lang or autosub.PODNAPISILANG == 'Both')) or \
           (Item['site'].lower() == u'subscene.com' and (autosub.SUBSCENELANG == lang or  autosub.SUBSCENELANG == 'Both')):
            Item['release'] = Item['release'][:-4].lower() if Item['release'].endswith(".srt") else Item['release'].lower()
            NameDict = ProcessFilename(Item['release'],Wanted['container'])
            score = autosub.Helpers.scoreMatch(NameDict, Item['release'], Wanted['quality'], Wanted['releasegrp'], Wanted['source'], Wanted['codec'])
            if score >= autosub.MINMATCHSCORE:
                scoreList.append({'score':score, 'url':Item['url'] , 'website':Item['site'].lower(), 'releaseName':Item['release'],'SubCodec':''})
    return scoreList


def Addic7ed(a7ID , language, releaseDetails):

    title      = releaseDetails['title']      if 'title'      in releaseDetails.keys() else None
    season     = releaseDetails['season']     if 'season'     in releaseDetails.keys() else None
    episode    = releaseDetails['episode']    if 'episode'    in releaseDetails.keys() else None
    quality    = releaseDetails['quality']    if 'quality'    in releaseDetails.keys() else None
    releasegrp = releaseDetails['releasegrp'] if 'releasegrp' in releaseDetails.keys() else None
    source     = releaseDetails['source']     if 'source'     in releaseDetails.keys() else None
    codec      = releaseDetails['codec']      if 'codec'      in releaseDetails.keys() else None

    langs = u''
    if 'English' in language:
        langs = '|1|'
    else:
        langs = '|17|'
    SearchUrl = '/ajax_loadShow.php?show=' + a7ID + '&season=' +season.lstrip('0') + '&langs=' + langs + '&hd=0&hi=0'
    log.info('getSubLinks: Addic7ed search URL: %s' % u'http://www.addic7ed.com' + SearchUrl)

    Result = autosub.ADDIC7EDAPI.get(SearchUrl)
    if Result:
        try:
            soup = BeautifulSoup(Result)
        except:
            log.debug("getSubLinks: Addic7ed no soup exception.")
            return None
    else:
       return None

    scoreList = []

    for row in soup('tr', class_='epeven completed'):
        cells = row('td')
        #Check if line is intact
        if not len(cells) == 11:
            continue
        # filter on Completed, wanted language and episode
        if cells[5].string != 'Completed':
            continue
        if not unicode(cells[3].string) == language:
            continue
        if not unicode(cells[1].string) == episode and not unicode(cells[1].string) == unicode(int(episode)):
            continue
        # use ASCII codec and put in lower case
        details = unicode(cells[4].string).encode('utf-8')
        details = details.lower()
        HD = True if cells[8].string != None else False
        downloadUrl = cells[9].a['href'].encode('utf-8')
        hearingImpaired = True if bool(cells[6].string) else False
        if hearingImpaired:
            releasename = autosub.Addic7ed.makeReleaseName(details, title, season, episode, HI=True)
        else:
            releasename = autosub.Addic7ed.makeReleaseName(details, title, season, episode)

        # Return is a list of possible releases that match
        versionDicts = autosub.Addic7ed.ReconstructRelease(details, HD)
        if not versionDicts:
            continue
        for version in versionDicts:
            score = autosub.Helpers.scoreMatch(version, details, quality, releasegrp, source, codec)
            if score >= autosub.MINMATCHSCORE:
                releaseDict = {'score':score , 'releaseName':releasename, 'website':'addic7ed.com' , 'url':downloadUrl , 'HI':hearingImpaired}
                scoreList.append(releaseDict)
    return scoreList


def Opensubtitles(ImdbId, language, Wanted):
    if not Wanted:
        return None
    Data = {}
    if 'English' in language:
        Data['sublanguageid'] = 'eng'
    else: 
        Data['sublanguageid']= 'dut'
    Data['imdbid' ] = ImdbId
    Data['season']  = Wanted['season']
    Data['episode'] = Wanted['episode']
    time.sleep(6)
    try:
        Subs = autosub.OPENSUBTITLESSERVER.SearchSubtitles(autosub.OPENSUBTITLESTOKEN, [Data])
    except:
        log.debug('Opensubtitles: Error from Opensubtitles search API')
        return None

    if Subs['status'] != '200 OK':
        log.info('Opensubtitles: No subs found for %s on Opensubtitles.' % Wanted['releaseName'])
        return
    scoreList = []
    for Sub in Subs['data']:
        if int(Sub['SubBad']) > '0' or int(Sub['SubHearingImpaired']) > 0 :
            continue
        NameDict = ProcessFilename(Sub['MovieReleaseName'],Wanted['container'])
        SubId = Sub['IDSubtitleFile']
        LangCode = Sub['ISO639']
        if not NameDict or not SubId or not LangCode: continue
         # here we score the subtitle and if it's high enough we add it to the list 
        score = autosub.Helpers.scoreMatch(NameDict, Sub['MovieReleaseName'], Wanted['quality'], Wanted['releasegrp'], Wanted['source'], Wanted['codec'])
        if score >= autosub.MINMATCHSCORE:
            scoreList.append({'score':score, 'url':SubId , 'website':'opensubtitles.org','releaseName':Sub['MovieReleaseName'], 'SubCodec':Sub['SubEncoding']})
        else:
            log.debug('Opensubtitles: %s has scorematch %s skipping it.' % (Sub['MovieReleaseName'],score))
    return scoreList



def getSubLinks(ImdbId, a7_id, lang, releaseDetails):
    """
    Return all the hits that reach minmatchscore, sorted with the best at the top of the list
    Each element had the downloadlink, score, releasename, and source website)
    Matching is based on the provided release details.

    Keyword arguments:
    ImdbId -- The IMDB id of the show
    a7_id  -- The Addic7ed id of the show
    lang -- Language of the wanted subtitle, Dutch or English
    releaseDetails -- Dict containing the quality, releasegrp, source season and episode.
    """
    log.debug("getSubLinks: Show ID: %s - Addic7ed ID: %s - Language: %s - Release Details: %s" % (ImdbId,a7_id,lang,releaseDetails))
    sourceWebsites, scoreListSubSeeker, scoreListAddic7ed, scoreListOpensubtitles, fullScoreList  = [],[],[],[],[]
    if autosub.PODNAPISILANG == lang or autosub.PODNAPISILANG == 'Both':
        sourceWebsites.append('podnapisi.net')
    if autosub.SUBSCENELANG == lang or autosub.SUBSCENELANG == 'Both':
        sourceWebsites.append('subscene.com')

    # If one of his websites choosen call subtitleseeker
    if len(sourceWebsites) > 0:
        scoreListSubSeeker = SubtitleSeeker(ImdbId, lang, releaseDetails, sourceWebsites)
        log.debug("getSubLinks: dump scorelist: %s" % scoreListSubSeeker)

    # Use Addic7ed if selected
    if (autosub.ADDIC7EDLANG == lang or autosub.ADDIC7EDLANG == 'Both') and a7_id:
        scoreListAddic7ed = Addic7ed(a7_id, lang, releaseDetails)

    # Use OpenSubtitles if selected
    if (autosub.OPENSUBTITLESLANG == lang or autosub.OPENSUBTITLESLANG == 'Both') and autosub.OPENSUBTITLESTOKEN:
        scoreListOpensubtitles = Opensubtitles(ImdbId, lang, releaseDetails)

    for list in [scoreListSubSeeker, scoreListAddic7ed, scoreListOpensubtitles]:
        if list: fullScoreList.extend(list)

    # Done comparing all the results, lets sort them and return the highest result
    # If there are results with the same score, the download links which comes last (anti-alphabetically) will be returned
    # Also check if the result match the minimal score
    sortedscorelist = sorted(fullScoreList, key=itemgetter('score', 'website'), reverse=True)

    if len(sortedscorelist) > 0:
        return sortedscorelist

    return None