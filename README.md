# KissBot
Automatically download video from kissanime.ru, kisscartoon.se and kissasian.com via a spreadsheet. Reliably mass download videos.<br>
<br>
Contact for support/troubleshooting https://discord.gg/W7uVTd7 (Username - Yubikiri).<br>
<br>
**Features:**
* Parrallel downloader, with support to specify how many asynchronous downloads are allowed at the same time!
* GUI to easily queue series to download!
* Resumable operations, cancel the operation anytime.
* Files are verified if downloaded, to prevent redownloading downloaded files. Resumes from last downloaded episode.
* Queue management to prevent link expiry.
* Define max resolution to download, start and end episode.

**Installation**
* Install Python 3 [Download Here](https://www.python.org/downloads/)
* Download and copy [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) to folder of script
* Install [Chrome](https://www.google.com.au/chrome/browser/desktop/#eula)
* Install any missing python modules with `pip install {module}`, don't forget to run as superuser if error!

**Configuration**<br>
KissDownloader.py configuration under #CONFIG<br>
* 'username' and 'userpassword' as kiss account

**Usage**<br>
Run KissDownloaderGUI.py <br>
* URL:                 [Kiss url to page listing episodes] (required)
* Filename:            [Filename used for downloaded files] (required)
* Episode Count:  0    [Episode count, numeric value] (required)
* Episode Min:    0    [First episode to download, numeric value] (Ignored if 0)
* Episode Max:    0    [Last episode to download, numeric value] (Ignored if 0)
* Resolution:     720p [Restrict resolution to quality equal to or less than ('360','480','720','1080')] (Ignored if 0)
