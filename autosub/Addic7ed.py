#
# Autosub Addic7ed.py -https://github.com/Donny87/autosub-bootstrapbill
#
# The Addic7ed method specific module
#

import re
import library.requests as requests
from bs4 import BeautifulSoup
import time
import sys

import autosub
import autosub.Helpers
import autosub.Tvdb

from itertools import product


import logging

log = logging.getLogger('thelogger')


#Every part of the file_info got a list with regex. The first item in this list should be the standardnaming
#The second (and following) regex contains nonstandard naming (either typo's or other renaming tools (like sickbeard)) 
#Nonstandard naming should be renamed using the syn dictionary. 

_show = [re.compile('(.+)\s+\(?(\d{4})\)?', re.IGNORECASE),
              re.compile('(.+)\s+\(?(us)\)?', re.IGNORECASE),
              re.compile('(.+)\s+\(?(uk)\)?', re.IGNORECASE)]


_source = [re.compile("(ahdtv|hdtv|web[. _-]*dl|blu[. _-]*ray|dvdrip|web[-]*rip|hddvd)", re.IGNORECASE),
          re.compile("(dvd|bdrip|web)", re.IGNORECASE)]

#A dictionary containing as keys, the nonstandard naming. Followed by there standard naming.
#Very important!!! Should be unicode and all LOWERCASE!!!
_source_syn = {u'ahdtv'  : u'hdtv',
               u'dvd'    : u'dvdrip',
               u'bdrip'  : u'bluray',
               u'blu-ray': u'bluray',
               u'webdl'  : u'web-dl',
               u'web'    : u'web-dl',
               u'web-rip': u'webrip'}


_quality = [re.compile("(1080p|720p|480p)" , re.IGNORECASE), 
           re.compile("(1080[i]*|720|480)", re.IGNORECASE)]

_quality_syn = {u'1080'  : u'1080p',
                u'1080i' : u'1080p',
                u'720'   : u'720p',
                u'480p'  : u'sd',
                u'480'   : u'sd'}

_codec = [re.compile("([xh]*264|xvid|dvix)" , re.IGNORECASE)]

#Note: x264 is the opensource implementation of h264.
_codec_syn = {u'x264' : u'h264',
             u'264' : u'h264'}

#The following 2 variables create the regex used for guessing the releasegrp. Functions should not call them!
_rlsgrps_rest = ['0TV',
                'aAF',
                'BATV',
                'BTN',
                'BWB',
                'ChameE',
                'CLUE',
                'CP',
                'DEMAND',
                'DNR',
                'EbP',
                'FUSiON',
                'GFY',
                'GreenBlade',
                'HAGGiS',
                'HoodBag',
                'hV',
                'LFF',
                'LP',
                'Micromkv',
                'MMI',
                'mSD',
                'NBS',
                'NFT',
                'NIN',
                'nodlabs',
                'OOO',
                'ORPHEUS',
                'P0W4',
                'P0W4HD',
                'playXD',
                'RANDi',
                'RARBG',
                'REWARD',
                'ROVERS',
                'RRH',
                'SAiNTS',
                'SAPHiRE',
                'SCT',
                'SiNNERS',
                'SkyM',
                'SLOMO',
                'SNEAkY',
                'sozin',
                'sundox',
                'T00NG0D',
                'TASTETV',
                'TjHD',
                'TOKUS',
                'TOPAZ',
                'UP',
                'VASKITTU',
                'XS']

_rlsgrps_HD =  ['0SEC',
                '2HD',
                'CTU',
                'DIMENSION',
                'EVOLVE',
                'EXCELLENCE',
                'IMMERSE',
                'KILLERS',
                'KYR',
                'MOMENTUM',
                'ORENJi',
                'PublicHD',
                'REMARKABLE']

_rlsgrps_SD =  ['ASAP',
                'AVS',
                'BiA',
                'COMPULSiON',
                'FEVER',
                'FoV',
                'FoV',
                'FQM',
                'LOL',
                'NoTV',
                'XOR']

_rlsgrps_xvid = ['AFG',
                 'Hype']

_rlsgrps_h264 = ['TLA',
                 'BAJSKOR']

