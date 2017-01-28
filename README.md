# KissBot
Modification of https://github.com/BDrgon/KissDownloader<br>
Automatically download anime from KissAnime from a spreadsheet<br>
This build is designed to reliably mass download anime, it features many improvements and bug fixes over BDrgons code.<br>
Tested working with over 300 animes series.<br>
Contact me (Username - Yubikiri) at https://discord.gg/W7uVTd7 and be sure to click the 'Watch' button to get notified for updates and bugfixes.
<br>
**Features:**
* async downloader, with support to specify download thread count
* resolve from last downloaded episode
* download queue_limit to prevet link expiry on downloads with large episode count
* recheck failed downloads with retrieve_last to resolve files again and redownload

**Installation**
* Install Python 3 [Download Here](https://www.python.org/downloads/)
* Install any missing python modules with `pip install {module}`

**Configuration**<br>
Required KissDownloader.py edits #CONFIG<br>
* 'user_name' and 'user_password' as kissanime account
* 'destination' download folder

**Usage**<br>
KissDownloader.py resolved.csv spreadsheet<br>
The following columns are required in the spreadsheet:<br>
* Column 1: anime title (used for filename)
* Column 2: kissanime url
* Column 3: 0 (leave as 0, used by developer)
* Column 4: episode count
