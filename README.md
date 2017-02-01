# KissBot
Automatically download video from kissanime.ru, kisscartoon.se and kissasian.com via a spreadsheet. This build is designed to reliably mass download videos, this code has many improvements and fixes over the main release.<br>
<br>
Contact via https://discord.gg/W7uVTd7 (Username - Yubikiri).<br>
<br>
**Features:**
* Parrallel downloader, with support to specify how many asynchronous downloads are allowed at the same time.
* Limit the queue limit to prevent link expiry on downloads with large episode count
* Resumable operations, cancel the operation anytime and you'll have no issues when restarting
* Files are checked if downloaded, to prevent redownloading downloaded files. Resumes from last downloaded episode.
* Defined max resolution to download

**Installation**
* Install Python 3 [Download Here](https://www.python.org/downloads/)
* Download and copy [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) to folder of script
* Install [Chrome](https://www.google.com.au/chrome/browser/desktop/#eula)
* Install any missing python modules with `pip install {module}`

**Configuration**<br>
Required KissDownloader.py configuration #CONFIG<br>
* 'user_name' and 'user_password' as kiss account

**Usage**<br>
KissDownloader.py resolved.csv spreadsheet<br>
The following columns are required in the spreadsheet:<br>
* Column 1: [Filename]
* Column 2: [Kiss url to page listing episodes]
* Column 3: 0 [Ignore, used by developer]
* Column 4: 0 [Episode count, numeric value]
* Column 5: 0 (Optional) [Initial episode to download from, numeric value]
* Column 6: 0 (Optional) [Max episode to download from, numeric value]
* Column 7: 0 [Restrict resolution to quality equal to or lower than ('360','480','720','1080'), value range 0-1080]