_rlsgrps_webdl=['BS',
                'CtrlHD',
                'ECI',
                'FUM',
                'HWD',
                'KiNGS',
                'NFHD',
                'NTb',
                'PCSYNDICATE',
                'POD',
                'TVSmash',
                'YFN']


def _regexRls(releaseGroupList, list=False):
    releasegrp_pre = '(' + '|'.join(releaseGroupList) + ')'
    regexReleasegrp = [re.compile(releasegrp_pre, re.IGNORECASE)]
    
    if list: return regexReleasegrp
    else: return regexReleasegrp.pop()

def _returnHits(regex, version_info):
    # Should have been filter out beforehand
    results=[]
    if not version_info:
        results.append(-1)        
        return results
    
    for reg in regex:
        results = re.findall(reg, version_info)
        if results:
            results = [x.lower() for x in results]
            results = [re.sub("[. _-]", "-", x) for x in results]
            break
    return results
        
                    
def _checkSynonyms(synonyms, results):
    for index, result in enumerate(results):
        if result in synonyms.keys() and synonyms[result]:
            results[index] = synonyms[result].lower()
        else: continue
    return results


def _getSource(file_info):
    results = _checkSynonyms(_source_syn,
                            _returnHits(_source, file_info))
    return results

def _getQuality(file_info, HD):
    results = _checkSynonyms(_quality_syn,
                            _returnHits(_quality, file_info))
    return results

def _getCodec(file_info):
    results = _checkSynonyms(_codec_syn,
                            _returnHits(_codec, file_info))
    
    return results

def _getReleasegrp(file_info):
    _allRlsgrps = _rlsgrps_rest + _rlsgrps_HD + _rlsgrps_SD + _rlsgrps_xvid + _rlsgrps_h264 + _rlsgrps_webdl
    results = _returnHits(_regexRls(_allRlsgrps, list=True), file_info)
    
    return results


def _getShow(title):
    searchName = title
    suffix = ''
    for reg in _show:
        try:
            m = re.match(reg, title)
        except TypeError:
            log.error("_getShow: Error while processing: %s %s" %(searchName, suffix))
            return searchName, suffix
        
        if m:
            searchName = m.group(1)
            suffix = m.group(2)
            break
    return searchName, suffix


def _ParseVersionInfo(version_info, HD):
    # Here the information in the a7 version columns get grouped 
    # Either source, quality, codec or releasegroup
    
    sourceList = _getSource(version_info)
    qualityList = _getQuality(version_info, HD)
    codecList = _getCodec(version_info)
    releasegroupList = _getReleasegrp(version_info)
    
    parametersList = [sourceList, qualityList, codecList, releasegroupList]   
    return parametersList

    
def _checkIfParseable(parametersList):
    # only 1 paramter list can contain more than 1 element
    for index,parameter in enumerate(parametersList):
        if len(parameter) > 1:
            tempLists = parametersList[:]
            tempLists.pop(index)
            for tempList in tempLists:
                if len(tempList) > 1:
                    return True
    return False


def _checkConflicts(versionDicts):
# Check if data is consistent in the dict
# If inconsistent, remove this dict
    toDelete = []
    for index, versionDict in enumerate(versionDicts):
        source = versionDict['source']
        quality = versionDict['quality']
        codec = versionDict['codec']
        releasegroup = versionDict['releasegrp']
        
        # The following combinations are inconsistent
        
    
        # Based on source
        if source == u'web-dl':
            if codec == u'xvid':
                toDelete.append(index)
                continue
        

        # Based on releasegroup
        if releasegroup:
            if re.match(_regexRls(_rlsgrps_HD + _rlsgrps_SD + _rlsgrps_xvid + _rlsgrps_h264), releasegroup):
                if source == u'web-dl':
                    toDelete.append(index)
                    continue
            if re.match(_regexRls(_rlsgrps_HD + _rlsgrps_h264) , releasegroup):
                if codec == u'xvid':
                    toDelete.append(index)
                    continue
            if re.match(_regexRls(_rlsgrps_HD), releasegroup):
                if quality == u'sd':
                    toDelete.append(index)
                    continue
            if re.match(_regexRls(_rlsgrps_xvid), releasegroup):
                if codec == u'h264':
                    toDelete.append(index)
                    continue
            if re.match(_regexRls(_rlsgrps_SD), releasegroup):
                if quality == u'720p' or quality == u'1080p':
                    toDelete.append(index)
                    continue
    
    # Delete duplicate indices
    toDelete = sorted(set(toDelete))    
    i = len(toDelete) -1
    
    while i>=0:
        versionDicts.pop(toDelete[i])
        i=i-1
    return versionDicts   

