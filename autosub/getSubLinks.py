#
# Autosub getSubLinks.py - https://github.com/Donny87/autosub-bootstrapbill
#
# The getSubLinks module
#

import logging

from xml.dom import minidom
import xml.etree.cElementTree as ET
from operator import itemgetter
from bs4 import BeautifulSoup
import autosub.Helpers
from autosub.ProcessFilename import ProcessFilename
import autosub.Addic7ed
from autosub.OpenSubtitles import TimeOut
# Settings
log = logging.getLogger('thelogger')


def SubtitleSeeker(showid, lang, releaseDetails, sourceWebsites):
    # Get the scored list for all SubtitleSeeker hits
    api = autosub.API


    season     = releaseDetails['season']     if 'season'     in releaseDetails.keys() else None
    episode    = releaseDetails['episode']    if 'episode'    in releaseDetails.keys() else None
    quality    = releaseDetails['quality']    if 'quality'    in releaseDetails.keys() else None
    releasegrp = releaseDetails['releasegrp'] if 'releasegrp' in releaseDetails.keys() else None
    source     = releaseDetails['source']     if 'source'     in releaseDetails.keys() else None
    codec      = releaseDetails['codec']      if 'codec'      in releaseDetails.keys() else None


    # this is the API search 
    getSubLinkUrl = "%s&imdb=%s&season=%s&episode=%s&language=%s" % (api, showid, season, episode, lang)
    log.info('getSubLinks: SubtitleSeeker request URL: %s' % getSubLinkUrl)
    if autosub.Helpers.checkAPICallsSubSeeker(use=True):
        try:
            subseekerapi = autosub.Helpers.API(getSubLinkUrl)
            dom = minidom.parse(subseekerapi.resp)
            subseekerapi.resp.close()
        except:
            log.error("getSubLink: The server returned an error for request %s" % getSubLinkUrl)
            return None
    else:
        log.error("API: out of api calls for SubtitleSeeker.com")
        return None
    
    if not len(dom.getElementsByTagName('error')) == 0:
        for error in dom.getElementsByTagName('error'):
            try:
                errormsg = error.getElementsByTagName('msg')[0].firstChild.data
                log.error("getSubLink: Error found in API response: %s" % errormsg)
            except AttributeError:
                log.debug("getSubLink: Invalid msg tag in API response, unable to read error message.")
        return None

    if not dom or len(dom.getElementsByTagName('item')) == 0:
        return None

    scoreList = []

    for sub in dom.getElementsByTagName('item'):
        try:
            release = sub.getElementsByTagName('release')[0].firstChild.data
            release = release.lower()
            # Remove the .srt extension some of the uploaders leave on the file
            if release.endswith(".srt"):
                release = release[:-4]
        except AttributeError:
            log.debug("getSubLink: Invalid release tag in API response, skipping this item.")
            continue
        
        try:
            website = sub.getElementsByTagName('site')[0].firstChild.data
            website = website.lower()
        except AttributeError:
            log.debug("getSubLink: Invalid website tag in API response, skipping this item.")
            continue
        
        try:
            url = sub.getElementsByTagName('url')[0].firstChild.data
        except AttributeError:
            log.debug("getSubLink: Invalid URL tag in API response, skipping this item.")
            continue
        
        tmpDict = ProcessFilename(release, '')
        
        if not website in sourceWebsites or not tmpDict:
            continue

        # ReleaseDict is a dictionary with the score, releasename and source website for the subtitle release
        releaseDict = {'score':None , 'releasename':release , 'url':url , 'website':website}
        releaseDict['score'] = autosub.Helpers.scoreMatch(tmpDict, release, quality, releasegrp, source, codec)

        scoreList.append(releaseDict)


def Addic7ed(a7ID , language, releaseDetails):

    title      = releaseDetails['title']      if 'title'      in releaseDetails.keys() else None
    season     = releaseDetails['season']     if 'season'     in releaseDetails.keys() else None
    episode    = releaseDetails['episode']    if 'episode'    in releaseDetails.keys() else None
    quality    = releaseDetails['quality']    if 'quality'    in releaseDetails.keys() else None
    releasegrp = releaseDetails['releasegrp'] if 'releasegrp' in releaseDetails.keys() else None
    source     = releaseDetails['source']     if 'source'     in releaseDetails.keys() else None
    codec      = releaseDetails['codec']      if 'codec'      in releaseDetails.keys() else None

    params = {'show_id': a7ID, 'season': season}
    Result = autosub.ADDIC7EDAPI.get('/show/{show_id}&season={season}'.format(**params))
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
            releaseDict = {'score':None , 'releasename':releasename, 'website':'addic7ed.com' , 'url':downloadUrl , 'HI':hearingImpaired}
            releaseDict['score'] = autosub.Helpers.scoreMatch(version, details, quality, releasegrp, source, codec)
            scoreList.append(releaseDict)
    return scoreList


