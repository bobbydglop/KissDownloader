#!/usr/bin/env python
import sys
import os
import time
import glob
import shutil
import random
from random import randint
import csv
import re
import socket
import requests
from pathlib import Path

import threading
from threading import Thread, Lock
import queue as Queue

import urllib
import urllib.request as urllib2
from urllib.request import urlretrieve
from urllib.parse import urlparse

import youtube_dl
import pySmartDL

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from utils import *

# TODO Fix min episode
# TODO Revise get_episode logic, support non-standard naming schema

utils.log("== Starting up ==")
utils.config = utils.read_settings()
if not utils.config['DEFAULT']['username'] or not utils.config['DEFAULT']['userpassword']:
    utils.log("Please provide username and password in the configuration file.")
    sys.exit()
else:
    username = utils.config['DEFAULT']['username']
    userpassword = utils.config['DEFAULT']['userpassword']
    destination_folder = utils.config['DEFAULT']['destination_folder']

    download_threads = utils.config['OTHER']['download_threads']
    complete_dir = utils.config['OTHER']['complete_dir']
    demo_data = utils.config['OTHER']['demo_data']

if getattr(sys, 'frozen', False):
    dir_path = os.path.dirname(sys.executable)
elif __file__:
    dir_path = os.path.dirname(__file__)

randnum=str(randint(1, 100000)) # used to create random filename, should be revised
queue=Queue.Queue()
count=0
download_list=({})
download_prog = False

