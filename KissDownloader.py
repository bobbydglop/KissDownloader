#!/usr/bin/env python
import urllib, csv, re, socket, requests, sys, os, time, glob, shutil, random, threading, youtube_dl
from settings import *
import urllib.request as urllib2
import queue as Queue
import tqdm as tqdm
from threading import Thread, Lock
from urllib.request import urlretrieve
from urllib.parse import urlparse
from pathlib import Path
from bs4 import BeautifulSoup
from random import randint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

# TODO Fix GUI not closing when click start download
# TODO Fix download bar (previously working)
# TODO Add support for movies/episodes not following the standard naming schema
# TODO Retrieve until queue_limit is reached, across multiple series. Require rework to handle managing multiple series at once.

try:
    if not str(username) and str(userpassword):
        sys.exit("Undefined username/userpassword under CONFIG")
except:
    sys.exit("Error reading CONFIG for KissDownloader.py")

dir_path = os.path.dirname(os.path.realpath(__file__))
randnum = str(randint(1,100000))
queue = Queue.Queue()
start = time.time()
count = 0
downloading = 0
complete_dir = "" # Developer
prefix = "" # Developer

class KissDownloader(threading.Thread):
    def __init__(self, params, queue):
        if(params):
            self.rootPage = ""
            self.file_extension = ""
            self.download(params)
        else:
            threading.Thread.__init__(self)
            self.queue = queue

    def run(self):
        global count
        downloaded = 0
        while True:
            host = self.queue.get()
            nestlist = [x for x in episode_list if host in x[0]]

            try:
                if(os.path.isfile(nestlist[0][2] + nestlist[0][1])):
                    print("File exists " + nestlist[0][1] + "...")
                elif not nestlist:
                    print("Unable to read download")
                elif not host:
                    print("Unable to read download host")
                else:
                    try:
                        print("Download " + nestlist[0][3] + "...")
                        count = count + 1
                        urlretrieve(str(host), str(nestlist[0][2] + "temp/" + nestlist[0][1]))
                        print("Completed " + nestlist[0][3] + "!")
                        downloaded = 1
                        count = count - 1
                    except:
                        try:
                            print("Retry episode " + nestlist[0][3])
                            urlretrieve(str(host), str(nestlist[0][2] + "temp/" + nestlist[0][1]))
                            print("Completed episode " + nestlist[0][3])
                            downloaded = 1
                            count = count - 1
                        except:
                            print("Episode " + nestlist[0][3] + " failed")
                            count = count - 1
            except:
                try:
                    print("Error downloading episode " + nestlist[0][3])
                except:
                    print("Spreadsheet error")
            try:
                if(downloaded == 1):
                    shutil.move(nestlist[0][2] + "temp/" + nestlist[0][1], nestlist[0][2] + nestlist[0][1])
            except:
                print("Failed moving " + str(nestlist[0][2] + "temp/" + nestlist[0][1]) + " to " + str(nestlist[0][2] + nestlist[0][1]))

            #total = tqdm.tqdm(count)
            #total.update(1)
            self.queue.task_done()

    def login(self, user, pw, site):
        status = ""
        while (status == 503 and status != ""):
            req = requests.head(str(site))
            status = req.status_code
            print("status code: " + str(req.status_code))
            return status
            time.sleep(random.randint(1,2))

        print("Login...  (5 second cloudflare check)")
        try:
            self.driver.get(str(site) + "/Login")
            time.sleep(10)
            self.driver.implicitly_wait(30)
            self.driver.execute_script("window.stop()")
        except:
            print("Critical error: login failed")
            time.sleep(4)
            return False
        try:
            time.sleep(3)
            username = self.driver.find_element_by_id("username")
            password = self.driver.find_element_by_id("password")
            username.send_keys(user)
            password.send_keys(pw)
            # send the filled out login form and wait
            password.send_keys(Keys.RETURN)
            time.sleep(4)
        except:
            print("Login credential failed:")
            print(str(user) + " - " + str(pw))
            time.sleep(4)
            return False
        #print(self.driver.current_url)

        if str(self.driver.current_url).lower() == site + "/login" or str(self.driver.current_url).lower() == site + "/login": # confirm login success, return bool
            return False
        else:
            return True

    def get_episode_page(self, episode, site): # parse video url, get episode page from list
        soup = BeautifulSoup(self.rootPage, 'html.parser')
        if episode % 1 == 0:
            ###for non special episodes
            episode = int(episode)
            # uncensored vvv
            for link in soup.findAll('a'):
                currentlink = link.get('href')
                if currentlink is None:
                    pass
                elif "uncensored-episode-" + str(episode).zfill(3) + "?" in currentlink.lower() or "uncensored-episode-" + str(episode).zfill(2) + "?" in currentlink.lower() or "uncen-episode-" + str(episode).zfill(3) + "?" in currentlink.lower() or "uncen-episode-" + str(episode).zfill(2) + "?" in currentlink.lower() or "episode-" + str(episode).zfill(3) + "-uncensored?" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "-uncensored?" in currentlink.lower() or "episode-" + str(episode).zfill(3) + "-uncen?" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "-uncen?" in currentlink.lower()  or "episode-" + str(episode).zfill(1) + "-uncen?" in currentlink.lower():
                    return [site + "" + currentlink.lower(), True]
            # censored vvv
            for link in soup.findAll('a'):
                currentlink = link.get('href')
                if currentlink is None:
                    pass
                else:
                    if "episode-" + str(episode).zfill(3) + "?" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "?" in currentlink.lower():
                        return [site + "" + currentlink.lower(), False]
            # weird urls
            for link in soup.findAll('a'):
                currentlink = link.get('href')
                if currentlink is None:
                    pass
                elif "episode-" + str(episode).zfill(3) + "-" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "-" in currentlink.lower():
                    return [site + "" + currentlink.lower(), False]
            # experimental urls
            for link in soup.findAll('a'):
                currentlink = link.get('href')
                if(currentlink is None):
                    pass
                else:
                    if("episode-" in link.get('href').lower()):
                        currentlinkx = currentlink.lower()
                        episodex = 0
                        if ("/anime/" in currentlinkx):
                            currentlinkx = currentlinkx.replace("/anime/", "")
                            animetitle = currentlinkx.split("/", 1)
                            for item in animetitle:  # get last item
                                episodexx = item
                            if animetitle[0] + "-" in episodexx:
                                episodex = episodexx.replace(animetitle[0] + "-", "")
                                #print("found [" + episodex + "]")
                                episodex = episodex.split("-")[0]
                        try:
                            if float(episodex) == float(episode) and float(episode) != 0:
                                return [site + "" + currentlink.lower(), False]
                            else:
                                pass
                        except ValueError:
                            pass
            return ["", False]

    def get_video_src(self, episode_page, resolution): # parse the video source link, retrieve highest available quality
        x = True
        while x:
            try:
                page = self.driver.get(episode_page)
                #print(page.text)
                url = self.driver.current_url
                if "Special/AreYouHuman?" in str(url):
                    print("Captcha " + str(self.driver.current_url))
                    #webbrowser.open(self.driver.current_url)
                    while("Special/AreYouHuman?" in str(self.driver.current_url)):
                        time.sleep(1)
                    episode = episode-1
                else:
                    x = False
            except:
                print("Timeout [" + str(episode_page) + "] Retrying...")
                time.sleep(random.randint(5,10))
        #print(page.url)
        currentpage = self.driver.page_source
        soup = BeautifulSoup(currentpage, 'html.parser')

        time.sleep(1) # wait for render

        try:
            resolution = int(resolution)
        except:
            sys.exit("Resolution error " + str(resolution))

        if(resolution >= 1080 or resolution == 0):
            teneighty = pattern = re.compile(r'x1080.mp4')
            for link in soup.findAll('a', text=teneighty):
                return [link.get('href'), ".mp4", "1080p"]
        if(resolution >= 720 or resolution == 0):
            seventwenty = pattern = re.compile(r'x720.mp4')
            for link in soup.findAll('a', text=seventwenty):
                return [link.get('href'), ".mp4", "720p"]
        if(resolution >= 480 or resolution == 0):
            foureighty = pattern = re.compile(r'x480.mp4')
            for link in soup.findAll('a', text=foureighty):
                return [link.get('href'), ".mp4", "480p"]
        if(resolution >= 360 or resolution == 0):
            threesixty = pattern = re.compile(r'x360.mp4')
            for link in soup.findAll('a', text=threesixty):
                return [link.get('href'), ".mp4", "360p"]
        # fallback for other resolution
        if(resolution >= 0):
            finalcheck = pattern = re.compile(r'.mp4')
            for link in soup.findAll('a', text=finalcheck):
                resolutionr = str(link).rsplit('.mp4')[0][-3:]
                if(int(resolutionr) and int(resolutionr) >= 360 and int(resolutionr) <= 1080):
                    return [link.get('href'), ".mp4", resolutionr+"p"]

        # openload
        for link in soup.find_all('a', string="CLICK HERE TO DOWNLOAD"):
            ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
            with ydl:
                result = ydl.extract_info(link.get('href'),download=False) # extract info
                if 'entries' in result:
                    video = result['entries'][0] # playlist video
                else:
                    video = result # single video
                return [video['url'], "."+video['ext'], "720p"]

        return ["false", "", ""]

    def frange(self, start, stop, step):
        i = start
        while i < stop:
            yield i
            i += step

    def zpad(self, val, n):
        try:
            bits = val.split('.')
            return "%s.%s" % (bits[0].zfill(n), bits[1])
        except:
            print("calc error")

    def download(self, p):
        global episode_list
        global downloading
        episode_list = []
        file_list = []
        global prefix
        global download_threads
        ecount = 0
        if(int(p[5])>0):
            epcount = int(p[5])-1 # temp folder
        else:
            epcount = 0

        if(downloading == 0):
            for i in range(int(download_threads)): # start downloader, wait for files
                downloading = 1
                params=""
                t = KissDownloader(params, queue)
                t.setDaemon(True)
                t.start()

        for infile in glob.glob(p[7]+"/*.mp4"):
            infile = infile.replace(p[7],"")
            infile = re.sub(r'.*_-_', '', infile)
            infile = infile[:3]
            if(int(infile)):
                file_list.append(int(infile))
        if file_list:
            if(int(max(file_list))):
                if(len(file_list) < int(max(file_list)) and p[5] == 0):
                    print("Downloaded episode " + str(max(file_list)) + ", filecount " + str(len(file_list)))
                    print("Recheck from 0")
                    epcount = p[5]
                else:
                    epcount = int(max(file_list))+1

        if(p[4] and int(p[9])==0):
            maxretrieve = int(p[4])+1 # +1 to handle 0 episodes
        elif(int(p[9])>0):
            maxretrieve = int(p[9])

        if(int(ecount) < maxretrieve):
            extension = webdriver.ChromeOptions()
            extension.add_argument('--dns-prefetch-disable')
            extension.add_extension(dir_path+"/extension/ublock_origin.crx")
            extension.add_extension(dir_path+"/extension/image_block.crx")
            try:
                self.driver = webdriver.Chrome(chrome_options = extension)
                self.driver.set_page_load_timeout(50)
            except:
                sys.exit("Chrome failed to load")
            try:
                l = self.login(p[0], p[1], p[8])
                while not l:
                    print("Login failed, try again")
                    l = self.login(p[0], p[1], p[8])
            except:
                sys.exit("Login failed")
        k = True
        while k:
            try:
                self.driver.get(p[3])
                time.sleep(2)
                self.rootPage = self.driver.page_source
                k = False
            except:
                time.sleep(2)
                print("Error loading page")

        if (int(ecount) < (int(p[4])+1)):
            print("Retrieve from " + str(epcount) + " of " + str(p[4]))

            for e in self.frange(float(epcount), int(maxretrieve), 1):
                if(int(ecount) < int(download_threads)*3 and int(ecount) < int(maxretrieve)):
                    time.sleep(random.randint(2,4))
                    page = self.get_episode_page(e, p[8])
                    if page[0] == "":
                        pass
                    else:
                        video = self.get_video_src(page[0], p[10])
                        KA = ""
                        if prefix:
                            prefix2 = p[6] + prefix
                            KA = "_KA"
                        else:
                            prefix2 = ""
                        if (video[0] != 'false'):
                            if e % 1 == 0:
                                e = self.zpad(str(e), 3).replace(".0", "")
                            # check if hyphen seporator
                            varxx = page[0].split('?id=', 1)[0]
                            number7 = sum(c.isdigit() for c in varxx[-7:])
                            if(number7 == 6 and "-" in varxx[-7:]):
                                e = str("00" + varxx[-7:])
                            number5 = sum(c.isdigit() for c in varxx[-5:])
                            if(number5 == 4 and "-" in varxx[-5:]):
                                e = str("00" + varxx[-5:])
                            if page[1]:  # uncensored
                                filename = prefix2 + p[2] + "_-_" + e + "_" + video[2] +"_BD" + KA + video[1]
                            else:
                                filename = prefix2 + p[2] + "_-_" + e + "_" + video[2] + KA + video[1]
                            episode_list.append((video[0], filename, p[7], e))
                            ecount = ecount + 1
                            print("Resolved [" + str(filename) + "]")

                            queue.put(video[0]) # add video url to download queue
                        else:
                            print("Retrieve failed [" + str(e) + "]")
                else:
                    print("Queue limit reached ("+str(int(download_threads)*3)+")")
                    break
            else:
                print("Retrieved episode limit ("+str(int(maxretrieve)-1)+")")

        self.driver.close()

        global count
        last_count = 9001
        while(count > 0):
            time.sleep(1)
            if(int(count) != int(last_count) and int(count) < int(download_threads)):
                if(int(last_count) > 9000):
                    last_count = count
                else:
                    print("> " + str(count) + " remain")
                    last_count = count
        #queue.join() # wait for queue to complete

        if(episode_list):
            os.rename( dir_path + "/temp/resolved"+randnum+".csv", dir_path + "/resolved.csv.trash")
            KissDownloader.init()
        else:
            print("Download finished!")
            if(complete_dir): # move *.mp4 to complete_dir
                file_count = []
                for infile in glob.glob(p[7]+"/*.mp4"):
                    file_count.append(infile)
                print(str(len(file_count)) + "/" + str(p[4]))
                if(len(file_count) >= int(p[4])):
                    try:
                        finaldestination = destination + "/" + p[2]
                        for files in os.listdir(finaldestination):
                            if files.endswith('.mp4'):
                                shutil.move(os.path.join(finaldestination,files), os.path.join(complete_dir,files))
                        try:
                            os.rmdir(finaldestination + "/temp")
                            os.rmdir(finaldestination)
                        except:
                            print("Folder delete failed")
                    except:
                        print("Files move failed")

                else:
                    print("Invalid filecount!")

            os.remove( dir_path + "/resolved.csv")
            os.rename( dir_path + "/temp/resolved"+randnum+".csv", dir_path + "/resolved.csv")
            KissDownloader.init()

    def read_config():
        if os.path.exists(dir_path + "/temp"):
            shutil.rmtree(dir_path + "/temp")
        os.mkdir(dir_path + "/temp")

        reader = csv.reader(open( dir_path + "/resolved.csv","r"),delimiter=",")
        newfile = open( dir_path + "/temp/resolved"+randnum+".csv", "a")
        writer = csv.writer(newfile)
        br = 0
        for row in reader:
            try:
                if row:
                    #print(row)
                    if(br==0):
                        title = row[0]
                        url = row[1]
                        episode_count = row[2]
                        mal = row[3]
                        episode_min = row[4]
                        if(int(row[4])):
                            print("Minimum episode set to " + str(row[5]))
                        episode_max = row[5]
                        if(int(row[5])):
                            print("Maximum episode set to " + str(row[5]))
                        if(int(row[6]) >= 0 and int(row[6]) <= 1080):
                            if(int(row[6]) >= 360):
                                print("Resolution limited to " + str(row[6]) + "p")
                            resolution = row[6]
                        else:
                            sys.exit("Column 6 resolution out of bounds ['360','480','720','1080']")
                        br = 1
                        newrow=[row[0],row[1],row[2],row[3],row[4],row[5],row[6],1]
                        pass
                    else:
                        writer.writerows([row])
            except IndexError:
                print("EndIndex")
            except Exception:
                print("Exception")
        #writer.writerows([newrow])

        newfile.close()
        try:
            for k, v in {'&&':'', '&':'_and_', "'s":'s'}.items(): # replace
                title = title.replace(k, v)
            title = re.sub(r'[^a-zA-Z0-9\[\]]','_', title) # alphanumeric only
            title = re.sub('_+', '_', title) # replace multiple _
            title = title.rstrip('_') # remove last underscore
        except:
            sys.exit("Critical error renaming title")
        print('Initiate... [' + str(title) + ']')

        if not os.path.exists(destination_folder + "/" + title):
            os.mkdir(destination_folder + "/" + title)
        if not os.path.exists(destination_folder + "/" + title + "/temp"):
            os.mkdir(destination_folder + "/" + title + "/temp")

        website = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))
        if website.endswith('/'):
            website = website[:-1]

        return website,username,userpassword,title,url,mal,episode_min,episode_count,destination_folder,episode_max,resolution

    def run_download(self):
        if self[8] == "":
            if not os.path.exists(dir_path + "/downloads"):
                os.mkdir(dir_path + "/downloads")
            destination = dir_path + "/downloads"
        else:
            destination_folderx = self[8].replace("\\", "/")
            destination = str(destination_folderx) + str(self[3]) + "/"
            if not destination_folderx.endswith('/'):
                destination = str(destination_folderx) + "/" + str(self[3]) + "/"
        params = [self[1], self[2], self[3], self[4], self[5], self[6], self[7], destination, self[0], self[9], self[10]]
        #print(params)
        KissDownloader(params, queue)

    def init():

        try: # check network connection
            socket.create_connection(("www.google.com", 80))
        except OSError:
            sys.exit("Unable to connect to network :(")

        # 0 website, 1 username,2 userpassword, 3 title, 4 url, 5 mal, 6 episode_min, 7 episode_count, 8 destination, 9 episode_max, 10 resolution
        website,username,userpassword,title,url,mal,episode_min,episode_count,destination_folder,episode_max, resolution = KissDownloader.read_config()
        KissDownloader.run_download([website,username,userpassword,title,url,mal,episode_min,episode_count,destination_folder,episode_max,resolution])
        episodes_list = []
        for tup in episodes_list:
            url = tup[0]
            filename = tup[1]
            destination = tup[2]

if __name__ == "__main__":
    KissDownloader
    KissDownloader.init()