def _addInfo(versionDicts,HD):
    # assume missing codec is x264, error prone!
    for index, versionDict in enumerate(versionDicts):
        source = versionDict['source']
        quality = versionDict['quality']
        codec = versionDict['codec']
        releasegroup = versionDict['releasegrp']
    
        # Based on quality
        if quality == u'1080p':
            if not source:
                versionDicts[index]['source'] = u'web-dl'

    
        # Based on source
        if any(source == x for x in (u'web-dl', u'hdtv', u'bluray')):
            if not codec:
                versionDicts[index]['codec'] = u'h264'
        if source == u'web-dl':
            # default quality for WEB-DLs is 720p
            if not quality:
                versionDicts[index]['quality'] = u'720p'

        # Based on specific Releasegroups  
        if releasegroup:  
            if re.match(_regexRls(_rlsgrps_HD + _rlsgrps_SD + _rlsgrps_h264 + _rlsgrps_webdl), releasegroup):
                if not codec:
                    versionDicts[index]['codec'] = u'h264'
            if re.match(_regexRls(_rlsgrps_xvid), releasegroup):
                if not codec:
                    versionDicts[index]['codec'] = u'xvid'
            if re.match(_regexRls(_rlsgrps_HD + _rlsgrps_SD + _rlsgrps_xvid + _rlsgrps_h264), releasegroup):
                if not source:
                    versionDicts[index]['source'] = u'hdtv'  
            if re.match(_regexRls(_rlsgrps_webdl), releasegroup):
                if not source:
                    versionDicts[index]['source'] = u'web-dl'
            else:
                if quality == u'1080p' or quality == u'720p' or HD:
                    if not source:
                        versionDicts[index]['source'] = u'hdtv'
            if re.match(_regexRls(_rlsgrps_HD), releasegroup):
                if not quality:
                    versionDicts[index]['quality'] = u'720p'
            if re.match(_regexRls(_rlsgrps_SD), releasegroup):
                if not quality:
                    versionDicts[index]['quality'] = u'sd'

    return versionDicts


def _MakeTwinRelease(originalDict):
    # This modules creates the SD/HD counterpart for releases with specific releasegroups
    # DIMENSION <> LOL
    # IMMERSE <> ASAP
    # 2HD <> 2HD 720p
    # BiA <> BiA 720p
    # FoV <> FoV 720p
    
    rlsgroup = originalDict['releasegrp']
    qual = originalDict['quality']
    source = originalDict['source']
    
    rlsSwitchDict = {u'dimension' : u'lol',
                     u'lol': u'dimension',
                     u'immerse': u'asap',
                     u'asap' : u'immerse',
                     u'2hd' : u'2hd',
                     u'bia' : u'bia',
                     u'fov' : u'fov'}
    
    qualSwitchDict_hdtv = {u'sd' : u'720p',
                           u'720p' : u'sd',
                           u'1080p' : u'720p',
                           u'480p' : u'720p'}
    
    qualSwitchDict_webdl =  {u'1080p' : u'720p',
                             u'720p' : u'1080p'}
    
    twinDict = originalDict.copy()
    if rlsgroup in rlsSwitchDict.keys():
        twinDict['releasegrp'] = rlsSwitchDict[rlsgroup]
        twinDict['quality'] = qualSwitchDict_hdtv[qual]
   
    # WEB-DLs 720p and 1080p are always synced
    if source == 'web-dl' and qual in qualSwitchDict_webdl.keys():
        twinDict['quality'] = qualSwitchDict_webdl[qual]
    
    diff = set(originalDict.iteritems())-set(twinDict.iteritems())
    
    if len(diff):
        return twinDict
    else:
        return None  
    

