# KissBot
Automatically download anime from KissAnime from a spreadsheet. This build is designed to reliably mass download anime, it features many improvements and bug fixes over BDrgons code, tested working with over 300 animes series.<br>
<br>
Contact me (Username - Yubikiri) at https://discord.gg/W7uVTd7 and be sure to click the 'Watch' button to get notified for updates and bugfixes.<br>
<br>
**Features:**
* async downloader, with support to specify download thread count
* resolve from last downloaded episode
* download queue_limit to prevet link expiry on downloads with large episode count
* logic to prevent redownloading downloaded files

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
* Column 4: episode count (episode count to download) (overwritten if column 6 isn't 0)
* Column 5: 0 (refer to below explaination)
* Column 6: 0 (refer to below explaination)
<br>
Column 5 and 6 are optional, used to define episode number to download between. If column 5 is set to 5 it will start at episode 5, if column 6 is set to 10 it will download till episode 10. Useful to download only certain episodes.

