# KissBot
Automatically download video from kissanime.ru, kisscartoon.se and kissasian.com via a spreadsheet. Reliably mass download videos.<br>
<br>
Contact for support/troubleshooting https://discord.gg/W7uVTd7 (Username - Yubikiri).<br>
<br>
**Features:**
* GUI to easily queue multiple series to download.
* Download multiple files at the same time.

**Installation**
* Install Python 3 [Download Here](https://www.python.org/downloads/)
* Download and copy [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) to folder of script
* Install [Chrome](https://www.google.com.au/chrome/browser/desktop)
* Run `pip install -r requirements.txt` to install required modules.

**Configuration**<br>
KissDownloader.py configuration under #CONFIG<br>
* 'username' and 'userpassword' as kiss account

**Usage**<br>
Run KissDownloaderGUI.py <br>
* URL:                 [Kiss url to page listing episodes] (required)
* Filename:            [Filename used for downloaded files] (required)
* Episode Count:  0    [Episode count, numeric value] (required)
* Episode Min:    0    [First episode to download, numeric value] (ignored if 0)
* Episode Max:    0    [Last episode to download, numeric value] (ignored if 0)
* Resolution:     720p [Restrict resolution to quality equal to or less than ('360','480','720','1080')] (Ignored if 0)
