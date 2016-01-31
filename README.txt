README 

IMPORTANT INFO
Due to the removal of the main repo this fork now serves as the latest "well tested" version of Auto-Sub Bootstrap Bill. This isn't my code and I'm certainly not the main developer. If you're interested in the further development of the program, please visit https://github.com/BenjV/autosub-bootstrapbill
If you encounter any issues while using Auto-Sub, please report them at https://github.com/BenjV/autosub-bootstrapbill/issues

+--- Auto-Sub Bootstrap Bill
     |
     +--- Uses SubtitleSeeker API, supporting the following website:
     |    +--- Podnapisi
     |    +--- Subscene
     |    +--- OpenSubtitles
     |    \--- Undertexter
     |
     +--- Addic7ed support.
     |    +--- Requires account.
     |    \--- Limited downloads per 24 hours. (Regular: 30 - VIP: 55)
     |
     +--- Notifications
     |    +--- Windows & Windows Phone
     |    |    +--- Pushalot
     |    |    \--- Growl
     |    +--- Android
     |    |    +--- Notify My Android
     |    |    \--- Pushover
     |    +--- OSX & iDevices
     |    |    +--- Pushover
     |    |    +--- Growl
     |    |    +--- Prowl
     |    |    \--- Boxcar
     |    \--- Other
     |         +--- Email
     |         +--- Twitter
     |         \--- Plex Media Server
     |
     \--- Features
          +--- Mobile template, automatically detected.
          +--- Multiple folder support, separate folders with a comma. Example: D:\Series1,D:\Series2
          +--- Select which languages you want to allow per website.
          |    \--- If you set this to 'None', then the site will be disabled.
          +--- Remove English subtitle when the Dutch subtitle has been downloaded.
          +--- Configure a custom post-process script.
          \--- Home tables.
               +--- Both
               |    +--- Select 10, 25, 50, 100, All items to display. Options are stored using localStorage.
               |    \--- Search field, which allows you to search on show name.
               +--- Wanted
               |    +--- Option to skip show when clicking on the show name.
               |    \--- Option to skip season when clicking on the season.
               +--- Downloaded
                    \--- Display original subtitle and website by hovering over the show name

To use:

Ubuntu
Make sure you have python installed. Also you need the python-cheetah package:
 * sudo apt-get install python-cheetah
 * Download the zip file from our download section
 * Unzip the file, change to the directory where AutoSub.py is located
 * Start the script: " python AutoSub.py "
 * A webbrowser should now open
 * Go to the config page, check the settings, make sure you set atleast: path 
(Should point to the location where AutoSub.py is located. Rootpath (Should point to the root of your series folder)
 * Shutdown AutoSub and start it again
Enjoy your subtitles!

Requirements for running Auto-Sub Bootstrap Bill:
- Install Cheetah : https://pypi.python.org/pypi/Cheetah/2.4.4
- Python2.7

You can use a version lower than python2.7 but as an additional dependency, you have to install
the python html5lib module: https://pypi.python.org/pypi/html5lib/1.0b3