class KissDownloader(threading.Thread):
    def __init__(self, params, queue):
        if(params):
            self.rootPage=""
            self.file_extension=""
            self.download(params)
        else:
            threading.Thread.__init__(self)
            self.queue=queue

    def run(self):
        global count
        global download_list
        while True:
            host=self.queue.get()
            #print('url',host)
            nestlist=[x for x in episode_list if host in x[0]]
            if(nestlist):
                count=count + 1
                if not os.path.isfile(nestlist[0][2] + nestlist[0][1]):
                    episode=str(nestlist[0][3])
                    #print("Download", episode)
                    #urlretrieve(str(host).replace(" ","%20"), str(nestlist[0][2] + "temp/" + nestlist[0][1]))
                    #path=nestlist[0][2] + "temp/" + nestlist[0][1]
                    #location=obj.get_dest()
                    obj=pySmartDL.SmartDL(str(host).replace(" ","%20"), nestlist[0][2] + "temp/" + nestlist[0][1], progress_bar=False, fix_urls=True)
                    obj.start(blocking=False)
                    while True:
                        if obj.isFinished():
                            break
                        progress = obj.get_progress() * 100
                        if obj.get_eta() > 0 and (obj.get_progress() * 100) < 100:
                            console_output=str(nestlist[0][1] + "\t " + str(float("{0:.2f}".format((float(obj.get_progress())*100)))) + "% done at " + pySmartDL.utils.sizeof_human(obj.get_speed(human=False)) + "/s, ETA: "+ obj.get_eta(human=True))
                            try:
                                download_list[nestlist[0][3]]=console_output # update
                            except KeyError:
                                download_list[nestlist[0][3]].append(console_output) # initial
                            except Exception as e:
                                utils.log(e)
                                utils.log("=E Download logic error")
                        time.sleep(1)
                        if progress == 100 and obj.get_eta() == 0:
                            time.sleep(1)
                    if obj.isFinished():
                        try:
                            del download_list[nestlist[0][3]] # remove
                        except Exception as e:
                            utils.log(e)
                            utils.log("Error: unable to remove episode" + str(nestlist[0][3]))
                        try:
                            shutil.move(nestlist[0][2] + "temp/" + nestlist[0][1], nestlist[0][2] + nestlist[0][1]) # move on download complete
                        except Exception as e:
                            utils.log(e)
                            utils.log("Failed moving " + str(nestlist[0][2] + "temp/" + nestlist[0][1]) + " to " + str(nestlist[0][2] + nestlist[0][1]))
                    utils.log("Completed" + str(episode))
                count=count - 1
                self.queue.task_done()

    def download_message():
        global download_prog
        global download_list
        global count
        if(download_prog == 0): # one instance
            download_prog=1
            while count > 0:
                sep = 0
                for item in download_list:
                    if download_list[item]:
                        if sep == 0:
                            sep = 1
                            utils.log("\u2500\u2500\u2500\u2500\u2500\u2500") # ------
                        utils.log(download_list[item]) # output download progress
                    else:
                        utils.log('Download starting...')
                    #print(str(item), ':', download_list[item])
                time.sleep(4)
            download_prog=0

    def login(self, user, pw, site):
        status=""
        while (status == 503 and status != ""):
            req=requests.head(str(site))
            status=req.status_code
            utils.log("status code: " + str(req.status_code))
            return status
            time.sleep(2)

        utils.log("Login...  (5 second cloudflare check)")
        try:
            self.driver.get(str(site) + "/Login")
            time.sleep(4)
            self.driver.implicitly_wait(30)
            self.driver.execute_script("window.stop()")
            time.sleep(1)
            try: # fill login form and send
                username=self.driver.find_element_by_id("username")
                password=self.driver.find_element_by_id("password")
                username.send_keys(user)
                password.send_keys(pw)
                password.send_keys(Keys.RETURN)
                time.sleep(2)
            except Exception as e:
                utils.log(e)
                utils.log("Error: login page not loaded (critical)")
                return False
        except Exception as e:
            utils.log(e)
            utils.log("Error: login failed")
            time.sleep(4)
            return False

        # print(self.driver.current_url)
        if str(self.driver.current_url).lower() == site + "/login" or str(self.driver.current_url).lower() == site + "/login": # confirm login success, return bool
            return False
        else:
            return True

    def get_episode_regex(self, keyword, episode, keyword2, string):
        episode = episode.replace('-5', '.5')
        string = string.replace('-5', '.5')
		#print(keyword,episode,keyword2,string)
        if '.5' in episode and '.5' in string:
            #print('decimal')
            regex = re.compile(keyword+'([0-9]*).5'+keyword2)
        else:
            regex = re.compile(keyword+'([0-9]*)'+keyword2)
        try:
            if float(episode) == float(regex.findall(string)[0]):
                if '.5' in episode and '.5' in string \
					or '.5' not in episode and '.5' not in string:
                    utils.log('Found ['+str(keyword)+str(episode)+str(keyword2)+'] in ['+str(string)+']')
                    return regex.findall(string)[0]
                #else:
                #    print('Not2',episode,regex.findall(string)[0])
            #else:
            #    print('Not',float(episode),float(regex.findall(string)[0]))
        except IndexError as e:
            return None
        except ValueError as e:
            return None
        except Exception as e:
            utils.log(e)
            sys.exit()
        return None

    def get_episode_page(self, episode, site): # parse video url, get episode page from list
		# TODO support for 0 episode
		# TODO test support for -5 episode http://kissanime.ru/Anime/Durarara episode 12.5
        soup=BeautifulSoup(self.rootPage, 'html.parser')
        init_episode=float(episode)
        episode=str(init_episode).replace(".0","")
        episode=str(episode).replace(".5","-5")
        for link in soup.findAll('a'): # uncensored
            currentlink=link.get('href')
            if currentlink is None:
                pass
            elif self.get_episode_regex('uncensored-episode-', episode, '', currentlink.lower()) \
				or self.get_episode_regex('uncen-episode-', episode, '', currentlink.lower()) \
				or self.get_episode_regex('episode-', episode, '-uncensored?', currentlink.lower()) \
				or self.get_episode_regex('episode-', episode, '-uncen?', currentlink.lower()) \
				or self.get_episode_regex('', episode, '?', currentlink.lower()):
                return [site + "" + currentlink.lower(), True]

        for link in soup.findAll('a'): # censored
            currentlink=link.get('href')
            if currentlink is None:
                pass
            elif self.get_episode_regex('episode-', episode, '', currentlink.lower()) \
				or self.get_episode_regex('ova-', episode, '?', currentlink.lower()) \
				or self.get_episode_regex('', episode, '?id=', currentlink.lower()):
                return [site + "" + currentlink.lower(), False]

		# TODO revise to work with new logic
        for link in soup.findAll('a'): # experimental
            currentlink=link.get('href')
            if(currentlink is None):
                pass
            else:
                if("episode-" in link.get('href').lower()):
                    currentlinkx=currentlink.lower()
                    episodex=0
                    if ("/anime/" in currentlinkx):
                        currentlinkx=currentlinkx.replace("/anime/", "")
                        animetitle=currentlinkx.split("/", 1)
                        for item in animetitle: # get last item
                            episodexx=item
                        if animetitle[0] + "-" in episodexx:
                            episodex=episodexx.replace(
                                animetitle[0] + "-", "")
                            # print("found [" + episodex + "]")
                            episodex=episodex.split("-")[0]
                    try:
                        if float(episodex) == float(episode) and float(episode) != 0:
                            return [site + "" + currentlink.lower(), False]
                        else:
                            pass
                    except ValueError:
                        pass
                    except Exception as e:
                        utils.log(e)
                        sys.exit()
        return ["", False]

    def get_video_src(self, episode_page, resolution): # parse url, return video url
        x=True
        while x:
            try:
                page=self.driver.get(episode_page)
                # print(page.text)
                url=self.driver.current_url
                if "Special/AreYouHuman?" in str(url):
                    utils.log("Captcha " + str(self.driver.current_url))
                    # webbrowser.open(self.driver.current_url)
                    while("Special/AreYouHuman?" in str(self.driver.current_url)):
                        time.sleep(1)
                    episode=episode - 1
                else:
                    x=False
            except Exception as e:
                utils.log(e)
                utils.log("Timeout [" + str(episode_page) + "] Retrying...")
                time.sleep(5)
        # print(page.url)
        currentpage=self.driver.page_source
        soup=BeautifulSoup(currentpage, 'html.parser')

        time.sleep(1) # delay for page render

        try:
            resolution=int(resolution)
        except Exception as e:
            utils.log(e)
            utils.log("Resolution error " + str(resolution))
            sys.exit()

        if(resolution >= 1080 or resolution == 0):
            teneighty=pattern=re.compile(r'x1080.mp4')
            for link in soup.findAll('a', text=teneighty):
                return [link.get('href'), ".mp4", "1080p"]
        if(resolution >= 720 or resolution == 0):
            seventwenty=pattern=re.compile(r'x720.mp4')
            for link in soup.findAll('a', text=seventwenty):
                return [link.get('href'), ".mp4", "720p"]
        if(resolution >= 480 or resolution == 0):
            foureighty=pattern=re.compile(r'x480.mp4')
            for link in soup.findAll('a', text=foureighty):
                return [link.get('href'), ".mp4", "480p"]
        if(resolution >= 360 or resolution == 0):
            threesixty=pattern=re.compile(r'x360.mp4')
            for link in soup.findAll('a', text=threesixty):
                return [link.get('href'), ".mp4", "360p"]
        if(resolution >= 0): # fallback
            finalcheck=pattern=re.compile(r'.mp4')
            for link in soup.findAll('a', text=finalcheck):
                resolutionr=str(link).rsplit('.mp4')[0][-3:]
                if(int(resolutionr) and int(resolutionr) >= 360 and int(resolutionr) <= 1080):
                    return [link.get('href'), ".mp4", resolutionr + "p"]

        for link in soup.find_all('a', string="CLICK HERE TO DOWNLOAD"): # openload (experimental)
            utils.log("openload not supported yet")

        return ["false", "", ""]

    def frange(self, start, stop, step):
        try:
            i=start
            while i < stop:
                yield i
                i += step
        except Exception as e:
            utils.log(e)
            utils.log("frange error")

    def zpad(self, val, n):
        try:
            bits=val.split('.')
            return "%s.%s" % (bits[0].zfill(n), bits[1])
        except Exception as e:
            utils.log(e)
            utils.log("zpad error")

    def download(self, p):
        global count
        global prefix
        global downloading
        global episode_list
        global complete_dir
        global download_threads
        file_list=[]
        episode_list=[]
        ecount=0
        downloading=0
        if(int(p[5]) > 0):
            epcount=int(p[5]) - 1 # temp folder
        else:
            epcount=0

        if(downloading == 0):
            downloading=1
            for i in range(int(download_threads)): # start downloader, wait for files
                params=""
                t=KissDownloader(params, queue)
                t.setDaemon(True)
                t.start()

        for infile in glob.glob(p[7] + "/*.mp4"):
            infile=infile.replace(p[7], "")
            infile=re.sub(r'.*_-_', '', infile)
            infile=infile[:3]
            if(infile.find('-')):
                infile=str(infile).replace("-","")
                if(infile[-1:] == "."):
                    infile=infile.replace(".","")
                file_list.append(float(infile))
                file_list.append(float(infile)+1)
            elif(int(infile)):
                file_list.append(int(infile))
        if file_list:
            if(int(max(file_list))):
                if(len(file_list) < int(max(file_list)) and p[5] == 0):
                    utils.log("Downloaded episode " + str(max(file_list)) + ", filecount " + str(len(file_list)))
                    utils.log("Recheck from 0")
                    epcount=p[5]
                else:
                    epcount=int(max(file_list)) + 1

        if(p[4] and int(p[9]) == 0):
            maxretrieve=int(p[4]) + 1
        elif(int(p[9]) > 0):
            maxretrieve=int(p[9]) + 1

        if(int(ecount) < maxretrieve):
            extension=webdriver.ChromeOptions()
            try:
                extension.add_extension(dir_path + "/extension/ublock_origin.crx")
            except OSError as e:
                utils.log(e)
                utils.log("Error loading extension")
            extension.add_argument('--dns-prefetch-disable')
            #prefs = {"profile.managed_default_content_settings.images":2}
            #extension.add_experimental_option("prefs",prefs)
            self.driver=webdriver.Chrome(chrome_options=extension)
            self.driver.set_page_load_timeout(50)
            l = True
            while l:
                l=self.login(p[0], p[1], p[8])
                if not l:
                    utils.log("Login failed... try again")
                else:
                    l = False
        k=True
        while k:
            try:
                self.driver.get(p[3])
                time.sleep(3)
                self.rootPage=self.driver.page_source
                k=False
            except Exception as e:
                utils.log(e)
                time.sleep(2)
                utils.log("Error loading page")

        if (int(ecount) < (int(p[4]) + 1)):
            utils.log("Retrieve from " + str(epcount) + " of " + str(p[4]))

            for e in self.frange(float(epcount), int(maxretrieve), 0.5):
                if(int(ecount) < int(download_threads) * 3 and int(ecount) < int(maxretrieve)):
                    time.sleep(2)
                    page=self.get_episode_page(e, p[8])
                    if page[0] == "":
                        utils.log('Reading page episodes...')
                        pass
                    else:
                        video=self.get_video_src(page[0], p[10])
                        KA=""
                        try:
                            if prefix:
                                prefix2=p[6] + prefix
                                KA="_KA"
                        except:
                            prefix2=""
                        if (video[0] != 'false'):
                            if e % 1 == 0:
                                e=self.zpad(str(e), 3).replace(".0", "")

                            try: # hyphen seporator
                                varxx=page[0].split('?id=', 1)[0]
                                number7=sum(c.isdigit() for c in varxx[-7:])
                                if(number7 == 6 and "-" in varxx[-7:]):
                                    e=str(varxx[-7:]).zfill(2)
                                number5=sum(c.isdigit() for c in varxx[-5:])
                                if(number5 == 4 and "-" in varxx[-5:]):
                                    e=str(varxx[-5:]).zfill(2)
                            except Exception as e:
                                utils.log(e)
                                utils.log("Error: hyphen")

                            if page[1]: # uncensored
                                filename=prefix2 + p[2] + "_-_" + str(e) + "_" + video[2] + "_BD" + KA + video[1]
                            else:
                                filename=prefix2 + p[2] + "_-_" + str(e) + "_" + video[2] + KA + video[1]
                            episode_list.append((video[0], filename, p[7], e))
                            ecount=ecount + 1
                            utils.log("Resolved [" + str(filename) + "]")

                            queue.put(video[0]) # append video url to queue
                        else:
                            utils.log("Retrieve failed [" + str(e) + "]")
                else:
                    utils.log("Queue limit reached (" + str(int(download_threads) * 3) + ")")
                    break
            else:
                utils.log("Retrieved episode limit (" + str(int(maxretrieve) - 1) + ")")

        self.driver.close()

        # DownloadGUI Initiate

        try:
            last_count=9001
            while(count > 0):
                time.sleep(5) # allow downloads to start

                t=threading.Thread(target=KissDownloader.download_message())
                t.daemon=True
                t.start()

                if(int(count) != int(last_count) and int(count) < int(download_threads)):
                    if(int(last_count) > 9000):
                        last_count=count
                    else:
                        utils.log("> " + str(count) + " remain")
                        last_count=count
        except KeyboardInterrupt:
            utils.log("keyboard interrupt") # TODO proper thread exit logic
            sys.exit()
        except Exception as e:
            utils.log(e)

        if(episode_list):
            try:
                os.remove(dir_path + "/resolved.csv.trash")
            except FileNotFoundError as e:
                pass
            os.rename(dir_path + "/temp/resolved" + randnum + ".csv", dir_path + "/resolved.csv.trash")
            KissDownloader.init()
        else:
            utils.log("Download finished!")
            finaldestination=p[7]
            utils.log(finaldestination)
            if(complete_dir): # move *.mp4 to complete_dir
                file_count=[]
                for infile in glob.glob(p[7] + "/*.mp4"):
                    file_count.append(infile)
                utils.log(str(len(file_count)) + "/" + str(p[4]))
                if(len(file_count) >= int(p[4])-1):
                    for files in os.listdir(finaldestination):
                        if files.endswith('.mp4'):
                            shutil.move(os.path.join(finaldestination, files), os.path.join(complete_dir, files))
                    try:
                        os.rmdir(finaldestination + "/temp")
                        os.rmdir(finaldestination)
                    except Exception as e:
                        utils.log(e)
                        utils.log("Folder delete failed")
                else:
                    if(len(file_count) <= 1):
                        utils.log("Download failed!")
                        os.rmdir(finaldestination + "/temp")
                        os.rmdir(finaldestination)
                    else:
                        utils.log("Invalid filecount!")

            os.remove(dir_path + "/resolved.csv")
            os.rename(dir_path + "/temp/resolved" + randnum + ".csv", dir_path + "/resolved.csv")

            KissDownloader.init()

    def read_config():
        global destination_folder

        if os.path.exists(dir_path + "/temp"):
            shutil.rmtree(dir_path + "/temp")
        os.mkdir(dir_path + "/temp")

        resolved = Path(dir_path + "/resolved.csv")
        if not resolved.is_file():
            utils.log('Error: no series queued to download!')
            sys.exit()

        reader=csv.reader(open(dir_path + "/resolved.csv", "r"), delimiter=",")
        newfile=open(dir_path + "/temp/resolved" + randnum + ".csv", "a")
        writer=csv.writer(newfile)
        br=0
        for row in reader:
            try:
                if row:
                    if(br == 0):
                        if row[0]:
                            title=row[0]
                        else:
                            utils.log("Error reading title")
                            sys.exit()
                        if row[1]:
                            url=row[1]
                        else:
                            utils.log("Error reading url")
                            sys.exit()
                        if row[2]:
                            episode_count=row[2]
                        else:
                            utils.log("Error reading episode_count")
                            sys.exit()
                        mal=row[3]
                        if(int(row[4]) > 0):
                            episode_min=int(row[4])+1
                            utils.log("Minimum episode set to " + str(int(episode_min)-1))
                        else:
                            episode_min=int(0)
                        if(int(row[5])):
                            episode_max=row[5]
                            utils.log("Maximum episode set to " + str(episode_max))
                        else:
                            episode_max=int(0)
                        if(int(row[6]) >= 0 and int(row[6]) <= 1080):
                            if(int(row[6]) >= 360):
                                utils.log("Resolution limited to " + str(row[6]) + "p")
                            resolution=row[6]
                        else:
                            resolution=0
                        break
                    else:
                        writer.writerows([row])
            except IndexError as e:
                utils.log(e)
                utils.log("IndexError")
            except Exception as e:
                utils.log(e)
                utils.log("Exception reading resolved.csv")
        # writer.writerows([newrow])

        newfile.close()
        try:
            if not title:
                utils.log("Complete!")
                sys.exit()
        except:
            utils.log("Complete!")
            sys.exit()
        try:
            for k, v in {'&&': '', '&': '_and_', "'s": 's'}.items(): # replace
                title=title.replace(k, v)
            title=re.sub(r'[^a-zA-Z0-9\[\]]', '_', title) # alphanumeric only
            title=re.sub('_+', '_', title) # replace multiple _
            title=title.rstrip('_') # remove last underscore
        except Exception as e:
            utils.log(e)
            utils.log("Critical error renaming title")
            sys.exit()
        utils.log('Initiate... [' + str(title) + ']')

        if not destination_folder:
            destination_folder=str(dir_path)

        if not destination_folder.endswith('/'):
            destination=str(destination_folder) + "/" + title + "/"

        if not os.path.exists(destination_folder + "/" + title):
            os.mkdir(destination_folder + "/" + title)
        if not os.path.exists(destination_folder + "/" + title + "/temp"):
            os.mkdir(destination_folder + "/" + title + "/temp")

        website='{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))
        if website.endswith('/'):
            website=website[:-1]

        try:
            return website, username, userpassword, title, url, mal, episode_min, episode_count, destination_folder, episode_max, resolution
        except UnboundLocalError as e:
            utils.log(e)
            utils.log("Critical error reading resolved.csv in " + dir_path)
            sys.exit()
        except Exception as e:
            utils.log(e)
            sys.exit()

    def run_download(self):
        if self[8] == "":
            if not os.path.exists(dir_path + "/downloads"):
                os.mkdir(dir_path + "/downloads")
            destination=dir_path + "/downloads"
        else:
            destination_folderx=self[8].replace("\\", "/")
            destination=str(destination_folderx) + str(self[3]) + "/"
            if not destination_folderx.endswith('/'):
                destination=str(destination_folderx) + "/" + str(self[3]) + "/"
        params=[self[1], self[2], self[3], self[4], self[5], self[6], self[7], destination, self[0], self[9], self[10]]
        # print(params)
        KissDownloader(params, queue)

    def init():
        try: # check network connection
            socket.create_connection(("www.google.com", 80))
        except OSError:
            utils.log("Unable to connect to network :(")
            sys.exit()

        # 0 website, 1 username,2 userpassword, 3 title, 4 url, 5 mal, 6 episode_min, 7 episode_count, 8 destination, 9 episode_max, 10 resolution
        website, username, userpassword, title, url, mal, episode_min, episode_count, destination_folder, episode_max, resolution=KissDownloader.read_config()
        KissDownloader.run_download([website, username, userpassword, title, url, mal, episode_min, episode_count, destination_folder, episode_max, resolution])
        episodes_list=[]
        for tup in episodes_list:
            url=tup[0]
            filename=tup[1]
            destination=tup[2]

if __name__ == "__main__":
    KissDownloader
    KissDownloader.init()