def ReconstructRelease(version_info, HD):
    # This method reconstructs the original releasename    
    # First split up all components
    parametersList = _ParseVersionInfo(version_info, HD)

    #First check for unresolvable versions (eg 3 sources combined with multiple qualities)
    problem = _checkIfParseable(parametersList)
    if problem:
        return False
      
    releasegroups = parametersList.pop()
    codecs = parametersList.pop()
    qualities = parametersList.pop()
    sources = parametersList.pop()
    
    for x in [sources, qualities, codecs, releasegroups]:
        if not x: x.append(None)
       
    # Make version dictionaries
    # Do a cartessian product    
    versionDicts = [
    {'source': sour, 'quality': qual, 'codec': cod, 'releasegrp': rls}
    for sour, qual, cod, rls in product(sources, qualities, codecs, releasegroups)
    ]

    
    # Check for conflicting entries
    versionDicts = _checkConflicts(versionDicts)
    if not versionDicts:
        return False

    # Fill in the gaps
    versionDicts = _addInfo(versionDicts, HD)

    twinDicts = []
    for originalDict in versionDicts:
        twinDict = _MakeTwinRelease(originalDict)
        if twinDict:
            twinDicts.append(twinDict)
    
    versionDicts.extend(twinDicts)
    
    return versionDicts


def makeReleaseName(versionInfo, title, season, episode, HI=False):
    version = versionInfo.replace(' ','.')
    se = 'S' + season + 'E' + episode
    release = '.'.join([title,se,version])
    if HI:
        release = release + '.HI'
    return release

    
