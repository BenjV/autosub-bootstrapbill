# Autosub common.py - https://code.google.com/p/autosub-bootstrapbill/
#
# The Autosub checkSub module
#
# Based on Sickbeard & Guesit, thanks!
# 

import re

#List with all the possible seperators used in filenaming
seperator = u' ._-()[]{}'

show_regex = [re.compile("^((?P<title>.+?)[. _-]+)?s(?P<season>\d+)[x. _-]*e(?P<episode>\d+)[x. _-]*(?P<extra_info>.+)*", re.IGNORECASE),
        re.compile("^((?P<title>.+?)[. _-]+)?(?P<season>\d+)x(?P<episode>\d+)[x. _-]*(?P<extra_info>.+)*", re.IGNORECASE),
        re.compile("^((?P<title>.+?)[. _-]+)?(?P<season>\d{1,2})(?P<episode>\d{2})[x. _-]*(?P<extra_info>.+)*", re.IGNORECASE)]

episode_regex = [re.compile("(s\d+[x. _-]*e\d+|\d+x\d+)", re.IGNORECASE)]

#Every part of the file_info got a list with regex. The first item in this list should be the standardnaming
#The second (and following) regex contains nonstandard naming (either typo's or other renaming tools (like sickbeard)) 
#Nonstandard naming should be renamed using the syn dictionary. 

source = [re.compile("(ahdtv|hdtv|web[. _-]*dl|blu[. _-]*ray|dvdrip|web[-]*rip|hddvd)", re.IGNORECASE),
          re.compile("(dvd|bdrip|web)", re.IGNORECASE)]

#A dictionary containing as keys, the nonstandard naming. Followed by there standard naming.
#Very important!!! Should be unicode and all LOWERCASE!!!
source_syn = {u'ahdtv'  : u'hdtv',
              u'dvd'    : u'dvdrip',
              u'bdrip'  : u'bluray',
              u'blu-ray': u'bluray',
              u'webdl'  : u'web-dl',
              u'web'    : u'web-dl',
              u'web-rip': u'webrip'}

quality = [re.compile("(1080p|720p)" , re.IGNORECASE), 
           re.compile("(1080[i]*|720|HD|SD)", re.IGNORECASE)]

quality_syn = {u'1080' : u'1080p',
               u'1080i': u'1080p',
               u'720'  : u'720p',
               u'hd'   : u'720p'}

#A dictionary containing as keys fileextensions followed by the matching quality.
#If the quality regex fails, ProcessFile will look in this dictionary. If the fileextension
#is not here, it will guess that the quality is SD. 
quality_fileext = {u'.mkv' : u'720p',
                   u'.mp4' : u'sd',
                   u'.avi' : u'sd'}

codec = [re.compile("([xh]*264|xvid|dvix)" , re.IGNORECASE)]

#Note: x264 is the opensource implementation of h264.
codec_syn = {u'x264' : u'h264',
             u'264'  : u'h264'}

codec_fileext = {u'.mkv' : u'h264',
                 u'.mp4' : u'h264',
                 u'.avi' : u'xvid'}

#The following 2 variables create the regex used for guessing the releasegrp. Functions should not call them!
_releasegrps = ['0TV',
                '0SEC',
                '2HD',
                'aAF',
                'AFG',
                'ASAP',
                'AVS',
                'BAJSKORV',
                'BATV',
                'BiA',
                'BS',
                'BTN',
                'CHAMEE',
                'CLUE',
                'compulsion',
                'CP',
                'CtrlHD',
                'CTU',
                'DEMAND',
                'DIMENSION',
                'DNR',
                'EbP',
                'ECI',
                'EVOLVE',
                'EXCELLENCE',
                'FOV',
                'FQM',
                'FUM',
                'FUSiON',
                'GFY',
                'GreenBlade',
                'HoodBag',
                'hV',
                'HWD',
                'Hype',
                'IMMERSE',
                'KILLERS',
                'KiNGS',
                'KYR',
                'LFF',
                'LOL',
                'LP',
                'Micromkv',
                'MMI',
                'MOMENTUM',
                'mSD',
                'NBS',
                'NFHD',
                'NFT',
                'NIN',
                'nodlabs',
                'NTb',
                'OOO',
                'ORENJi',
                'ORPHEUS',
                'P0W4',
                'P0W4HD',
                'PCSYNDICATE',
                'playXD',
                'POD',
                'PUBLICHD',
                'RANDi',
                'REMARKABLE',
                'RRH',
                'SAINTS',
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
                'TLA',
                'TOKUS',
                'TVSMASH',
                'UP',
                'VASKITTU',
                'XS',
                'YFN']

_releasegrp_pre = '(' + '|'.join(_releasegrps) + ')$'

releasegrp = [re.compile(_releasegrp_pre, re.IGNORECASE)]

#If the releasegrp is not in the list (_releasegrps), try our old regex.
releasegrp_fallback = [re.compile("(-(?P<releasegrp>[^- \.]+))?$", re.IGNORECASE)]

#If you know a result is invalid you can use the syn dict to renaming it to a None type.
releasegrp_syn = {u'dl': None}