def Opensubtitles(EpisodeId, language, releaseDetails):

    title      = releaseDetails['title']      if 'title'      in releaseDetails.keys() else None
    season     = releaseDetails['season']     if 'season'     in releaseDetails.keys() else None
    episode    = releaseDetails['episode']    if 'episode'    in releaseDetails.keys() else None
    quality    = releaseDetails['quality']    if 'quality'    in releaseDetails.keys() else None
    releasegrp = releaseDetails['releasegrp'] if 'releasegrp' in releaseDetails.keys() else None
    source     = releaseDetails['source']     if 'source'     in releaseDetails.keys() else None
    codec      = releaseDetails['codec']      if 'codec'      in releaseDetails.keys() else None


    LangId = 'dut' if language == 'Dutch' else 'eng'
    SearchUrl = '/xml/search/sublanguageid-' + str(LangId) + '/imdbid-' + str(EpisodeId)
    try:
        TimeOut()
        RequestResult = autosub.OPENSUBTTITLESSESSION.get(autosub.OPENSUBTITLESURL + SearchUrl, timeout=10)
        Referer = SearchUrl.replace('/xml','')
        autosub.OPENSUBTTITLESSESSION.headers.update({'referer': Referer})
    except:
        log.debug('getSubLinks: Could not connect to OpenSubtitles.')
        return None
    if 'text/xml' not in RequestResult.headers['Content-Type']:
        log.error('getSubLinks: OpenSubtitles responded with an error')
        return None
    try:
        root = ET.fromstring(RequestResult.content)
    except:
        log.debug('getSubLinks: Serie with IMDB ID %s could not be found on OpenSubtitles.' %SerieImdb)
        return None    

    try:
        SubTitles = root.find('.//search/results')
    except:
        log.debug('getSubLinks: Serie with IMDB ID %s could not be found on OpenSubtitles.' %SerieImdb)
        return None
    # We fetch the show overview page and search voor the Id's of the epiode we want
    # Because as we have this whole page, we put the other Episode Id's in the cache
    scoreList = []
    for Sub in SubTitles:
        try:
            if Sub.tag != 'subtitle':
                continue
            try:
                SubBad = int(Sub.find('SubBad').text)
                if SubBad > 0:
                    log.debug("getSubLinks: OpenSubtitles has %d bad reports for this subtitle, skipping." %SubBad)
                    continue
                else:
                    log.debug("getSubLinks: OpenSubtitles has %d bad reports for this subtitle." %SubBad)
            except:
                pass
            Link = Sub.find('IDSubtitle').attrib['Link']
            release = Sub.find('MovieReleaseName').text.split('[]')[0].lower()
        except:
            continue
        url = autosub.OPENSUBTITLESURL[:-3] + Link +'/xml'
        tmpDict = ProcessFilename(release, '')
        
        if not tmpDict:
            continue

        # ReleaseDict is a dictionary with the score, releasename and source website for the subtitle release
        releaseDict = {'score':None , 'releasename':release , 'url':url , 'website':'opensubtitles.org'}
        releaseDict['score'] = autosub.Helpers.scoreMatch(tmpDict, release, quality, releasegrp, source, codec)

        scoreList.append(releaseDict)
    return scoreList


def getSubLinks(showid, a7_id, episodeId, lang, releaseDetails):
    """
    Return all the hits that reach minmatchscore, sorted with the best at the top of the list
    Each element had the downloadlink, score, releasename, and source website)
    Matching is based on the provided release details.

    Keyword arguments:
    showid -- The IMDB id of the show
    a7_id  -- The Addic7ed id of the show
    lang -- Language of the wanted subtitle, Dutch or English
    releaseDetails -- Dict containing the quality, releasegrp, source season and episode.
    """
    log.debug("getSubLinks: Show ID: %s - Addic7ed ID: %s - Language: %s - Release Details: %s" % (showid,a7_id,lang,releaseDetails))
    sourceWebsites, scoreListSubSeeker, scoreListAddic7ed, scoreListOpensubtitles, fullScoreList  = [],[],[],[],[]
    if autosub.PODNAPISILANG == lang or autosub.PODNAPISILANG == 'Both':
        sourceWebsites.append('podnapisi.net')
    if autosub.SUBSCENELANG == lang or autosub.SUBSCENELANG == 'Both':
        sourceWebsites.append('subscene.com')
    if autosub.UNDERTEXTERLANG == lang or autosub.UNDERTEXTERLANG == 'Both':
        sourceWebsites.append('undertexter.se')

    # If one of his websites choosen call subtitleseeker
    if len(sourceWebsites) > 0:
        scoreListSubSeeker = SubtitleSeeker(showid, lang, releaseDetails, sourceWebsites)
        log.debug("getSubLinks: dump scorelist: %s" % scoreListSubSeeker)

    # Use Addic7ed if selected
    if (autosub.ADDIC7EDLANG == lang or autosub.ADDIC7EDLANG == 'Both') and a7_id:
        log.debug("getSubLinks: goto Addic7ed function with ID %s" %a7_id)
        scoreListAddic7ed = Addic7ed(a7_id, lang, releaseDetails)

    # Use OpenSubtitles if selected
    if (autosub.OPENSUBTITLESLANG == lang or autosub.OPENSUBTITLESLANG == 'Both') and episodeId:
        log.debug("getSubLinks: goto OpenSubtitles function with ID %s" %episodeId)
        scoreListOpensubtitles = Opensubtitles(episodeId, lang, releaseDetails)

    for list in [scoreListSubSeeker, scoreListAddic7ed, scoreListOpensubtitles]:
        if list: fullScoreList.extend(list)

    # Done comparing all the results, lets sort them and return the highest result
    # If there are results with the same score, the download links which comes last (anti-alphabetically) will be returned
    # Also check if the result match the minimal score
    sortedscorelist = sorted(fullScoreList, key=itemgetter('score', 'website'), reverse=True)

    toDelete = []
    for index, item in enumerate(sortedscorelist):
        name = item['releasename']
        log.debug('getSubLink: checking minimal match score for %s. Minimal match score is: %s' % (name, autosub.MINMATCHSCORE))
        score = item['score']
        if not score >= autosub.MINMATCHSCORE:
            log.debug('getSubLink: %s does not match the minimal match score' % name)
            toDelete.append(index)
    i = len(toDelete) - 1
    while i >= 0:
        log.debug("getSubLink: Removed item from the ScoreDict at index %s" % toDelete[i])
        sortedscorelist.pop(toDelete[i])
        i -= 1

    if len(sortedscorelist) > 0:
        return sortedscorelist

    return None