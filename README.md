# KissDownloader
Downloads a list of shows from Kissanime.ru, Kisscartoon.me, Kissasian.com<br>
Modification of https://github.com/BDrgon/KissDownloader with the ability to download from a list 

**Installation**
* Install Python 3 [Download Here](https://www.python.org/downloads/)
* Run UpdateModuals.py (as superuser on mac/linux)
* Install any missing python modules with `pip install {module}`.
* Edit KissDownloader.py (under #CONFIG), define 'user_name', 'user_password', 'destination'.

**Usage**
* KissDownloader.py will iterate through each line in resolved.csv
* Resolved.csv is a spreadsheet required by this program, included extensive example list.
* Column 1: anime title (required)
* Column 2: kissanime url (required)
* Column 3: episode count (optional)
* Column 4: (not used, leave as '0')

**Configuration**
* 'website' as either ["kissanime.ru", "kisscartoon.me", "kissasian.com"]
* 'user_name' and 'user_password' as your kissanime account
* 'destination' as your download folder