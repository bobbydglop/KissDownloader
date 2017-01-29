#!/usr/bin/env python
import urllib, scrapy, csv, re, shutil, cfscrape, requests, sys, os, time, pip, glob, shutil, webbrowser, random, threading, time, youtube_dl
from threading import Thread, Lock
from urllib.request import urlretrieve
from urllib.parse import urlparse
import urllib.request as urllib2
import queue as Queue
import tqdm as tqdm
from pathlib import Path
from bs4 import BeautifulSoup
from tempfile import NamedTemporaryFile
from random import randint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

# ----  CONFIG START ---- #

user_name = "" # required
user_password = "" # required
destination = "" # optional (defaults to /downloads folder)
complete_dir = "" # optional (move all downloaded mp4 to this location on download complete)
queue_limit = 35 # recommended 2-40 (limits url to retrieve before downloading; retrieved url expire)
download_threads = 6 # recommended 2+
retrieve_last = 0 # current_episode - retrieve_last to resolve files agian and redownload if failed
prefix = "" # filename prefix

# ----  CONFIG END   ---- #

# TODO Fix download bar (broken currently)

dir_path = os.path.dirname(os.path.realpath(__file__))
randnum = str(randint(1,100000))
queue = Queue.Queue()
start = time.time()
count = 0

class KissDownloader(threading.Thread):
    def __init__(self, params, queue):
        if(params):
            print("Load chrome...")
            extension = webdriver.ChromeOptions()
            extension.add_extension("./extension/ublock_origin.crx")
            extension.add_extension("./extension/image_block.crx")
            self.driver = webdriver.Chrome(chrome_options = extension)
            self.driver.set_page_load_timeout(20)

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
            else:
                try:
                    print("Initiate episode " + nestlist[0][3])
                    count = count + 1
                    urlretrieve(host, nestlist[0][2] + "temp/" + nestlist[0][1])
                    print("Completed episode " + nestlist[0][3])
                    downloaded = 1
                    count = count - 1
                except:
                    try:
                        print("Retry episode " + nestlist[0][3])
                        urlretrieve(host, nestlist[0][2] + "temp/" + nestlist[0][1])
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
        self.driver.get(str(site) + "/Login")
        time.sleep(5)
        self.driver.implicitly_wait(10)

        username = self.driver.find_element_by_id("username")
        password = self.driver.find_element_by_id("password")
        # type login info into fields
        username.send_keys(user)
        password.send_keys(pw)
        # send the filled out login form and wait
        password.send_keys(Keys.RETURN)
        time.sleep(5)

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
                elif "uncensored-episode-" + str(episode).zfill(3) + "?" in currentlink.lower() or "uncensored-episode-" + str(episode).zfill(2) + "?" in currentlink.lower() or "uncen-episode-" + str(episode).zfill(3) + "?" in currentlink.lower() or "uncen-episode-" + str(episode).zfill(2) + "?" in currentlink.lower() or "episode-" + str(episode).zfill(3) + "-uncensored?" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "-uncensored?" in currentlink.lower() or "episode-" + str(episode).zfill(3) + "-uncen?" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "-uncen?" in currentlink.lower():
                    return [site + "" + currentlink.lower(), True]
            # censored vvv
            for link in soup.findAll('a'):
                currentlink = link.get('href')
                if currentlink is None:
                    pass
                else:
                    if "episode-" + str(episode).zfill(3) + "?" in currentlink.lower() or "episode-" + str(episode).zfill(2) + "?" in currentlink.lower() or "episode-" + str(episode).zfill(1) + "?" in currentlink.lower():
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
                                if self.debug_mode:
                                    print("found [" + episodex + "]")
                                episodex = episodex.split("-")[0]
                        try:
                            if float(episodex) == float(episode):
                                return [site + "" + currentlink.lower(), False]
                            else:
                                pass
                        except ValueError:
                            pass
            return ["", False]

    def get_video_src(self, episode_page): # parse the video source link, retrieve highest available quality
        x = True
        while x:
            try:
                page = self.driver.get(episode_page)
                #print(page.text)
                url = self.driver.current_url
                if "Special/AreYouHuman?" in str(url):
                    print("Captcha " + str(self.driver.current_url))
                    webbrowser.open(self.driver.current_url)
                    input("Input Enter to continue...")
                    episode = episode-1
                x = False
            except:
                print("loading " + episode_page + " timed out, retrying...")
                time.sleep(random.randint(5,10))
        #print(page.url)
        currentpage = self.driver.page_source
        soup = BeautifulSoup(currentpage, 'html.parser')

        #for link in soup.findAll('a', string="1920x1080.mp4"):
        #    return [link.get('href'), ".mp4"]

        for link in soup.findAll('a', string="1280x720.mp4"):
            return [link.get('href'), ".mp4", "720p"]
        for link in soup.findAll('a', string="960x720.mp4"):
            return [link.get('href'), ".mp4", "720p"]
        for link in soup.findAll('a', string="854x480.mp4"):
            return [link.get('href'), ".mp4", "480p"]
        for link in soup.findAll('a', string="480x360.mp4"):
            return [link.get('href'), ".mp4", "480p"]
        for link in soup.findAll('a', string="640x360.mp4"):
            return [link.get('href'), ".mp4", "360p"]

        for link in soup.find_all('a', string="CLICK HERE TO DOWNLOAD"): # openload
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
        episode_list = []
        file_list = []
        global prefix
        global queue_limit
        ecount = 0
        if(int(p[5])>0):
            epcount = int(p[5])-1 # temp folder
        else:
            epcount = 0

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
        if(int(epcount) > int(retrieve_last)):
            epcount = (int(epcount) - int(retrieve_last))

        try:
            l = self.login(p[0], p[1], p[8])
            while not l:
                print("Login failed, try again")
                l = self.login(p[0], p[1], p[8])
        except:
            sys.exit("Error message")
        self.driver.get(p[3])
        time.sleep(3)
        self.rootPage = self.driver.page_source
        if (int(ecount) < (int(p[4]))):
            print("Retrieve from " + str(epcount))
            if(p[4] and int(p[9])==0):
                maxretrieve = int(p[4])+2
            elif(int(p[9])>0):
                maxretrieve = int(p[9])
            for e in self.frange(float(epcount), maxretrieve, 1):
                if(int(ecount) < int(queue_limit) and int(ecount) < maxretrieve):
                    time.sleep(1)
                    page = self.get_episode_page(e, p[8])
                    if page[0] == "":
                        pass
                    else:
                        video = self.get_video_src(page[0])
                        if prefix:
                            prefix2 = p[6] + prefix
                        else:
                            prefix2 = ""
                        if (video[0] != 'false'):
                            if e % 1 == 0:
                                print(e)
                                e = self.zpad(str(e), 3).replace(".0", "")
                            # check if hyphen seporator
                            varxx = page[0].split('?id=', 1)[0]
                            # 001-002
                            number7 = sum(c.isdigit() for c in varxx[-7:])
                            if(number7 == 6 and "-" in varxx[-7:]):
                                e = str("00" + varxx[-7:])
                            # 01-02
                            number5 = sum(c.isdigit() for c in varxx[-5:])
                            if(number5 == 4 and "-" in varxx[-5:]):
                                e = str("00" + varxx[-5:])
                            if page[1]:  # uncensored
                                filename = prefix2 + p[2] + "_-_" + e + "_" + video[2] +"_BD_KA" + video[1]
                            else:
                                filename = prefix2 + p[2] + "_-_" + e + "_" + video[2] + "_KA" + video[1]
                            episode_list.append((video[0], filename, p[7], e))
                            ecount = ecount + 1
                            print("Resolved [" + str(filename) + "]")
                        else:
                            print("Retrieve failed [" + str(e) + "]")
                else:
                    print("Queue limit reached ("+str(queue_limit)+")")
                    break
            else:
                print("Retrieved episode limit ("+str(maxretrieve)+")")


        self.driver.close()

        for i in range(download_threads):
          params=""
          t = KissDownloader(params, queue)
          t.setDaemon(True)
          t.start()

        for host in episode_list: # url from episode_list
          queue.put(host[0])
        queue.join()


        print("Start download")
        for tuple in episode_list:
            url = tuple[0]
            filename = tuple[1]
            destinationf = tuple[2]
            episode = tuple[3]
            my_file = Path(destinationf + filename)

        if(episode_list):
            os.rename( dir_path + "/temp/resolved"+randnum+".csv", dir_path + "/resolved.csv.trash")
            KissDownloader.init()
        else:
            print("Download complete!")
            if(complete_dir): # move *.mp4 to complete_dir
                try:
                    print("Move *.mp4 to " + complete_dir)
                    destinationf = p[7]
                    if destinationf.endswith('/'):
                        destinationf = destinationf[:-1]
                    source = os.listdir(destinationf)
                    for files in source:
                        if files.endswith('.mp4'):
                            shutil.move(os.path.join(destinationf,files), os.path.join(complete_dir,files))
                except:
                    print("Exception failed to move mp4")

            os.remove( dir_path + "/resolved.csv")
            os.rename( dir_path + "/temp/resolved"+randnum+".csv", dir_path + "/resolved.csv")
            KissDownloader.init()

    def read_config():

        if os.path.exists(dir_path + "/temp"):
            shutil.rmtree(dir_path + "/temp")
        os.mkdir(dir_path + "/temp")

        try:
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
                            episode_max = row[5]
                            br = 1
                            newrow=[row[0],row[1],row[2],row[3],row[4],row[5],1]
                            pass
                        else:
                            writer.writerows([row])
                except IndexError:
                    print("EndIndex")
                except Exception:
                    print("Exception")
            '''
            writer.writerows([newrow])
            '''

            newfile.close()
        except:
            sys.exit("Critical error: Unable to read spreadsheet")
        try:
            mapping = {'&&':'', '&':'_and_', "'s":'s', '__':'_', '__':'_', '__':'_', '___':'_' }
            for k, v in mapping.items():
                title = title.replace(k, v)
            title = re.sub(r'[^a-zA-Z0-9\[\]]','_', title)
            title = title.rstrip('_')
            title = title.rstrip('_')
        except:
            sys.exit("Critical error renaming title")
        print('Initiate... [' + str(title) + ']')

        if not os.path.exists(destination + "/" + title):
            os.mkdir(destination + "/" + title)
        if not os.path.exists(destination + "/" + title + "/temp"):
            os.mkdir(destination + "/" + title + "/temp")

        website = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))
        if website.endswith('/'):
            website = website[:-1]

        return website,user_name,user_password,title,url,mal,episode_min,episode_count,destination,episode_max

    def run_download(self):
        if self[8] == "":
            if not os.path.exists(dir_path + "/downloads"):
                os.mkdir(dir_path + "/downloads")
            destination = dir_path + "/downloads"
        else:
            destination_folder = self[8].replace("\\", "/")
            if destination_folder.endswith('/'):
                destination = str(destination_folder) + str(self[3]) + "/"
            else:
                destination = str(destination_folder) + "/" + str(self[3]) + "/"
        params = [self[1], self[2], self[3], self[4], self[5], self[6], self[7], destination, self[0], self[9]]
        #print(params)
        KissDownloader(params, queue)

    def init():
        # 0 website, 1 user_name,2 user_password, 3 title, 4 url, 5 mal, 6 episode_min, 7 episode_count, 8 destination, 9 episode_max
        website,user_name,user_password,title,url,mal,episode_min,episode_count,destination,episode_max = KissDownloader.read_config()
        KissDownloader.run_download([website,user_name,user_password,title,url,mal,episode_min,episode_count,destination,episode_max])
        episodes_list = []
        for tup in episodes_list:
            url = tup[0]
            filename = tup[1]
            destination = tup[2]

if __name__ == "__main__":
    KissDownloader
    KissDownloader.init()
