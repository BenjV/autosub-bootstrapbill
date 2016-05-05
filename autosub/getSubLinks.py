#
# The getSubLinks module
#

import logging
import time,sys
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
from autosub.OpenSubtitles import OpenSubtitlesNoOp
import autosub.Addic7ed
# Settings
log = logging.getLogger('thelogger')


def SubtitleSeeker(lang, Wanted, sourceWebsites):
    # Get the scored list for all SubtitleSeeker hits
    scoreList = []
    SearchUrl = "%s&imdb=%s&season=%s&episode=%s&language=%s&return_type=json" % (autosub.API, Wanted['ImdbId'], Wanted['season'], Wanted['episode'], lang)
    log.debug('getSubLinks: SubtitleSeeker request URL: %s' % SearchUrl)
    if autosub.Helpers.checkAPICallsSubSeeker(use=True):
        try:
            SubseekerSession = requests.session()
            Result = SubseekerSession.get(SearchUrl).json()
            SubseekerSession.close()
        except Exception as error:
            log.error("getSubLink: The server returned an error for request %s. Message is %s" % (SearchUrl,error))
            return scoreList
    else:
        log.error("API: out of api calls for SubtitleSeeker.com")
        return scoreList
    try:
        if not 'total_matches' in Result['results'].keys():
            return scoreList
    except Exception as error:
        log.info('getSublink: No subtitle found on Subtitleseeker for this video : %s' % Wanted['originalFileLocationOnDisk'])
        return scoreList
    if int(Result['results']['total_matches']) == 0:
        return scoreList

    for Item in Result['results']['items']:
        if (Item['site'].lower() == u'podnapisi.net' and (autosub.PODNAPISILANG == lang or autosub.PODNAPISILANG == 'Both')) or \
           (Item['site'].lower() == u'subscene.com' and (autosub.SUBSCENELANG == lang or  autosub.SUBSCENELANG == 'Both')):
            Item['release'] = Item['release'][:-4].lower() if Item['release'].endswith(".srt") else Item['release'].lower()
            NameDict = ProcessFilename(Item['release'],Wanted['container'])
            score = autosub.Helpers.scoreMatch(NameDict,Wanted)
            if score >= autosub.MINMATCHSCORE:
                scoreList.append({'score':score, 'url':Item['url'] , 'website':Item['site'].lower(), 'releaseName':Item['release'],'SubCodec':''})
    log.debug('SubSeeker: Scorelist: %r' % scoreList)
    return scoreList


def Addic7ed(language, Wanted):

    scoreList = []
    langs = u''
    if 'English' in language:
        langs = '|1|'
    else:
        langs = '|17|'

    SearchUrl = '/ajax_loadShow.php?show=' + Wanted['A7Id'] + '&season=' + Wanted['season'].lstrip('0') + '&langs=' + langs + '&hd=0&hi=0'
    log.debug('getSubLinks: Addic7ed search URL: %s' % u'http://www.addic7ed.com' + SearchUrl)

    Result = autosub.ADDIC7EDAPI.get(SearchUrl)
    if Result:
        try:
            soup = BeautifulSoup(Result)
        except:
            log.debug("getSubLinks: Addic7ed no soup exception.")
            return scoreList
    else:
       return None

    for row in soup('tr', class_='epeven completed'):
        try:
            cells = row('td')
            #Check if line is intact
            if not len(cells) == 11:
                continue
            # check on downloadlink, Completed, wanted language and episode
            if int(cells[1].string) != int(Wanted['episode']):
                continue
            if cells[5].string != u'Completed':
                continue
            if not cells[3].string:
                continue
            elif cells[3].string.upper() != language.upper():
                continue
            if not cells[9].a['href']:
                continue
            else:
                downloadUrl = cells[9].a['href']
            if not cells[4].string:
                continue
            else:
                details = cells[4].string.lower()
            HD = True if cells[8].text else False
            hearingImpaired = True if cells[6].text else False
            releasename = autosub.Addic7ed.makeReleaseName(details, Wanted['title'], Wanted['season'] , Wanted['episode'], hearingImpaired)

            # Return is a list of possible releases that match
            versionDicts = autosub.Addic7ed.ReconstructRelease(details, HD)
            if not versionDicts:
                continue
            for version in versionDicts:
                score = autosub.Helpers.scoreMatch(version, Wanted)
                if score >= autosub.MINMATCHSCORE:
                    releaseDict = {'score':score , 'releaseName':releasename, 'website':'addic7ed.com' , 'url':downloadUrl , 'HI':hearingImpaired}
                    scoreList.append(releaseDict)
        except:
            log.debug('getSubLinks: Exception from analysing episode page.')
    log.debug('Addic7ed: Scorelist: %r' % scoreList)
    return scoreList