class Addic7edAPI():
    def __init__(self):
        self.session = requests.Session()
        self.server = 'http://www.addic7ed.com'
        self.session.headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.A.B.C Safari/525.13', 'Referer' : 'http://www.addic7ed.com', 'Pragma': 'no-cache'}
        self.logged_in = False
                
    def login(self, addic7eduser=None, addic7edpasswd=None):        
        log.debug('Addic7edAPI: Logging in')
        
        # Expose to test login
        # When fields are empty it will check the config file
        if not addic7eduser:
            addic7eduser = autosub.ADDIC7EDUSER
        
        if not addic7edpasswd:
            addic7edpasswd = autosub.ADDIC7EDPASSWD
        
        if addic7eduser == u"" or addic7edpasswd == u"":
            log.error('Addic7edAPI: Username and password must be specified')
            return False

        data = {'username': addic7eduser, 'password': addic7edpasswd, 'Submit': 'Log in'}
        try:
            r = self.session.post(self.server + '/dologin.php', data, timeout=10, allow_redirects=False)
        except requests.Timeout:
            log.debug('Addic7edAPI: Timeout after 10 seconds')
            return False
        
        if r.status_code == 302:
            log.info('Addic7edAPI: Logged in')
            self.logged_in = True
            return True
        else:
            log.error('Addic7edAPI: Failed to login')
            return False

    def logout(self):
        if self.logged_in:
            try:
                r = self.session.get(self.server + '/logout.php', timeout=10)
                log.info('Addic7edAPI: Logged out')
            except requests.Timeout:
                log.debug('Addic7edAPI: Timeout after 10 seconds')
                return None
            
            if r.status_code != 200:
                log.error('Addic7edAPI: Request failed with status code %d' % r.status_code)
        self.session.close()

    def get(self, url, login=True):
        """
        Make a GET request on `url`
        :param string url: part of the URL to reach with the leading slash
        :rtype: text
        """
        if not self.logged_in and login:
            log.error("Addic7edAPI: You are not properly logged in. Check your credentials!")
            return None
        try:
            r = self.session.get(self.server + url, timeout=15)
        except requests.Timeout:
            log.error('Addic7edAPI: Timeout after 15 seconds')
            return None
        except:
            log.error('Addic7edAPI: Unexpected error: %s' % sys.exc_info()[0])
            return None
        
        if r.status_code != 200:
            log.error('Addic7edAPI: Request failed with status code %d' % r.status_code)

        log.debug("Addic7edAPI: Resting for 60 seconds to prevent errors")
        time.sleep(60)
        r.encoding = 'utf-8'
        return r.text

    def download(self, downloadlink):
        if not self.logged_in:
            log.error("Addic7edAPI: You are not properly logged in. Check your credentials!")
            return None
        
        try:
            r = self.session.get(self.server + downloadlink, timeout=10, headers={'Referer': autosub.USERAGENT})
        except requests.Timeout:
            log.error('Addic7edAPI: Timeout after 10 seconds')
            return None
        except:
            log.error('Addic7edAPI: Unexpected error: %s' % sys.exc_info()[0])
            return None

        if r.status_code != 200:
            log.error('Addic7edAPI: Request failed with status code %d' % r.status_code)
        else:
            log.debug('Addic7edAPI: Request successful with status code %d' % r.status_code)
        
        if r.headers['Content-Type'] == 'text/html':
            log.error('Addic7edAPI: Expected srt file but got HTML; report this!')
            log.debug("Addic7edAPI: Response content: %s" % r.content)
            return None
        log.debug("Addic7edAPI: Resting for 60 seconds to prevent errors")
        time.sleep(60)
        return r.content
    
    def checkCurrentDownloads(self, logout=True):      
        self.login()
            
        try:
            soup = BeautifulSoup(self.get('/panel.php'))
            # Get Download Count
            countTag = soup.select('a[href^="mydownloads.php"]')
            pattern = re.compile('(\d*).*of.*\d*', re.IGNORECASE)
            myDownloads = countTag[0].text if countTag else False
            count = re.search(pattern, myDownloads).group(1)
            autosub.DOWNLOADS_A7 = int(count)
            
            # Get account type and set download max
            classTag = soup.select("tr")[20]
            account = classTag.select("td")[1].string
            if account == 'VIP':
                autosub.DOWNLOADS_A7MAX = 80
        except:
            log.error("Addic7edAPI: Couldn't retrieve Addic7ed MyPanel data")
            return False
        
        if logout:
            self.logout()
        
        return True    
    
    def geta7ID(self,TvdbShowName, localShowName):
        # Last resort: lookup official name and try to match with a7 show list

        show_ids={}
        html = self.get('/shows.php', login=False)
        if not html:
            return None
        show_ids = dict(url.split("\">") for url in re.findall(r'<a href=[\'"]/show/?([^<]+)', html))

        #----------------------------------------------------------------#
        # changed the beautifull soup call to a simpel regex             #
        # beautifull soup takes alsmost 20 seconds to process this page. #
        #----------------------------------------------------------------#

        #try:
        #    soup = self.get('/shows.php', login=False)
        #    for html_show in soup.select('td.version > h3 > a[href^="/show/"]'):
        #        show_ids[html_show.string.lower()] = int(html_show['href'][6:]) 
        #except:
        #    log.error('geta7IDApi: failed to retrieve a7 show list')
        #    return None
        
        
        # First clip of year or US, UK from the name
        show_regex = [re.compile('(.+)\s+\(?(\d{4})\)?', re.IGNORECASE),
                      re.compile('(.+)\s+\(?(us)\)?', re.IGNORECASE),
                      re.compile('(.+)\s+\(?(uk)\)?', re.IGNORECASE)]


        searchName_off, suffix_off = _getShow(TvdbShowName)
        for Id, show in show_ids.iteritems():
            # First try it with the official show name from TvDB
            m = re.match('%s(.*)' % searchName_off, show, re.I)
            if m:
                # Get False-Positive UK titles out; assumes UK is always indicated
                if not re.search('UK', suffix_off, re.I) and re.search('UK', m.group(1), re.I):
                    continue
                if len(searchName_off) < len(show):
                    log.debug("geta7IDApi: Skipping %s because we found a just a partial match for %s" %(show,TvdbShowName))
                    continue
                a7_id = Id
                log.debug("geta7IDApi: Addic7ed ID %s found using the official show name %s" %(a7_id, TvdbShowName))
                return a7_id
            # If the official show name is different try also the one from the episode file
            if localShowName != TvdbShowName:
                searchName_local, suffix_local = _getShow(localShowName)
                n = re.match('%s(.*)' % searchName_local, show, re.I)
                if n:
                    # Get False-Positive UK titles out; assumes UK is always indicated
                    if not re.search('UK', suffix_local, re.I) and re.search('UK', n.group(1), re.I):
                        continue
                    if len(searchName_local) < len(show):
                        log.debug("geta7IDApi: Skipping %s because we found a just a partial match for %s" %(show,localShowName))
                        continue
                    a7_id = Id
                    log.debug("geta7IDApi: Addic7ed ID %s found using filename show name %s" % (a7_id, localShowName))
                    return a7_id

        return None
