README 

+--- Auto-Sub Bootstrap Bill
     |
     +--- Uses SubtitleSeeker API, supporting the following website:
     |    +--- Podnapisi
     |    +--- Subscene
     |
     +---Uses the Opensubtitles API
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
          +--- Skip filter for English and Dutch subtitles
          +--- Configure auto-refresh rate on home page (0 is no refresh)
          +--- Choose the default codepage for subtitles (default is windows-1252)
          +--- Choose to skip hidden directories from being searchedz
          +--- Choose to launch browser after startup
          +--- Mobile template, automatically detected.
          +--- Multiple folder support, separate folders with a comma. Example: D:\Series1,D:\Series2
          +--- Select which languages you want to allow per website.
          |    \--- If you set this to 'None', then the site will be disabled.
          +--- Remove English subtitle when the Dutch subtitle has been downloaded.
          +--- Calls a custom post-process script.
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

Windows:
Download the zipfile and run the pythonscript from the directory you're unzipped it to
Use pythonw autosub.py tot start it as a process
Start you're brouwser with http://localhost:8083/home/

Synology:
Use the package from http://packages.mdevries.org/
Add this location to the package centre and don't forget to check "Any Publisher" ( Settings, Trust Level)


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
- Python2.7 preferable 2.7.9 or higher

You can use a version lower than python2.7 but as an additional dependency, you have to install
the python html5lib module: https://pypi.python.org/pypi/html5lib/1.0b3

Release information:

Version 0.8.1
Maintenance release

- Changed the layout of the config page.
  Put the most important items on top.
  Changed some input field in tick boxes
  Changed some input field to easier quantities (bytes -> Kbytes, secs -> Hours)
- It is now no longer possible to choose a sub language per website. That feature was quite useless and created a lot op confusion.
  Language choice is now for all websites.
- Add an option in de Config to include or exclude Hearing Impaired Subs
- Added a reboot option to the menu
- Added the possibility to add ImdbId's as Skipshow 
- Fixed an issue with a skipshow if a semicolon was in the showname
- Fixed an issue with the notifiers when a non-ascii charachter is found in the showname.
- In the wanted list the attibutes which are set in the minmatchscore are now a different color, so it is easy to see on which criteria the subs are scored.
- The pushover notifier is changed, now it does not use its own application key anymore, but the user has to supply both application key and user key.

Version 0.7.4:
- Fixed a bug that ssl websites (podnapisi,subscene and github) could not be reached (file not found error).
- Fixed an issue that the skipstring for English in certain situations didn't function
- Removed the message after start of the Update command so the browser would stay on the home page 
- updated to Requests library version 2.10