def Opensubtitles(language, Wanted):
    scoreList = []
    if not Wanted:
        return scoreList
    Data = {}
    scoreList = []
    if 'English' in language:
        Data['sublanguageid'] = 'eng'
    else: 
        Data['sublanguageid']= 'dut'
    Data['imdbid' ] = Wanted['ImdbId']
    Data['season']  = Wanted['season']
    Data['episode'] = Wanted['episode']
    time.sleep(6)
    if not OpenSubtitlesNoOp():
        return scoreList
    try:
        Subs = autosub.OPENSUBTITLESSERVER.SearchSubtitles(autosub.OPENSUBTITLESTOKEN, [Data])
    except:
        autosub.OPENSUBTITLESTOKEN = None
        log.error('Opensubtitles: Error from Opensubtitles search API')
        return scoreList
    if Subs['status'] != '200 OK':
        log.debug('Opensubtitles: No subs found for %s on Opensubtitles.' % Wanted['releaseName'])
        return scoreList

    for Sub in Subs['data']:
        if int(Sub['SubBad']) > 0 or int(Sub['SubHearingImpaired']) > 0 or not Sub['MovieReleaseName'] or not Sub['IDSubtitleFile']:
            continue
        NameDict = ProcessFilename(Sub['MovieReleaseName'],Wanted['container'])
        if not NameDict:
            continue
         # here we score the subtitle and if it's high enough we add it to the list 
        score = autosub.Helpers.scoreMatch(NameDict,Wanted)
        if score >= autosub.MINMATCHSCORE:
            scoreList.append({'score':score, 'url':Sub['IDSubtitleFile'] , 'website':'opensubtitles.org','releaseName':Sub['MovieReleaseName'], 'SubCodec':Sub['SubEncoding']})
        else:
            log.debug('Opensubtitles: %s has scorematch %s skipping it.' % (Sub['MovieReleaseName'],score))
    return scoreList



def getSubLinks(lang, Wanted):
    """
    Return all the hits that reach minmatchscore, sorted with the best at the top of the list
    Each element had the downloadlink, score, releasename, and source website)
    Matching is based on the provided release details.

    Keyword arguments:
    lang -- Language of the wanted subtitle, Dutch or English
    Wanted -- Dict containing the ImdbId, A7Id, quality, releasegrp, source season and episode.
    """
    log.debug("getSubLinks: Show ID: %s - Addic7ed ID: %s - Language: %s - Title: %s" % (Wanted['ImdbId'],Wanted['A7Id'],lang,Wanted['title']))
    sourceWebsites, scoreListSubSeeker, scoreListAddic7ed, scoreListOpensubtitles, fullScoreList  = [],[],[],[],[]
    if autosub.PODNAPISILANG == lang or autosub.PODNAPISILANG == 'Both':
        sourceWebsites.append('podnapisi.net')
    if autosub.SUBSCENELANG == lang or autosub.SUBSCENELANG == 'Both':
        sourceWebsites.append('subscene.com')

    # If one of his websites is choosen call subtitleseeker and the python version is high enough to support https websites

    if len(sourceWebsites) > 0 and sys.version_info >= autosub.SSLVERSION:
        scoreListSubSeeker = SubtitleSeeker(lang, Wanted, sourceWebsites)
        log.debug("getSubLinks: dump scorelist: %s" % scoreListSubSeeker)

    # Use Addic7ed if selected
    if (autosub.ADDIC7EDLANG == lang or autosub.ADDIC7EDLANG == 'Both') and Wanted['A7Id']:
        scoreListAddic7ed = Addic7ed(lang, Wanted)

    # Use OpenSubtitles if selected
    if (autosub.OPENSUBTITLESLANG == lang or autosub.OPENSUBTITLESLANG == 'Both') and autosub.OPENSUBTITLESTOKEN:
        scoreListOpensubtitles = Opensubtitles(lang, Wanted)

    for list in [scoreListSubSeeker, scoreListAddic7ed, scoreListOpensubtitles]:
        if list: fullScoreList.extend(list)

    # Done comparing all the results, lets sort them and return the highest result
    # If there are results with the same score, the download links which comes last (anti-alphabetically) will be returned
    # Also check if the result match the minimal score
    sortedscorelist = sorted(fullScoreList, key=itemgetter('score', 'website'), reverse=True)

    if len(sortedscorelist) > 0:
        return sortedscorelist

    return None